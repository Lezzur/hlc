"""
Comprehensive swap analysis script.
Computes actual byte savings for every SYMBOL_MAP and PHRASE_CODEBOOK entry.
Finds beneficial swaps from train-only words/phrases.
"""
import re
import sys
import io
import json
from pathlib import Path
from collections import Counter

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load corpus
def load_corpus(split):
    corpus_path = Path(__file__).parent / "corpus" / f"{split}.json"
    with open(corpus_path) as f:
        samples = json.load(f)
    return [s["text"] for s in samples]

train_texts = load_corpus("train")
val_texts = load_corpus("val")
train_blob = " ".join(train_texts).lower()
val_blob = " ".join(val_texts).lower()

# Load config
import config

# ============================================================
# STEP 1: Compute actual savings for every SYMBOL_MAP entry
# ============================================================

def count_word_occurrences(word, texts):
    """Count exact word boundary occurrences in texts."""
    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
    total = 0
    for text in texts:
        total += len(pattern.findall(text))
    return total

def word_byte_savings(word, symbol, train_count, val_count):
    """
    Compute actual byte savings.
    Original: word bytes per occurrence
    Replacement: symbol UTF-8 bytes per occurrence
    But we must account for phrase layer happening first —
    if the word is part of a phrase, it won't be replaced by symbol.
    For simplicity, use raw counts (phrase interactions are complex).
    """
    word_bytes = len(word.encode('utf-8'))
    symbol_bytes = len(symbol.encode('utf-8'))
    saving_per_hit = word_bytes - symbol_bytes
    total_train = saving_per_hit * train_count
    total_val = saving_per_hit * val_count
    return saving_per_hit, total_train, total_val

print("=" * 80)
print("SYMBOL MAP ANALYSIS")
print("=" * 80)

sym_low_value = []  # entries with actual_savings < 10 (combined)
sym_all = []

for word, symbol in config.SYMBOL_MAP.items():
    train_count = count_word_occurrences(word, train_texts)
    val_count = count_word_occurrences(word, val_texts)

    word_bytes = len(word.encode('utf-8'))
    symbol_bytes = len(symbol.encode('utf-8'))
    saving_per_hit = word_bytes - symbol_bytes

    total_train_savings = saving_per_hit * train_count
    total_val_savings = saving_per_hit * val_count
    combined_savings = total_train_savings + total_val_savings

    entry = {
        'word': word,
        'symbol': symbol,
        'symbol_bytes': symbol_bytes,
        'word_bytes': word_bytes,
        'saving_per_hit': saving_per_hit,
        'train_count': train_count,
        'val_count': val_count,
        'total_train_savings': total_train_savings,
        'total_val_savings': total_val_savings,
        'combined_savings': combined_savings,
    }
    sym_all.append(entry)

    if combined_savings < 10:
        sym_low_value.append(entry)

# Sort low-value by combined savings
sym_low_value.sort(key=lambda x: x['combined_savings'])

print(f"\nTotal SYMBOL_MAP entries: {len(config.SYMBOL_MAP)}")
print(f"Entries with combined savings < 10: {len(sym_low_value)}")
print(f"\nLowest value entries (savings < 10):")
print(f"{'Word':<25} {'Symbol':>6} {'SByt':>4} {'WByt':>4} {'Save/hit':>8} {'TrainN':>6} {'ValN':>4} {'TrSav':>5} {'VlSav':>5} {'Total':>5}")
print("-" * 100)
for e in sym_low_value[:80]:
    print(f"{e['word']:<25} {repr(e['symbol']):>6} {e['symbol_bytes']:>4} {e['word_bytes']:>4} {e['saving_per_hit']:>8} {e['train_count']:>6} {e['val_count']:>4} {e['total_train_savings']:>5} {e['total_val_savings']:>5} {e['combined_savings']:>5}")

# Find entries with NEGATIVE savings (symbol is bigger than word)
neg_savings = [e for e in sym_all if e['saving_per_hit'] < 0]
neg_savings.sort(key=lambda x: x['saving_per_hit'])
print(f"\n\nEntries with NEGATIVE saving per hit (symbol bigger than word): {len(neg_savings)}")
print(f"{'Word':<25} {'Symbol':>6} {'SByt':>4} {'WByt':>4} {'Save/hit':>8} {'TrainN':>6} {'ValN':>4} {'Total':>5}")
print("-" * 100)
for e in neg_savings[:40]:
    print(f"{e['word']:<25} {repr(e['symbol']):>6} {e['symbol_bytes']:>4} {e['word_bytes']:>4} {e['saving_per_hit']:>8} {e['train_count']:>6} {e['val_count']:>4} {e['combined_savings']:>5}")

