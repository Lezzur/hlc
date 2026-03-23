"""
Add train-only phrases, capped at 1000 to avoid slowdown.
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
all_used = set(config.SYMBOL_MAP.values()) | set(config.PHRASE_CODEBOOK.values())

def extract_ngrams(texts, n_range=(2, 6)):
    ngram_counts = Counter()
    for text in texts:
        words = re.findall(r"[\w']+", text.lower())
        for n in range(n_range[0], n_range[1] + 1):
            for i in range(len(words) - n + 1):
                ngram_counts[" ".join(words[i:i+n])] += 1
    return ngram_counts

train_ngrams = extract_ngrams(train_texts, (2, 5))
val_ngrams = extract_ngrams(val_texts, (2, 5))

# Train-only phrases
cands = []
for phrase, tc in train_ngrams.items():
    if phrase in existing_phrases: continue
    if val_ngrams.get(phrase, 0) > 0: continue
    pb = len(phrase.encode('utf-8'))
    if pb < 5: continue
    sav = (pb - 3) * tc
    if sav >= 4:
        cands.append({'phrase': phrase, 'tc': tc, 'pb': pb, 'sav': sav})

cands.sort(key=lambda x: -x['sav'])
# Cap at 1000
cands = cands[:1000]
print(f"Train-only phrases to add: {len(cands)}")

def find_free_codes(n, all_used):
    free = []
    for cp in range(0x0800, 0x10000):
        if 0xD800 <= cp <= 0xDFFF: continue
        c = chr(cp)
        if c not in all_used and len(c.encode('utf-8')) == 3:
            free.append(c)
            if len(free) >= n: return free
    return free

codes = find_free_codes(len(cands), all_used)
print(f"Free codes: {len(codes)}")

config_path = Path(__file__).parent / "config.py"
content = config_path.read_text(encoding='utf-8')

lines = content.split('\n')
idx = None
for i, line in enumerate(lines):
    if "VOWEL STRIPPING" in line:
        for j in range(i-1, max(0, i-10), -1):
            if lines[j].strip() == "}": idx = j; break
        break

plines = ["    # exp 15l: train-only phrases (capped)"]
for i, entry in enumerate(cands):
    if i >= len(codes): break
    c = codes[i]
    cb = len(c.encode('utf-8'))
    net_sav = (entry['pb'] - cb) * entry['tc']
    if net_sav < 3: continue
    plines.append(f'    "{entry["phrase"]}": {repr(c)},  # savings={net_sav}, train_only, count={entry["tc"]}')

lines = lines[:idx] + plines + lines[idx:]
config_path.write_text('\n'.join(lines), encoding='utf-8')
print(f"Added {len(plines)-1} train phrases")
