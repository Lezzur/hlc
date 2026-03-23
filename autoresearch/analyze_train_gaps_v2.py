"""
Analyze train/val compression gap v2:
- Find NEW phrase candidates (not covered by existing phrases)
- Also find phrases with train>=2, val>=1 OR train>=3, val>=0 (but with lower weight)
- Look at missed words more carefully
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

# Get existing phrases and words
existing_phrases = {p.lower() for p in config.PHRASE_CODEBOOK.keys()}
symbol_words = set(config.SYMBOL_MAP.keys())

# ═══════════════════════════════════════════════════════════
# PART 1: Find phrase candidates more carefully
# ═══════════════════════════════════════════════════════════

def extract_ngrams(text, min_n=2, max_n=5):
    """Extract n-grams from text, case-insensitive."""
    words = re.findall(r"[a-z']+", text.lower())
    ngrams = Counter()
    for n in range(min_n, max_n + 1):
        for i in range(len(words) - n + 1):
            phrase = " ".join(words[i:i+n])
            ngrams[phrase] += 1
    return ngrams

print("Extracting n-grams from train corpus...")
train_phrases = Counter()
for sample in train_samples:
    ngrams = extract_ngrams(sample["text"])
    train_phrases += ngrams

print("Extracting n-grams from val corpus...")
val_phrases = Counter()
for sample in val_samples:
    ngrams = extract_ngrams(sample["text"])
    val_phrases += ngrams

def is_covered_by_existing(phrase):
    """Check if this phrase is already in PHRASE_CODEBOOK."""
    return phrase.lower() in existing_phrases

def phrase_contains_only_symbols(phrase):
    """Check if all words in phrase are already in SYMBOL_MAP."""
    words = phrase.split()
    return all(w in symbol_words for w in words)

# Criteria: train >= 2, val >= 1 (to generalize)
# BUT we want to see ALL candidates, even those where words are in symbol map
# because phrase-level compression can still help by reducing word boundaries

print("\nFinding phrase candidates (train>=2, val>=1, not in existing PHRASE_CODEBOOK)...")
candidates = []
for phrase, train_count in train_phrases.items():
    if train_count < 2:
        continue
    val_count = val_phrases.get(phrase, 0)
    if val_count < 1:
        continue
    if is_covered_by_existing(phrase):
        continue

    phrase_bytes = len(phrase.encode("utf-8"))
    total_count = train_count + val_count

    # Calculate ACTUAL savings considering symbol map compression
    # If a word is in symbol_map, it already gets compressed to ~2 bytes
    # So phrase savings = (current_compressed_bytes - 2)
    words = phrase.split()
    current_compressed_bytes = 0
    for w in words:
        if w in symbol_words:
            sym = config.SYMBOL_MAP[w]
            current_compressed_bytes += len(sym.encode("utf-8"))
        else:
            # Word gets vowel-stripped but stays as text
            # Approximate: vowel strip saves ~30% on words >= 4 chars
            wbytes = len(w.encode("utf-8"))
            if len(w) >= 4:
                current_compressed_bytes += max(3, int(wbytes * 0.7))
            else:
                current_compressed_bytes += wbytes
    # Add spaces between words
    current_compressed_bytes += len(words) - 1

    # New phrase code would be 2 bytes (UTF-8)
    savings_per_hit = current_compressed_bytes - 2
    savings = total_count * savings_per_hit

    if savings <= 0:
        continue

    all_in_symbols = phrase_contains_only_symbols(phrase)

    candidates.append({
        "phrase": phrase,
        "train_count": train_count,
        "val_count": val_count,
        "total_count": total_count,
        "phrase_bytes": phrase_bytes,
        "compressed_bytes": current_compressed_bytes,
        "savings_per_hit": savings_per_hit,
        "savings": savings,
        "all_words_in_symbols": all_in_symbols,
    })

# Sort by savings descending
candidates.sort(key=lambda x: (-x["savings"], -x["total_count"]))

print(f"\nTotal candidates found: {len(candidates)}")

print("\n" + "=" * 120)
print("TOP 100 PHRASE CANDIDATES (sorted by estimated savings after symbol compression)")
print("=" * 120)
print(f"{'#':>3} {'Phrase':<45} {'Tr':>3} {'Vl':>3} {'PhrB':>4} {'CompB':>5} {'Save/hit':>8} {'Total$':>7} {'AllSym':>6}")
print("-" * 120)

for i, c in enumerate(candidates[:100]):
    sym_flag = "Y" if c["all_words_in_symbols"] else "N"
    print(f"{i+1:>3} {c['phrase']:<45} {c['train_count']:>3} {c['val_count']:>3} "
          f"{c['phrase_bytes']:>4} {c['compressed_bytes']:>5} {c['savings_per_hit']:>8} "
          f"{c['savings']:>7} {sym_flag:>6}")


# ═══════════════════════════════════════════════════════════
# PART 2: Missed words — words NOT in SYMBOL_MAP that appear
# frequently in BOTH train and val
# ═══════════════════════════════════════════════════════════

print("\n\n" + "=" * 120)
print("MISSED WORDS ANALYSIS: Words NOT in SYMBOL_MAP appearing in BOTH train AND val")
print("=" * 120)

# Count all words in train and val
train_word_counts = Counter()
for sample in train_samples:
    words = re.findall(r"[a-z']+", sample["text"].lower())
    for w in words:
        train_word_counts[w] += 1

val_word_counts = Counter()
for sample in val_samples:
    words = re.findall(r"[a-z']+", sample["text"].lower())
    for w in words:
        val_word_counts[w] += 1

missed_words = []
for word, train_count in train_word_counts.items():
    if word in symbol_words:
        continue
    val_count = val_word_counts.get(word, 0)
    word_bytes = len(word.encode("utf-8"))
    total = train_count + val_count

    # Calculate savings: bytes saved = (word_bytes - 2_bytes_for_symbol) per occurrence
    # But only count if word_bytes > 2
    if word_bytes <= 2:
        continue
    savings = total * (word_bytes - 2)

    missed_words.append({
        "word": word,
        "train_count": train_count,
        "val_count": val_count,
        "total": total,
        "word_bytes": word_bytes,
        "savings": savings,
        "in_val": val_count > 0,
    })

missed_words.sort(key=lambda x: (-x["savings"], -x["total"]))

# Show top 50 that ARE in both train and val
print("\nTop 50 missed words IN BOTH train and val:")
print(f"{'#':>3} {'Word':<25} {'Train':>5} {'Val':>4} {'Bytes':>5} {'Savings':>7}")
print("-" * 60)

count = 0
for w in missed_words:
    if not w["in_val"]:
        continue
    count += 1
    if count > 50:
        break
    print(f"{count:>3} {w['word']:<25} {w['train_count']:>5} {w['val_count']:>4} "
          f"{w['word_bytes']:>5} {w['savings']:>7}")

# Also show top words train-only (for reference)
print("\n\nTop 50 missed words TRAIN ONLY (val=0) — for reference:")
print(f"{'#':>3} {'Word':<25} {'Train':>5} {'Val':>4} {'Bytes':>5} {'Savings':>7}")
print("-" * 60)

count = 0
for w in missed_words:
    if w["in_val"]:
        continue
    count += 1
    if count > 50:
        break
    print(f"{count:>3} {w['word']:<25} {w['train_count']:>5} {w['val_count']:>4} "
          f"{w['word_bytes']:>5} {w['savings']:>7}")


# ═══════════════════════════════════════════════════════════
# PART 3: Detailed look at bottom 5 train samples
# ═══════════════════════════════════════════════════════════

print("\n\n" + "=" * 120)
print("DETAILED LOOK AT WORST 5 TRAIN SAMPLES — what remains uncompressed?")
print("=" * 120)

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

# Get all sample ratios
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
        "text": text,
        "compressed": comp,
    })

sample_ratios.sort(key=lambda x: x["ratio"])

for s in sample_ratios[:5]:
    print(f"\n--- {s['category']} (ratio: {s['ratio']:.1f}%) ---")
    print(f"ORIGINAL: {s['text'][:200]}...")
    print(f"COMPRESSED: {s['compressed'][:200]}...")

    # Show remaining text words (not symbols)
    remaining_words = re.findall(r"[a-zA-Z]{3,}", s["compressed"])
    remaining_unique = sorted(set(w.lower() for w in remaining_words))
    print(f"REMAINING WORDS ({len(remaining_unique)}): {', '.join(remaining_unique[:30])}")