# Find entries with ZERO count (never appear)
zero_count = [e for e in sym_all if e['train_count'] == 0 and e['val_count'] == 0]
print(f"\n\nEntries with ZERO occurrences in both train+val: {len(zero_count)}")
for e in zero_count[:20]:
    print(f"  {e['word']:<25} symbol={repr(e['symbol'])}")

# ============================================================
# STEP 2: Compute actual savings for every PHRASE_CODEBOOK entry
# ============================================================

print("\n" + "=" * 80)
print("PHRASE CODEBOOK ANALYSIS")
print("=" * 80)

def count_phrase_occurrences(phrase, texts):
    """Count case-insensitive phrase occurrences in texts."""
    pattern = re.compile(re.escape(phrase), re.IGNORECASE)
    total = 0
    for text in texts:
        total += len(pattern.findall(text))
    return total

phrase_low_value = []
phrase_all = []

for phrase, code in config.PHRASE_CODEBOOK.items():
    train_count = count_phrase_occurrences(phrase, train_texts)
    val_count = count_phrase_occurrences(phrase, val_texts)

    phrase_bytes = len(phrase.encode('utf-8'))
    code_bytes = len(code.encode('utf-8'))
    saving_per_hit = phrase_bytes - code_bytes

    total_train_savings = saving_per_hit * train_count
    total_val_savings = saving_per_hit * val_count
    combined_savings = total_train_savings + total_val_savings

    entry = {
        'phrase': phrase,
        'code': code,
        'code_bytes': code_bytes,
        'phrase_bytes': phrase_bytes,
        'saving_per_hit': saving_per_hit,
        'train_count': train_count,
        'val_count': val_count,
        'total_train_savings': total_train_savings,
        'total_val_savings': total_val_savings,
        'combined_savings': combined_savings,
    }
    phrase_all.append(entry)

    if combined_savings < 10:
        phrase_low_value.append(entry)

phrase_low_value.sort(key=lambda x: x['combined_savings'])

print(f"\nTotal PHRASE_CODEBOOK entries: {len(config.PHRASE_CODEBOOK)}")
print(f"Entries with combined savings < 10: {len(phrase_low_value)}")
print(f"\nLowest value phrase entries (savings < 10):")
print(f"{'Phrase':<35} {'Code':>6} {'CByt':>4} {'PByt':>4} {'Save/hit':>8} {'TrN':>4} {'VlN':>4} {'TrSav':>5} {'VlSav':>5} {'Total':>5}")
print("-" * 120)
for e in phrase_low_value[:80]:
    print(f"{e['phrase']:<35} {repr(e['code']):>6} {e['code_bytes']:>4} {e['phrase_bytes']:>4} {e['saving_per_hit']:>8} {e['train_count']:>4} {e['val_count']:>4} {e['total_train_savings']:>5} {e['total_val_savings']:>5} {e['combined_savings']:>5}")

# ============================================================
# STEP 3: Find train-only words for SYMBOL swaps
# ============================================================

print("\n" + "=" * 80)
print("CANDIDATE TRAIN-ONLY WORDS (for symbol swaps)")
print("=" * 80)

# Extract all words from train
all_train_words = Counter()
for text in train_texts:
    words = re.findall(r"[\w']+", text.lower())
    all_train_words.update(words)

all_val_words = Counter()
for text in val_texts:
    words = re.findall(r"[\w']+", text.lower())
    all_val_words.update(words)

# Find train-only words not in SYMBOL_MAP
existing_words = set(config.SYMBOL_MAP.keys())
existing_symbols = set(config.SYMBOL_MAP.values())

# For each low-value symbol entry, find the best replacement
# Low-value = entries with symbol_bytes >= 2 (multi-byte symbols) that could be reused
swappable_symbols = []
for e in sym_low_value:
    if e['combined_savings'] < 10:
        swappable_symbols.append(e)

