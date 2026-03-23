"""
Add more train-only phrases with savings >= 10.
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

import importlib
import config
importlib.reload(config)

existing_phrases = set(config.PHRASE_CODEBOOK.keys())
existing_symbols = set(config.SYMBOL_MAP.values())
existing_codes = set(config.PHRASE_CODEBOOK.values())
all_used = existing_symbols | existing_codes

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

# Find remaining train-only phrases with savings >= 10
remaining = []
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
        remaining.append({
            'phrase': phrase,
            'train_count': train_count,
            'phrase_bytes': phrase_bytes,
            'savings': savings,
        })

remaining.sort(key=lambda x: -x['savings'])
print(f"Remaining train-only phrases (sav>=10): {len(remaining)}")

# Find free codes
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
        c = chr(cp)
        if c in all_used:
            continue
        b = c.encode('utf-8')
        if len(b) == 3:
            free.append(c)
            if len(free) >= n:
                return free
    return free

# Also find remaining both-split phrases not yet captured
both_remaining = []
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
        both_remaining.append({
            'phrase': phrase,
            'train_count': train_count,
            'val_count': val_count,
            'phrase_bytes': phrase_bytes,
            'savings': savings,
        })

both_remaining.sort(key=lambda x: -x['savings'])
print(f"Remaining both-split phrases (sav>=10): {len(both_remaining)}")

# Combine: both-split first, then train-only
to_add = both_remaining + remaining
codes = find_free_codes(len(to_add), all_used)
if len(codes) < len(to_add):
    print(f"Available codes: {len(codes)}, truncating")
    to_add = to_add[:len(codes)]

print(f"Total phrases to add: {len(to_add)}")

config_lines = []
config_lines.append("    # exp 15c: remaining high-value phrases")
for i, entry in enumerate(to_add):
    code = codes[i]
    phrase = entry['phrase']
    savings = entry['savings']
    tr = entry['train_count']
    vl = entry.get('val_count', 0)
    if vl > 0:
        config_lines.append(f'    "{phrase}": {repr(code)},  # savings={savings}, train={tr}, val={vl}')
    else:
        config_lines.append(f'    "{phrase}": {repr(code)},  # savings={savings}, train_only, count={tr}')

# Apply to config.py
config_path = Path(__file__).parent / "config.py"
content = config_path.read_text(encoding='utf-8')

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

new_lines = lines[:insert_idx] + config_lines + lines[insert_idx:]
new_content = '\n'.join(new_lines)
config_path.write_text(new_content, encoding='utf-8')
print(f"\nInserted {len(config_lines)} lines at line {insert_idx}")
