"""
Analyze train/val compression gap v3:
- Find ALL n-gram phrases that appear 2+ times across COMBINED train+val
- Must appear at least once in train AND once in val
- Calculate real savings accounting for symbol map + vowel stripping
- Look at missed words comprehensively
"""

import json
import re
import sys
import os
from pathlib import Path
from collections import Counter

# Fix encoding for Windows
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# Load corpus
corpus_dir = Path(__file__).parent / "corpus"
with open(corpus_dir / "train.json") as f:
    train_samples = json.load(f)
with open(corpus_dir / "val.json") as f:
    val_samples = json.load(f)

# Load config
sys.path.insert(0, str(Path(__file__).parent))
import config

existing_phrases = {p.lower() for p in config.PHRASE_CODEBOOK.keys()}
symbol_words = set(config.SYMBOL_MAP.keys())

# ═══════════════════════════════════════════════════════════
# PART 1: Extract raw text words (after removing existing phrase matches)
# To find phrases that haven't been captured yet, we need to look
# at what TEXT remains after phrase+symbol compression
# ═══════════════════════════════════════════════════════════

def extract_ngrams_from_raw(text, min_n=2, max_n=5):
    """Extract case-insensitive n-grams directly from raw text."""
    words = re.findall(r"[a-z']+", text.lower())
    ngrams = Counter()
    for n in range(min_n, max_n + 1):
        for i in range(len(words) - n + 1):
            phrase = " ".join(words[i:i+n])
            ngrams[phrase] += 1
    return ngrams

print("Extracting n-grams from train corpus (raw text)...")
train_phrases = Counter()
for sample in train_samples:
    train_phrases += extract_ngrams_from_raw(sample["text"])

print("Extracting n-grams from val corpus (raw text)...")
val_phrases = Counter()
for sample in val_samples:
    val_phrases += extract_ngrams_from_raw(sample["text"])

# Check which existing phrases are SUBSTRINGS of longer potential phrases
# This helps find "extension" phrases

print("\n\nFinding phrase candidates: train>=2, val>=1, NOT already in codebook...")
candidates = []
for phrase, train_count in train_phrases.items():
    if train_count < 2:
        continue
    val_count = val_phrases.get(phrase, 0)
    if val_count < 1:
        continue
    # Skip if already an exact match in codebook
    if phrase in existing_phrases:
        continue

    phrase_bytes = len(phrase.encode("utf-8"))
    total_count = train_count + val_count

    # Estimate current compressed size of this phrase
    words = phrase.split()
    current_size = 0
    for w in words:
        if w in symbol_words:
            sym = config.SYMBOL_MAP[w]
            current_size += len(sym.encode("utf-8"))
        else:
            # After vowel stripping, roughly 70% of bytes for words >= 4 chars
            wb = len(w.encode("utf-8"))
            if len(w) >= 4:
                current_size += max(3, int(wb * 0.65))
            else:
                current_size += wb
    current_size += len(words) - 1  # spaces

    # New code = 2 bytes
    savings_per = current_size - 2
    savings = total_count * savings_per

    if savings <= 0:
        continue

    candidates.append({
        "phrase": phrase,
        "train": train_count,
        "val": val_count,
        "total": total_count,
        "raw_bytes": phrase_bytes,
        "est_comp_bytes": current_size,
        "savings_per": savings_per,
        "savings": savings,
    })

candidates.sort(key=lambda x: -x["savings"])

print(f"Total candidates: {len(candidates)}")
print("\n" + "=" * 110)
print("TOP 100 PHRASE CANDIDATES")
print("=" * 110)
print(f"{'#':>3} {'Phrase':<50} {'Tr':>3} {'Vl':>3} {'RawB':>4} {'EstCB':>5} {'$/hit':>5} {'Total$':>7}")
print("-" * 110)

for i, c in enumerate(candidates[:100]):
    print(f"{i+1:>3} {c['phrase']:<50} {c['train']:>3} {c['val']:>3} "
          f"{c['raw_bytes']:>4} {c['est_comp_bytes']:>5} {c['savings_per']:>5} "
          f"{c['savings']:>7}")