# All available replacement candidates: train-only words not currently in symbol map
# Must have higher savings than the current entry
candidates = []
for word, train_count in all_train_words.items():
    if word in existing_words:
        continue
    val_count = all_val_words.get(word, 0)
    if val_count > 0:
        continue  # only train-only
    if train_count < 2:
        continue  # need at least 2 occurrences
    word_bytes = len(word.encode('utf-8'))
    if word_bytes < 3:
        continue  # too short to save much
    candidates.append({
        'word': word,
        'train_count': train_count,
        'word_bytes': word_bytes,
    })

# For each candidate, compute savings with a 2-byte symbol (typical)
for c in candidates:
    # Savings = (word_bytes - 2) * train_count for a 2-byte symbol
    c['savings_2byte'] = (c['word_bytes'] - 2) * c['train_count']
    # Savings with 1-byte symbol
    c['savings_1byte'] = (c['word_bytes'] - 1) * c['train_count']

candidates.sort(key=lambda x: -x['savings_2byte'])

print(f"\nTop 50 train-only candidate words (not in map, no val hits):")
print(f"{'Word':<25} {'WByt':>4} {'TrN':>4} {'Sav@2B':>6}")
print("-" * 50)
for c in candidates[:50]:
    print(f"{c['word']:<25} {c['word_bytes']:>4} {c['train_count']:>4} {c['savings_2byte']:>6}")

# ============================================================
# STEP 4: Compute proposed swaps for symbols
# ============================================================

print("\n" + "=" * 80)
print("PROPOSED SYMBOL SWAPS (net gain >= 5)")
print("=" * 80)

swaps_sym = []
used_candidates = set()

# Sort swappable symbols by combined_savings ascending (worst first)
swappable_symbols.sort(key=lambda x: x['combined_savings'])

for entry in swappable_symbols:
    sym_bytes = entry['symbol_bytes']
    # Find best candidate that would give better savings with THIS symbol
    best = None
    best_gain = 0
    for c in candidates:
        if c['word'] in used_candidates:
            continue
        # New savings = (word_bytes - sym_bytes) * train_count
        new_savings = (c['word_bytes'] - sym_bytes) * c['train_count']
        if new_savings <= 0:
            continue
        net_gain = new_savings - entry['combined_savings']
        if net_gain >= 5 and net_gain > best_gain:
            best = c
            best_gain = net_gain
            best_new_savings = new_savings

    if best:
        swaps_sym.append({
            'old_word': entry['word'],
            'old_savings': entry['combined_savings'],
            'new_word': best['word'],
            'new_savings': best_new_savings,
            'net_gain': best_gain,
            'symbol': entry['symbol'],
            'sym_bytes': sym_bytes,
            'new_train_count': best['train_count'],
            'new_word_bytes': best['word_bytes'],
        })
        used_candidates.add(best['word'])

swaps_sym.sort(key=lambda x: -x['net_gain'])

print(f"\nBeneficial symbol swaps found: {len(swaps_sym)}")
print(f"\n{'Old Word':<20} {'OldSav':>6} {'New Word':<20} {'NewSav':>6} {'NetGain':>7} {'Symbol':>8} {'SByt':>4} {'TrN':>4} {'WByt':>4}")
print("-" * 100)
total_gain = 0
for s in swaps_sym:
    print(f"{s['old_word']:<20} {s['old_savings']:>6} {s['new_word']:<20} {s['new_savings']:>6} {s['net_gain']:>7} {repr(s['symbol']):>8} {s['sym_bytes']:>4} {s['new_train_count']:>4} {s['new_word_bytes']:>4}")
    total_gain += s['net_gain']

print(f"\nTotal net gain from symbol swaps: {total_gain}")

# ============================================================
# STEP 5: Find train-only phrases for PHRASE swaps
# ============================================================

print("\n" + "=" * 80)
print("CANDIDATE TRAIN-ONLY PHRASES")
print("=" * 80)

# Extract bigrams and trigrams from train
def extract_ngrams(texts, n_range=(2, 5)):
    """Extract n-grams from texts."""
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

existing_phrases = set(config.PHRASE_CODEBOOK.keys())

# Find train-only phrases with high value
phrase_candidates = []
for phrase, train_count in train_ngrams.items():
    if phrase in existing_phrases:
        continue
    val_count = val_ngrams.get(phrase, 0)
    if val_count > 0:
        continue  # only train-only
    if train_count < 2:
        continue
    phrase_bytes = len(phrase.encode('utf-8'))
    if phrase_bytes < 4:
        continue
    # Savings with a 2-byte code
    savings_2byte = (phrase_bytes - 2) * train_count
    phrase_candidates.append({
        'phrase': phrase,
        'train_count': train_count,
        'phrase_bytes': phrase_bytes,
        'savings_2byte': savings_2byte,
    })

