"""
Analyze train/val compression gap: find phrase candidates and missed words.
Focus on worst-compressing train categories: journalism, instructional, creative, casual, academic.
"""

import json
import re
import sys
from pathlib import Path
from collections import Counter

# Load corpus
corpus_dir = Path(__file__).parent / "corpus"
with open(corpus_dir / "train.json") as f:
    train_samples = json.load(f)
with open(corpus_dir / "val.json") as f:
    val_samples = json.load(f)

# Load config
sys.path.insert(0, str(Path(__file__).parent))
import config

# ═══════════════════════════════════════════════════════════
# PART 1: Extract phrases and find candidates
# ═══════════════════════════════════════════════════════════

def extract_ngrams(text, min_n=2, max_n=5):
    """Extract n-grams (2 to 5 words) from text, case-insensitive."""
    words = re.findall(r"[a-z']+", text.lower())
    ngrams = Counter()
    for n in range(min_n, max_n + 1):
        for i in range(len(words) - n + 1):
            phrase = " ".join(words[i:i+n])
            ngrams[phrase] += 1
    return ngrams

# Build phrase counters for train and val
print("Extracting n-grams from train corpus...")
train_phrases = Counter()
train_phrases_by_cat = {}
for sample in train_samples:
    cat = sample["category"]
    ngrams = extract_ngrams(sample["text"])
    train_phrases += ngrams
    if cat not in train_phrases_by_cat:
        train_phrases_by_cat[cat] = Counter()
    train_phrases_by_cat[cat] += ngrams

print("Extracting n-grams from val corpus...")
val_phrases = Counter()
for sample in val_samples:
    ngrams = extract_ngrams(sample["text"])
    val_phrases += ngrams

# Get existing phrases (case-insensitive)
existing_phrases = {p.lower() for p in config.PHRASE_CODEBOOK.keys()}

# Find candidates: 2+ in train, 1+ in val, not already in codebook
print("\nFinding phrase candidates...")
candidates = []
for phrase, train_count in train_phrases.items():
    if train_count < 2:
        continue
    val_count = val_phrases.get(phrase, 0)
    if val_count < 1:
        continue
    if phrase in existing_phrases:
        continue

    phrase_bytes = len(phrase.encode("utf-8"))
    total_count = train_count + val_count
    # Symbol code is typically 2 bytes (UTF-8 encoded)
    savings = total_count * (phrase_bytes - 2)

    if savings <= 0:
        continue

    # Check which worst-performing categories this phrase appears in
    worst_cats = ["journalism", "instructional", "creative", "casual", "academic"]
    in_worst = []
    for cat in worst_cats:
        if cat in train_phrases_by_cat and phrase in train_phrases_by_cat[cat]:
            in_worst.append(cat)

    candidates.append({
        "phrase": phrase,
        "train_count": train_count,
        "val_count": val_count,
        "total_count": total_count,
        "phrase_bytes": phrase_bytes,
        "savings": savings,
        "in_worst_cats": in_worst,
    })

# Sort by savings descending
candidates.sort(key=lambda x: (-x["savings"], -x["total_count"]))

print("\n" + "=" * 100)
print("TOP 100 PHRASE CANDIDATES (sorted by savings)")
print("=" * 100)
print(f"{'#':>3} {'Phrase':<40} {'Train':>5} {'Val':>3} {'Bytes':>5} {'Savings':>7} {'Worst Categories'}")
print("-" * 100)

for i, c in enumerate(candidates[:100]):
    cats = ",".join(c["in_worst_cats"][:3]) if c["in_worst_cats"] else "-"
    print(f"{i+1:>3} {c['phrase']:<40} {c['train_count']:>5} {c['val_count']:>3} "
          f"{c['phrase_bytes']:>5} {c['savings']:>7} {cats}")


# ═══════════════════════════════════════════════════════════
# PART 2: Find worst-compressing train samples and missed words
# ═══════════════════════════════════════════════════════════

print("\n\n" + "=" * 100)
print("ANALYZING WORST-COMPRESSING TRAIN SAMPLES")
print("=" * 100)

# Compress each train sample and find compression ratio
import importlib
importlib.reload(config)

VOWELS = set("aeiouAEIOU")

def compress_text(text, cfg):
    result = text
    phrases_sorted = sorted(cfg.PHRASE_CODEBOOK.keys(), key=len, reverse=True)
    for phrase in phrases_sorted:
        code = cfg.PHRASE_CODEBOOK[phrase]
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        result = pattern.sub(code, result)

    tokens = re.findall(r"[\w']+|[^\w\s]|\s+", result)
    rebuilt = []
    for token in tokens:
        if re.match(r"[\w']+", token):
            lower = token.lower()
            if lower in cfg.SYMBOL_MAP:
                rebuilt.append(cfg.SYMBOL_MAP[lower])
            else:
                rebuilt.append(token)
        else:
            rebuilt.append(token)
    result = "".join(rebuilt)

    tokens = re.findall(r"[\w']+|[^\w\s]|\s+", result)
    rebuilt = []
    for token in tokens:
        if re.match(r"[a-zA-Z]+$", token):
            lower = token.lower()
            if lower in cfg.PROTECTED_SHORTHAND:
                rebuilt.append(token)
                continue
            if lower in cfg.VOWEL_STRIP_EXCEPTIONS:
                rebuilt.append(token)
                continue
            if len(token) < cfg.MIN_VOWEL_STRIP_LENGTH:
                rebuilt.append(token)
                continue
            if len(token) == 1:
                rebuilt.append(token)
                continue
            first = token[0]
            last = token[-1]
            middle = token[1:-1]
            stripped = "".join(c for c in middle if c not in VOWELS)
            if stripped:
                rebuilt.append(first + stripped + last)
            else:
                rebuilt.append(token)
        else:
            rebuilt.append(token)
    result = "".join(rebuilt)
    return result