# ═══════════════════════════════════════════════════════════
# PART 2: ALL words analysis — find words not in SYMBOL_MAP
# that appear in both train AND val
# ═══════════════════════════════════════════════════════════

print("\n\n" + "=" * 110)
print("MISSED WORDS: NOT in SYMBOL_MAP, appear in BOTH train AND val")
print("=" * 110)

train_words = Counter()
for sample in train_samples:
    for w in re.findall(r"[a-z']+", sample["text"].lower()):
        train_words[w] += 1

val_words = Counter()
for sample in val_samples:
    for w in re.findall(r"[a-z']+", sample["text"].lower()):
        val_words[w] += 1

missed = []
for word, tc in train_words.items():
    if word in symbol_words:
        continue
    vc = val_words.get(word, 0)
    if vc == 0:
        continue
    wb = len(word.encode("utf-8"))
    if wb <= 2:
        continue
    total = tc + vc
    savings = total * (wb - 2)
    missed.append({
        "word": word,
        "train": tc,
        "val": vc,
        "total": total,
        "bytes": wb,
        "savings": savings,
    })

missed.sort(key=lambda x: -x["savings"])

print(f"\n{'#':>3} {'Word':<25} {'Train':>5} {'Val':>4} {'Bytes':>5} {'Savings':>7}")
print("-" * 60)
for i, w in enumerate(missed[:50]):
    print(f"{i+1:>3} {w['word']:<25} {w['train']:>5} {w['val']:>4} "
          f"{w['bytes']:>5} {w['savings']:>7}")


# ═══════════════════════════════════════════════════════════
# PART 3: High-frequency TRAIN-ONLY words (these could help if
# the val corpus happens to use similar patterns)
# ═══════════════════════════════════════════════════════════

print("\n\n" + "=" * 110)
print("HIGH-FREQ TRAIN-ONLY WORDS (val=0) — adding these would ONLY help train, risk overfitting")
print("=" * 110)

train_only = []
for word, tc in train_words.items():
    if word in symbol_words:
        continue
    vc = val_words.get(word, 0)
    if vc > 0:
        continue
    wb = len(word.encode("utf-8"))
    if wb <= 2:
        continue
    savings = tc * (wb - 2)
    if savings < 10:
        continue
    train_only.append({
        "word": word,
        "train": tc,
        "bytes": wb,
        "savings": savings,
    })

train_only.sort(key=lambda x: -x["savings"])

print(f"\n{'#':>3} {'Word':<25} {'Train':>5} {'Bytes':>5} {'Savings':>7}")
print("-" * 50)
for i, w in enumerate(train_only[:50]):
    print(f"{i+1:>3} {w['word']:<25} {w['train']:>5} "
          f"{w['bytes']:>5} {w['savings']:>7}")


# ═══════════════════════════════════════════════════════════
# PART 4: Look at what specific text remains after compression
# in the worst-performing samples
# ═══════════════════════════════════════════════════════════

import importlib
importlib.reload(config)

VOWELS_SET = set("aeiouAEIOU")

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
            stripped = "".join(c for c in middle if c not in VOWELS_SET)
            if stripped:
                rebuilt.append(first + stripped + last)
            else:
                rebuilt.append(token)
        else:
            rebuilt.append(token)
    result = "".join(rebuilt)
    return result

# Get ratios for all train samples
sample_data = []
for i, sample in enumerate(train_samples):
    text = sample["text"]
    cat = sample["category"]
    orig_bytes = len(text.encode("utf-8"))
    comp = compress_text(text, config)
    comp_bytes = len(comp.encode("utf-8"))
    ratio = (orig_bytes - comp_bytes) / orig_bytes * 100
    sample_data.append({
        "index": i,
        "category": cat,
        "ratio": ratio,
        "text": text,
        "compressed": comp,
    })

sample_data.sort(key=lambda x: x["ratio"])

print("\n\n" + "=" * 110)
print("REMAINING WORDS IN BOTTOM 20 SAMPLES (after compression)")
print("=" * 110)

