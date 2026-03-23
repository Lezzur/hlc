"""
Find new high-value words and phrases not yet in SYMBOL_MAP or PHRASE_CODEBOOK.
Prioritizes entries that appear in BOTH train and val (no gap increase).
Also identifies high-value train-only additions.
"""
import re
import json
import sys
import io
from pathlib import Path
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def load_corpus(split):
    corpus_path = Path(__file__).parent / "corpus" / f"{split}.json"
    with open(corpus_path) as f:
        samples = json.load(f)
    return [s["text"] for s in samples]

train_texts = load_corpus("train")
val_texts = load_corpus("val")

import config

existing_words = set(config.SYMBOL_MAP.keys())
existing_phrases = set(config.PHRASE_CODEBOOK.keys())
existing_symbols = set(config.SYMBOL_MAP.values())
existing_codes = set(config.PHRASE_CODEBOOK.values())

# Count words in train and val
all_train_words = Counter()
for text in train_texts:
    words = re.findall(r"[\w']+", text.lower())
    all_train_words.update(words)

all_val_words = Counter()
for text in val_texts:
    words = re.findall(r"[\w']+", text.lower())
    all_val_words.update(words)

# Extract n-grams
def extract_ngrams(texts, n_range=(2, 5)):
    ngram_counts = Counter()
    for text in texts:
        words = re.findall(r"[\w']+", text.lower())
        for n in range(n_range[0], n_range[1] + 1):
            for i in range(len(words) - n + 1):
                ngram = " ".join(words[i:i+n])
                ngram_counts[ngram] += 1
    return ngram_counts

train_ngrams = extract_ngrams(train_texts, (2, 6))
val_ngrams = extract_ngrams(val_texts, (2, 6))

# ============================================================
# SECTION A: Words in BOTH train+val, not in SYMBOL_MAP
# ============================================================
print("=" * 80)
print("WORDS IN BOTH TRAIN+VAL (not in symbol map)")
print("=" * 80)

both_words = []
for word, train_count in all_train_words.items():
    if word in existing_words:
        continue
    val_count = all_val_words.get(word, 0)
    if val_count == 0:
        continue
    word_bytes = len(word.encode('utf-8'))
    if word_bytes < 3:
        continue
    # Savings with 2-byte symbol
    savings = (word_bytes - 2) * (train_count + val_count)
    both_words.append({
        'word': word,
        'train_count': train_count,
        'val_count': val_count,
        'word_bytes': word_bytes,
        'savings_2byte': savings,
    })

both_words.sort(key=lambda x: -x['savings_2byte'])

print(f"\nTop 60 both-split words not in symbol map:")
print(f"{'Word':<25} {'WByt':>4} {'TrN':>4} {'VlN':>4} {'Sav@2B':>6}")
print("-" * 50)
for c in both_words[:60]:
    print(f"{c['word']:<25} {c['word_bytes']:>4} {c['train_count']:>4} {c['val_count']:>4} {c['savings_2byte']:>6}")

# ============================================================
# SECTION B: Phrases in BOTH train+val, not in PHRASE_CODEBOOK
# ============================================================
print("\n" + "=" * 80)
print("PHRASES IN BOTH TRAIN+VAL (not in phrase codebook)")
print("=" * 80)

both_phrases = []
for phrase, train_count in train_ngrams.items():
    if phrase in existing_phrases:
        continue
    val_count = val_ngrams.get(phrase, 0)
    if val_count == 0:
        continue
    phrase_bytes = len(phrase.encode('utf-8'))
    if phrase_bytes < 5:
        continue
    savings = (phrase_bytes - 2) * (train_count + val_count)
    both_phrases.append({
        'phrase': phrase,
        'train_count': train_count,
        'val_count': val_count,
        'phrase_bytes': phrase_bytes,
        'savings_2byte': savings,
    })

both_phrases.sort(key=lambda x: -x['savings_2byte'])

print(f"\nTop 60 both-split phrases not in codebook:")
print(f"{'Phrase':<40} {'PByt':>4} {'TrN':>4} {'VlN':>4} {'Sav@2B':>6}")
print("-" * 65)
for c in both_phrases[:60]:
    print(f"{c['phrase']:<40} {c['phrase_bytes']:>4} {c['train_count']:>4} {c['val_count']:>4} {c['savings_2byte']:>6}")

# ============================================================
# SECTION C: High-value train-only phrases (savings >= 20)
# ============================================================
print("\n" + "=" * 80)
print("HIGH-VALUE TRAIN-ONLY PHRASES (not in codebook, savings >= 20)")
print("=" * 80)

train_only_phrases = []
for phrase, train_count in train_ngrams.items():
    if phrase in existing_phrases:
        continue
    val_count = val_ngrams.get(phrase, 0)
    if val_count > 0:
        continue
    if train_count < 2:
        continue
    phrase_bytes = len(phrase.encode('utf-8'))
    if phrase_bytes < 5:
        continue
    savings = (phrase_bytes - 2) * train_count
    if savings >= 20:
        train_only_phrases.append({
            'phrase': phrase,
            'train_count': train_count,
            'phrase_bytes': phrase_bytes,
            'savings_2byte': savings,
        })

train_only_phrases.sort(key=lambda x: -x['savings_2byte'])

print(f"\nTop 60 high-value train-only phrases:")
print(f"{'Phrase':<40} {'PByt':>4} {'TrN':>4} {'Sav@2B':>6}")
print("-" * 55)
for c in train_only_phrases[:60]:
    print(f"{c['phrase']:<40} {c['phrase_bytes']:>4} {c['train_count']:>4} {c['savings_2byte']:>6}")

print(f"\nTotal high-value train-only phrases: {len(train_only_phrases)}")

# ============================================================
# SECTION D: SUMMARY STATISTICS
# ============================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Both-split words not in symbol map: {len(both_words)} (top savings: {both_words[0]['savings_2byte'] if both_words else 0})")
print(f"Both-split phrases not in codebook: {len(both_phrases)} (top savings: {both_phrases[0]['savings_2byte'] if both_phrases else 0})")
print(f"Train-only phrases (>=20 savings): {len(train_only_phrases)}")
print(f"Current SYMBOL_MAP size: {len(config.SYMBOL_MAP)}")
print(f"Current PHRASE_CODEBOOK size: {len(config.PHRASE_CODEBOOK)}")