phrase_candidates.sort(key=lambda x: -x['savings_2byte'])

print(f"\nTop 50 train-only candidate phrases (not in codebook):")
print(f"{'Phrase':<40} {'PByt':>4} {'TrN':>4} {'Sav@2B':>6}")
print("-" * 60)
for c in phrase_candidates[:50]:
    print(f"{c['phrase']:<40} {c['phrase_bytes']:>4} {c['train_count']:>4} {c['savings_2byte']:>6}")

# ============================================================
# STEP 6: Proposed phrase swaps
# ============================================================

print("\n" + "=" * 80)
print("PROPOSED PHRASE SWAPS (net gain >= 5)")
print("=" * 80)

swappable_phrases = []
for e in phrase_low_value:
    if e['combined_savings'] < 10:
        swappable_phrases.append(e)

swappable_phrases.sort(key=lambda x: x['combined_savings'])

swaps_phrase = []
used_phrase_candidates = set()

for entry in swappable_phrases:
    code_bytes = entry['code_bytes']
    best = None
    best_gain = 0
    for c in phrase_candidates:
        if c['phrase'] in used_phrase_candidates:
            continue
        new_savings = (c['phrase_bytes'] - code_bytes) * c['train_count']
        if new_savings <= 0:
            continue
        net_gain = new_savings - entry['combined_savings']
        if net_gain >= 5 and net_gain > best_gain:
            best = c
            best_gain = net_gain
            best_new_savings = new_savings

    if best:
        swaps_phrase.append({
            'old_phrase': entry['phrase'],
            'old_savings': entry['combined_savings'],
            'new_phrase': best['phrase'],
            'new_savings': best_new_savings,
            'net_gain': best_gain,
            'code': entry['code'],
            'code_bytes': code_bytes,
            'new_train_count': best['train_count'],
            'new_phrase_bytes': best['phrase_bytes'],
        })
        used_phrase_candidates.add(best['phrase'])

swaps_phrase.sort(key=lambda x: -x['net_gain'])

print(f"\nBeneficial phrase swaps found: {len(swaps_phrase)}")
print(f"\n{'Old Phrase':<35} {'OldSav':>6} {'New Phrase':<35} {'NewSav':>6} {'NetGain':>7} {'Code':>6} {'CByt':>4}")
print("-" * 140)
total_phrase_gain = 0
for s in swaps_phrase:
    print(f"{s['old_phrase']:<35} {s['old_savings']:>6} {s['new_phrase']:<35} {s['new_savings']:>6} {s['net_gain']:>7} {repr(s['code']):>6} {s['code_bytes']:>4}")
    total_phrase_gain += s['net_gain']

print(f"\nTotal net gain from phrase swaps: {total_phrase_gain}")

# ============================================================
# STEP 7: High-value train-only phrases (savings >= 20) not yet captured
# ============================================================

print("\n" + "=" * 80)
print("HIGH-VALUE TRAIN-ONLY PHRASES (savings >= 20) NOT IN CODEBOOK")
print("=" * 80)

high_value = [c for c in phrase_candidates if c['savings_2byte'] >= 20 and c['phrase'] not in used_phrase_candidates]
high_value.sort(key=lambda x: -x['savings_2byte'])

print(f"\nHigh-value train-only phrases not yet captured: {len(high_value)}")
print(f"{'Phrase':<40} {'PByt':>4} {'TrN':>4} {'Sav@2B':>6}")
print("-" * 60)
for c in high_value[:50]:
    print(f"{c['phrase']:<40} {c['phrase_bytes']:>4} {c['train_count']:>4} {c['savings_2byte']:>6}")

# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Symbol entries with savings < 10: {len(sym_low_value)}")
print(f"Beneficial symbol swaps (gain >= 5): {len(swaps_sym)}")
print(f"Total symbol swap net gain: {total_gain}")
print(f"")
print(f"Phrase entries with savings < 10: {len(phrase_low_value)}")
print(f"Beneficial phrase swaps (gain >= 5): {len(swaps_phrase)}")
print(f"Total phrase swap net gain: {total_phrase_gain}")
print(f"")
print(f"High-value train-only phrases (>=20) still available: {len(high_value)}")
print(f"Grand total potential gain: {total_gain + total_phrase_gain}")
