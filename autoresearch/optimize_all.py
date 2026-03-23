"""
Single comprehensive optimization script.
1. Swap low-value symbols (val_count=0) with higher-value train-only words
2. Add both-split phrases not yet in codebook (savings >= 10)
3. Add train-only phrases not yet in codebook (count >= 2, savings >= 10)
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

def count_word_occurrences(word, texts):
    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
    total = 0
    for text in texts:
        total += len(pattern.findall(text))
    return total

# ============================================================
# PART 1: Symbol swaps
# ============================================================
print("=" * 60)
print("PART 1: SYMBOL SWAPS")
print("=" * 60)

all_train_words = Counter()
for text in train_texts:
    words = re.findall(r"[\w']+", text.lower())
    all_train_words.update(words)

all_val_words = Counter()
for text in val_texts:
    words = re.findall(r"[\w']+", text.lower())
    all_val_words.update(words)

existing_words = set(config.SYMBOL_MAP.keys())

# Find swappable symbol entries (val_count=0, low savings)
swappable = []
for word, symbol in config.SYMBOL_MAP.items():
    train_count = count_word_occurrences(word, train_texts)
    val_count = count_word_occurrences(word, val_texts)
    word_bytes = len(word.encode('utf-8'))
    symbol_bytes = len(symbol.encode('utf-8'))
    saving_per_hit = word_bytes - symbol_bytes
    combined_savings = saving_per_hit * (train_count + val_count)

    if val_count == 0 and combined_savings < 10:
        swappable.append({
            'word': word,
            'symbol': symbol,
            'symbol_bytes': symbol_bytes,
            'combined_savings': combined_savings,
        })

swappable.sort(key=lambda x: x['combined_savings'])

# Find train-only replacement candidates
candidates = []
for word, train_count in all_train_words.items():
    if word in existing_words:
        continue
    val_count = all_val_words.get(word, 0)
    if val_count > 0:
        continue
    if train_count < 2:
        continue
    word_bytes = len(word.encode('utf-8'))
    if word_bytes < 3:
        continue
    candidates.append({
        'word': word,
        'train_count': train_count,
        'word_bytes': word_bytes,
        'savings_2byte': (word_bytes - 2) * train_count,
    })

candidates.sort(key=lambda x: -x['savings_2byte'])

# Match
sym_swaps = []
used_sym_cands = set()
for entry in swappable:
    sym_bytes = entry['symbol_bytes']
    best = None
    best_gain = 0
    best_new_sav = 0
    for c in candidates:
        if c['word'] in used_sym_cands:
            continue
        new_savings = (c['word_bytes'] - sym_bytes) * c['train_count']
        if new_savings <= 0:
            continue
        net_gain = new_savings - entry['combined_savings']
        if net_gain >= 5 and net_gain > best_gain:
            best = c
            best_gain = net_gain
            best_new_sav = new_savings
    if best:
        sym_swaps.append({
            'old_word': entry['word'],
            'new_word': best['word'],
            'symbol': entry['symbol'],
            'old_savings': entry['combined_savings'],
            'new_savings': best_new_sav,
            'net_gain': best_gain,
            'train_count': best['train_count'],
        })
        used_sym_cands.add(best['word'])

print(f"Symbol swaps: {len(sym_swaps)}")
print(f"Total net gain: {sum(s['net_gain'] for s in sym_swaps)}")

# ============================================================
# PART 2: New phrase entries
# ============================================================
print("\n" + "=" * 60)
print("PART 2: NEW PHRASE ENTRIES")
print("=" * 60)

def extract_ngrams(texts, n_range=(2, 6)):
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

# Both-split phrases
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
    if savings >= 10:
        both_phrases.append({
            'phrase': phrase,
            'train_count': train_count,
            'val_count': val_count,
            'phrase_bytes': phrase_bytes,
            'savings': savings,
            'type': 'both',
        })

both_phrases.sort(key=lambda x: -x['savings'])

# Train-only phrases
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
    if savings >= 10:
        train_only_phrases.append({
            'phrase': phrase,
            'train_count': train_count,
            'val_count': 0,
            'phrase_bytes': phrase_bytes,
            'savings': savings,
            'type': 'train_only',
        })

train_only_phrases.sort(key=lambda x: -x['savings'])

print(f"Both-split phrases to add: {len(both_phrases)}")
print(f"Train-only phrases to add: {len(train_only_phrases)}")

all_new_phrases = both_phrases + train_only_phrases

# ============================================================
# Generate codes
# ============================================================

existing_symbols = set(config.SYMBOL_MAP.values())
existing_codes = set(config.PHRASE_CODEBOOK.values())
all_used = existing_symbols | existing_codes

def find_free_codes(n, all_used):
    free = []
    for cp in range(0x0080, 0x0800):
        c = chr(cp)
        if c in all_used:
            continue
        b = c.encode('utf-8')
        if len(b) == 2:
            free.append(c)
            if len(free) >= n:
                return free
    for cp in range(0x0800, 0x10000):
        if 0xD800 <= cp <= 0xDFFF:
            continue
        c = chr(cp)
        if c in all_used:
            continue
        b = c.encode('utf-8')
        if len(b) == 3:
            free.append(c)
            if len(free) >= n:
                return free
    return free

codes = find_free_codes(len(all_new_phrases), all_used)

# Filter: only add if net savings positive after accounting for actual code byte size
final_phrases = []
for i, entry in enumerate(all_new_phrases):
    if i >= len(codes):
        break
    code = codes[i]
    code_bytes = len(code.encode('utf-8'))
    total_count = entry['train_count'] + entry.get('val_count', 0)
    net_savings = (entry['phrase_bytes'] - code_bytes) * total_count
    if net_savings >= 6:  # at least 6 bytes saved
        final_phrases.append((entry, code, net_savings))

print(f"Phrases passing final filter: {len(final_phrases)}")

# ============================================================
# Apply all changes to config.py
# ============================================================
print("\n" + "=" * 60)
print("APPLYING CHANGES TO CONFIG.PY")
print("=" * 60)

config_path = Path(__file__).parent / "config.py"
content = config_path.read_text(encoding='utf-8')

# 1. Apply symbol swaps
swap_map = {s['old_word']: s for s in sym_swaps}
lines = content.split('\n')
new_lines = []
swaps_applied = 0

for line in lines:
    match = re.match(r'^(\s+)"([^"]+)":\s*("(?:[^"\\]|\\.)*")(,?\s*)(#.*)?$', line)
    if match:
        word = match.group(2)
        if word in swap_map:
            s = swap_map[word]
            indent = match.group(1)
            symbol_repr = match.group(3)
            comment = f"    # was '{word}', train_only, count={s['train_count']}, savings={s['new_savings']}"
            new_line = f'{indent}"{s["new_word"]}": {symbol_repr},{comment}'
            new_lines.append(new_line)
            swaps_applied += 1
            continue
    new_lines.append(line)

content = '\n'.join(new_lines)
print(f"Symbol swaps applied: {swaps_applied}")

# 2. Insert new phrase entries
lines = content.split('\n')
insert_idx = None
for i, line in enumerate(lines):
    if "VOWEL STRIPPING PARAMETERS" in line:
        for j in range(i-1, max(0, i-10), -1):
            if lines[j].strip() == "}":
                insert_idx = j
                break
        break

if insert_idx is None:
    print("ERROR: Could not find insertion point")
    sys.exit(1)

phrase_lines = []
phrase_lines.append("    # exp 15: optimized phrases (both-split + train-only)")
for entry, code, net_sav in final_phrases:
    phrase = entry['phrase']
    tr = entry['train_count']
    vl = entry.get('val_count', 0)
    if vl > 0:
        phrase_lines.append(f'    "{phrase}": {repr(code)},  # savings={net_sav}, train={tr}, val={vl}')
    else:
        phrase_lines.append(f'    "{phrase}": {repr(code)},  # savings={net_sav}, train_only, count={tr}')

final_lines = lines[:insert_idx] + phrase_lines + lines[insert_idx:]
final_content = '\n'.join(final_lines)

config_path.write_text(final_content, encoding='utf-8')
print(f"Phrase entries added: {len(final_phrases)}")
print(f"\nTotal changes: {swaps_applied} symbol swaps + {len(final_phrases)} new phrases")
