"""
Add train-only words (not phrases) to close the train/val gap.
Words are fast to process (no phrase matching overhead).
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
all_used = set(config.SYMBOL_MAP.values()) | set(config.PHRASE_CODEBOOK.values())

all_train_words = Counter()
for text in train_texts:
    all_train_words.update(re.findall(r"[\w']+", text.lower()))

all_val_words = Counter()
for text in val_texts:
    all_val_words.update(re.findall(r"[\w']+", text.lower()))

# Train-only words not in map
new_words = []
for word, tc in all_train_words.items():
    if word in existing_words: continue
    if all_val_words.get(word, 0) > 0: continue
    wb = len(word.encode('utf-8'))
    if wb < 4: continue
    sav = (wb - 3) * tc
    if sav >= 1:  # Very low threshold -- even 1 byte helps
        new_words.append({'word': word, 'tc': tc, 'wb': wb, 'sav': sav})

new_words.sort(key=lambda x: -x['sav'])
print(f"Train-only words not in map: {len(new_words)}")

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

codes = find_free_codes(len(new_words), all_used)
print(f"Free 3-byte codes: {len(codes)}")

to_add = new_words[:min(len(new_words), len(codes))]

config_path = Path(__file__).parent / "config.py"
content = config_path.read_text(encoding='utf-8')

lines = content.split('\n')
idx = None
for i, line in enumerate(lines):
    if "PHRASE CODEBOOK" in line and "multi-word" in line:
        for j in range(i-1, max(0, i-10), -1):
            if lines[j].strip() == "}": idx = j; break
        break

wlines = ["    # exp 15k: train-only words (gap closing)"]
for i, entry in enumerate(to_add):
    wlines.append(f'    "{entry["word"]}": {repr(codes[i])},  # savings={entry["sav"]}, train_only, count={entry["tc"]}')

lines = lines[:idx] + wlines + lines[idx:]
config_path.write_text('\n'.join(lines), encoding='utf-8')
print(f"Added {len(to_add)} train words")
