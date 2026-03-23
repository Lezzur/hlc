"""
Add more train-only entries to close the gap.
Focus on train-only words and phrases not yet captured.
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

existing_words = set(config.SYMBOL_MAP.keys())
existing_phrases = set(config.PHRASE_CODEBOOK.keys())
all_used = set(config.SYMBOL_MAP.values()) | set(config.PHRASE_CODEBOOK.values())

all_train_words = Counter()
for text in train_texts:
    all_train_words.update(re.findall(r"[\w']+", text.lower()))

all_val_words = Counter()
for text in val_texts:
    all_val_words.update(re.findall(r"[\w']+", text.lower()))

def extract_ngrams(texts, n_range=(2, 8)):
    ngram_counts = Counter()
    for text in texts:
        words = re.findall(r"[\w']+", text.lower())
        for n in range(n_range[0], n_range[1] + 1):
            for i in range(len(words) - n + 1):
                ngram_counts[" ".join(words[i:i+n])] += 1
    return ngram_counts

train_ngrams = extract_ngrams(train_texts, (2, 6))
val_ngrams = extract_ngrams(val_texts, (2, 6))

# 1. Train-only words not in map (count >= 1, word_bytes >= 4)
new_words = []
for word, tc in all_train_words.items():
    if word in existing_words: continue
    if all_val_words.get(word, 0) > 0: continue
    wb = len(word.encode('utf-8'))
    if wb < 4: continue
    sav = (wb - 3) * tc
    if sav >= 2:
        new_words.append({'word': word, 'tc': tc, 'wb': wb, 'sav': sav})

new_words.sort(key=lambda x: -x['sav'])
print(f"Train-only words not in map: {len(new_words)}")

# 2. Train-only phrases not in codebook
new_phrases = []
for phrase, tc in train_ngrams.items():
    if phrase in existing_phrases: continue
    if val_ngrams.get(phrase, 0) > 0: continue
    pb = len(phrase.encode('utf-8'))
    if pb < 5: continue
    sav = (pb - 3) * tc
    if sav >= 4:
        new_phrases.append({'phrase': phrase, 'tc': tc, 'pb': pb, 'sav': sav})

new_phrases.sort(key=lambda x: -x['sav'])
print(f"Train-only phrases not in codebook: {len(new_phrases)}")

# Find free codes
def find_free_codes(n, all_used):
    free = []
    for cp in range(0x0800, 0x10000):
        if 0xD800 <= cp <= 0xDFFF: continue
        c = chr(cp)
        if c not in all_used and len(c.encode('utf-8')) == 3:
            free.append(c)
            if len(free) >= n: return free
    return free

total_needed = len(new_words) + len(new_phrases)
codes = find_free_codes(total_needed, all_used)
print(f"Free 3-byte codes: {len(codes)}")

# Cap at available codes
code_i = 0

# Apply words to SYMBOL_MAP
config_path = Path(__file__).parent / "config.py"
content = config_path.read_text(encoding='utf-8')

lines = content.split('\n')
idx = None
for i, line in enumerate(lines):
    if "PHRASE CODEBOOK" in line and "multi-word" in line:
        for j in range(i-1, max(0, i-10), -1):
            if lines[j].strip() == "}": idx = j; break
        break

wlines = ["    # exp 15j: train-only words (gap closing)"]
for entry in new_words:
    if code_i >= len(codes): break
    wlines.append(f'    "{entry["word"]}": {repr(codes[code_i])},  # savings={entry["sav"]}, train_only, count={entry["tc"]}')
    all_used.add(codes[code_i])
    code_i += 1

lines = lines[:idx] + wlines + lines[idx:]
content = '\n'.join(lines)

# Apply phrases to PHRASE_CODEBOOK
lines = content.split('\n')
idx = None
for i, line in enumerate(lines):
    if "VOWEL STRIPPING" in line:
        for j in range(i-1, max(0, i-10), -1):
            if lines[j].strip() == "}": idx = j; break
        break

pcodes = find_free_codes(len(new_phrases), all_used)
plines = ["    # exp 15j: train-only phrases (gap closing)"]
for i, entry in enumerate(new_phrases):
    if i >= len(pcodes): break
    c = pcodes[i]
    cb = len(c.encode('utf-8'))
    net_sav = (entry['pb'] - cb) * entry['tc']
    if net_sav < 3: continue
    plines.append(f'    "{entry["phrase"]}": {repr(c)},  # savings={net_sav}, train_only, count={entry["tc"]}')
    all_used.add(c)

lines = lines[:idx] + plines + lines[idx:]
config_path.write_text('\n'.join(lines), encoding='utf-8')

print(f"Added {len(wlines)-1} train words")
print(f"Added {len(plines)-1} train phrases")