# Collect all remaining words across bottom 20
all_remaining = Counter()
for s in sample_data[:20]:
    remaining = re.findall(r"[a-zA-Z]{3,}", s["compressed"])
    for w in remaining:
        all_remaining[w.lower()] += 1

print(f"\nMost frequent remaining words (after compression) in bottom 20 samples:")
print(f"{'#':>3} {'Word':<25} {'Freq in B20':>10} {'In Train':>8} {'In Val':>7} {'Bytes':>5}")
print("-" * 65)

for i, (word, freq) in enumerate(all_remaining.most_common(60)):
    tc = train_words.get(word, 0)
    vc = val_words.get(word, 0)
    wb = len(word.encode("utf-8"))
    # Check if this is a vowel-stripped form
    is_stripped = word in symbol_words
    marker = "*" if is_stripped else ""
    print(f"{i+1:>3} {word:<25} {freq:>10} {tc:>8} {vc:>7} {wb:>5} {marker}")


# ═══════════════════════════════════════════════════════════
# PART 5: Category-level stats
# ═══════════════════════════════════════════════════════════

print("\n\n" + "=" * 80)
print("COMPRESSION BY CATEGORY (sorted worst to best)")
print("=" * 80)

cat_stats = {}
for s in sample_data:
    cat = s["category"]
    if cat not in cat_stats:
        cat_stats[cat] = []
    cat_stats[cat].append(s["ratio"])

cat_avgs = [(cat, sum(r)/len(r)) for cat, r in cat_stats.items()]
cat_avgs.sort(key=lambda x: x[1])

print(f"{'Category':<25} {'Avg Ratio':>10}")
print("-" * 35)
for cat, avg in cat_avgs:
    print(f"{cat:<25} {avg:>9.1f}%")

# ═══════════════════════════════════════════════════════════
# PART 6: What phrases from worst categories appear in val?
# This is the key question — find cross-corpus phrases
# from the WORST categories
# ═══════════════════════════════════════════════════════════

print("\n\n" + "=" * 110)
print("PHRASES FROM WORST 5 CATEGORIES THAT ALSO APPEAR IN VAL")
print("(Categories: casual, instructional, creative, journalism, ai_conversation)")
print("=" * 110)

worst_cats = {"casual", "instructional", "creative", "journalism", "ai_conversation"}

# Extract phrases only from worst-category train samples
worst_train_phrases = Counter()
for sample in train_samples:
    if sample["category"] in worst_cats:
        worst_train_phrases += extract_ngrams_from_raw(sample["text"])

# Find overlap with val
worst_candidates = []
for phrase, wt_count in worst_train_phrases.items():
    val_count = val_phrases.get(phrase, 0)
    if val_count < 1:
        continue
    if phrase in existing_phrases:
        continue

    train_total = train_phrases.get(phrase, 0)
    if train_total < 2:
        continue

    phrase_bytes = len(phrase.encode("utf-8"))
    total = train_total + val_count

    words = phrase.split()
    current_size = 0
    for w in words:
        if w in symbol_words:
            sym = config.SYMBOL_MAP[w]
            current_size += len(sym.encode("utf-8"))
        else:
            wb = len(w.encode("utf-8"))
            if len(w) >= 4:
                current_size += max(3, int(wb * 0.65))
            else:
                current_size += wb
    current_size += len(words) - 1

    savings_per = current_size - 2
    savings = total * savings_per

    if savings <= 0:
        continue

    worst_candidates.append({
        "phrase": phrase,
        "worst_cat_count": wt_count,
        "train_total": train_total,
        "val": val_count,
        "savings": savings,
    })

worst_candidates.sort(key=lambda x: -x["savings"])

print(f"\n{'#':>3} {'Phrase':<50} {'WCat':>4} {'Train':>5} {'Val':>3} {'Savings':>7}")
print("-" * 90)
for i, c in enumerate(worst_candidates[:50]):
    print(f"{i+1:>3} {c['phrase']:<50} {c['worst_cat_count']:>4} {c['train_total']:>5} "
          f"{c['val']:>3} {c['savings']:>7}")