# Calculate compression for each sample
sample_ratios = []
for i, sample in enumerate(train_samples):
    text = sample["text"]
    cat = sample["category"]
    orig_bytes = len(text.encode("utf-8"))
    comp = compress_text(text, config)
    comp_bytes = len(comp.encode("utf-8"))
    ratio = (orig_bytes - comp_bytes) / orig_bytes * 100
    sample_ratios.append({
        "index": i,
        "category": cat,
        "ratio": ratio,
        "orig_bytes": orig_bytes,
        "comp_bytes": comp_bytes,
        "text": text,
    })

# Sort by ratio ascending (worst first)
sample_ratios.sort(key=lambda x: x["ratio"])

print("\nBottom 20 train samples by compression ratio:")
print(f"{'#':>3} {'Category':<20} {'Ratio':>7} {'Orig':>6} {'Comp':>6}")
print("-" * 50)
for i, s in enumerate(sample_ratios[:20]):
    print(f"{i+1:>3} {s['category']:<20} {s['ratio']:>6.1f}% {s['orig_bytes']:>6} {s['comp_bytes']:>6}")

# Now extract all words from the bottom 20 that are NOT in SYMBOL_MAP
print("\n\nExtracting uncompressed words from bottom 20 samples...")
symbol_words = set(config.SYMBOL_MAP.keys())
uncompressed_words = Counter()

for s in sample_ratios[:20]:
    words = re.findall(r"[a-z']+", s["text"].lower())
    for w in words:
        if w not in symbol_words:
            uncompressed_words[w] += 1

# Now count these words across the FULL train corpus
print("Counting frequencies across full train corpus...")
full_train_word_counts = Counter()
for sample in train_samples:
    words = re.findall(r"[a-z']+", sample["text"].lower())
    for w in words:
        full_train_word_counts[w] += 1

# Also count in val corpus
full_val_word_counts = Counter()
for sample in val_samples:
    words = re.findall(r"[a-z']+", sample["text"].lower())
    for w in words:
        full_val_word_counts[w] += 1

# Filter: words NOT in SYMBOL_MAP, appearing in both train and val
missed_words = []
for word, bottom20_count in uncompressed_words.items():
    if word in symbol_words:
        continue
    train_total = full_train_word_counts.get(word, 0)
    val_total = full_val_word_counts.get(word, 0)
    word_bytes = len(word.encode("utf-8"))
    # Savings: each occurrence saves (word_bytes - symbol_bytes)
    # Symbol is typically 2 bytes for UTF-8
    total_occurrences = train_total + val_total
    savings = total_occurrences * (word_bytes - 2)

    missed_words.append({
        "word": word,
        "bottom20_count": bottom20_count,
        "train_total": train_total,
        "val_total": val_total,
        "total": total_occurrences,
        "word_bytes": word_bytes,
        "savings": savings,
    })

# Sort by savings descending
missed_words.sort(key=lambda x: (-x["savings"], -x["total"]))

print("\n" + "=" * 100)
print("TOP 50 MISSED WORD CANDIDATES (from bottom 20 train samples, NOT in SYMBOL_MAP)")
print("=" * 100)
print(f"{'#':>3} {'Word':<25} {'B20':>4} {'Train':>5} {'Val':>4} {'Bytes':>5} {'Savings':>7}")
print("-" * 70)

for i, w in enumerate(missed_words[:50]):
    print(f"{i+1:>3} {w['word']:<25} {w['bottom20_count']:>4} {w['train_total']:>5} "
          f"{w['val_total']:>4} {w['word_bytes']:>5} {w['savings']:>7}")


# ═══════════════════════════════════════════════════════════
# PART 3: Category-level analysis
# ═══════════════════════════════════════════════════════════
print("\n\n" + "=" * 100)
print("COMPRESSION RATIO BY CATEGORY")
print("=" * 100)

cat_stats = {}
for s in sample_ratios:
    cat = s["category"]
    if cat not in cat_stats:
        cat_stats[cat] = {"total_orig": 0, "total_comp": 0, "count": 0, "ratios": []}
    cat_stats[cat]["total_orig"] += s["orig_bytes"]
    cat_stats[cat]["total_comp"] += s["comp_bytes"]
    cat_stats[cat]["count"] += 1
    cat_stats[cat]["ratios"].append(s["ratio"])

print(f"{'Category':<25} {'Count':>5} {'Avg Ratio':>10} {'Min':>7} {'Max':>7}")
print("-" * 60)
cat_avg = []
for cat, stats in sorted(cat_stats.items()):
    avg_ratio = sum(stats["ratios"]) / len(stats["ratios"])
    min_ratio = min(stats["ratios"])
    max_ratio = max(stats["ratios"])
    cat_avg.append((cat, avg_ratio))
    print(f"{cat:<25} {stats['count']:>5} {avg_ratio:>9.1f}% {min_ratio:>6.1f}% {max_ratio:>6.1f}%")

# Sort by avg ratio to show worst
cat_avg.sort(key=lambda x: x[1])
print("\nWorst categories (by avg compression ratio):")
for cat, avg in cat_avg[:5]:
    print(f"  {cat}: {avg:.1f}%")
