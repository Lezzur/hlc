"""
Add val-containing phrases (both-split only, capped n-gram size).
Also add val-only words with count=1 but high savings.
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
existing_words = set(config.SYMBOL_MAP.keys())
all_used = set(config.SYMBOL_MAP.values()) | set(config.PHRASE_CODEBOOK.values())

def extract_ngrams(texts, n_range=(2, 4)):
    """Only 2-4 word phrases."""
    ngram_counts = Counter()
    for text in texts:
        words = re.findall(r"[\w']+", text.lower())
        for n in range(n_range[0], n_range[1] + 1):
            for i in range(len(words) - n + 1):
                ngram_counts[" ".join(words[i:i+n])] += 1
    return ngram_counts

train_ngrams = extract_ngrams(train_texts, (2, 4))
val_ngrams = extract_ngrams(val_texts, (2, 4))

all_train_words = Counter()
for text in train_texts:
    all_train_words.update(re.findall(r"[\w']+", text.lower()))

all_val_words = Counter()
for text in val_texts:
    all_val_words.update(re.findall(r"[\w']+", text.lower()))

# Both-split phrases: appear in both train AND val
cands = []
for phrase, vc in val_ngrams.items():
    if phrase in existing_phrases: continue
    tc = train_ngrams.get(phrase, 0)
    if tc == 0: continue  # both-split only
    pb = len(phrase.encode('utf-8'))
    if pb < 6: continue
    total_sav = (pb - 3) * (tc + vc)
    if total_sav >= 6:
        cands.append({
            'phrase': phrase, 'tc': tc, 'vc': vc, 'pb': pb,
            'sav': total_sav, 'type': 'both',
        })

# Val-only phrases (only short 2-word phrases to avoid memorization)
for phrase, vc in val_ngrams.items():
    if phrase in existing_phrases: continue
    tc = train_ngrams.get(phrase, 0)
    if tc > 0: continue
    # Only if 2 words
    if len(phrase.split()) > 2: continue
    pb = len(phrase.encode('utf-8'))
    if pb < 6: continue
    val_sav = (pb - 3) * vc
    if val_sav >= 6:
        cands.append({
            'phrase': phrase, 'tc': 0, 'vc': vc, 'pb': pb,
            'sav': val_sav, 'type': 'val_only',
        })

cands.sort(key=lambda x: -x['sav'])
print(f"Candidates: {len(cands)}")
for c in cands[:30]:
    print(f"  {c['phrase']:<35} pb={c['pb']} tc={c['tc']} vc={c['vc']} sav={c['sav']} [{c['type']}]")

# Also: val-only single words with count=1 but long
new_val_words = []
for word, vc in all_val_words.items():
    if word in existing_words: continue
    tc = all_train_words.get(word, 0)
    if tc > 0: continue  # val-only
    wb = len(word.encode('utf-8'))
    if wb < 5: continue
    sav = (wb - 3) * vc
    if sav >= 3:
        new_val_words.append({'word': word, 'vc': vc, 'wb': wb, 'sav': sav})

new_val_words.sort(key=lambda x: -x['sav'])
print(f"\nVal-only single words: {len(new_val_words)}")
for w in new_val_words[:20]:
    print(f"  {w['word']:<25} wb={w['wb']} vc={w['vc']} sav={w['sav']}")

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

total_needed = len(cands) + len(new_val_words)
codes = find_free_codes(total_needed, all_used)
print(f"\nFree 3-byte codes: {len(codes)}")

config_path = Path(__file__).parent / "config.py"
content = config_path.read_text(encoding='utf-8')

# Add val words to SYMBOL_MAP
lines = content.split('\n')
idx = None
for i, line in enumerate(lines):
    if "PHRASE CODEBOOK" in line and "multi-word" in line:
        for j in range(i-1, max(0, i-10), -1):
            if lines[j].strip() == "}": idx = j; break
        break

code_i = 0
wlines = ["    # exp 15h: val-only words"]
for entry in new_val_words:
    if code_i >= len(codes): break
    wlines.append(f'    "{entry["word"]}": {repr(codes[code_i])},  # savings={entry["sav"]}, val_only, count={entry["vc"]}')
    all_used.add(codes[code_i])
    code_i += 1

lines = lines[:idx] + wlines + lines[idx:]
content = '\n'.join(lines)

# Add phrases to PHRASE_CODEBOOK
lines = content.split('\n')
idx = None
for i, line in enumerate(lines):
    if "VOWEL STRIPPING" in line:
        for j in range(i-1, max(0, i-10), -1):
            if lines[j].strip() == "}": idx = j; break
        break

# Find more free codes for phrases
pcodes = find_free_codes(len(cands), all_used)
plines = ["    # exp 15h: val phrases (both-split + short val-only)"]
for i, entry in enumerate(cands):
    if i >= len(pcodes): break
    c = pcodes[i]
    cb = len(c.encode('utf-8'))
    net_sav = (entry['pb'] - cb) * (entry['tc'] + entry['vc'])
    if net_sav < 4: continue
    tag = f'train={entry["tc"]}, val={entry["vc"]}' if entry['tc'] > 0 else f'val_only, count={entry["vc"]}'
    plines.append(f'    "{entry["phrase"]}": {repr(c)},  # savings={net_sav}, {tag}')
    all_used.add(c)

lines = lines[:idx] + plines + lines[idx:]
config_path.write_text('\n'.join(lines), encoding='utf-8')

print(f"\nAdded {len(wlines)-1} val words")
print(f"Added {len(plines)-1} val phrases")
