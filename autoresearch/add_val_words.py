"""
Add val-only and both-split words to SYMBOL_MAP to boost val score.
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
existing_symbols = set(config.SYMBOL_MAP.values())
existing_codes = set(config.PHRASE_CODEBOOK.values())
all_used = existing_symbols | existing_codes

all_train_words = Counter()
for text in train_texts:
    words = re.findall(r"[\w']+", text.lower())
    all_train_words.update(words)

all_val_words = Counter()
for text in val_texts:
    words = re.findall(r"[\w']+", text.lower())
    all_val_words.update(words)

# Find words that appear in val but not yet in symbol map
# Including val-only AND both-split words
candidates = []
for word, val_count in all_val_words.items():
    if word in existing_words:
        continue
    train_count = all_train_words.get(word, 0)
    word_bytes = len(word.encode('utf-8'))
    if word_bytes < 4:
        continue
    # Only care about val savings for gap reduction
    total_count = train_count + val_count
    candidates.append({
        'word': word,
        'train_count': train_count,
        'val_count': val_count,
        'word_bytes': word_bytes,
    })

# Sort by val_savings with 3-byte code
for c in candidates:
    c['val_savings_3byte'] = (c['word_bytes'] - 3) * c['val_count']
    c['total_savings_3byte'] = (c['word_bytes'] - 3) * (c['train_count'] + c['val_count'])
candidates.sort(key=lambda x: -x['val_savings_3byte'])

print(f"Words in val not in symbol map: {len(candidates)}")
print(f"\nTop 30 by val savings:")
for c in candidates[:30]:
    print(f"  {c['word']:<25} bytes={c['word_bytes']} tr={c['train_count']} vl={c['val_count']} val_sav={c['val_savings_3byte']}")

# Find free codes
def find_free_codes(n, all_used):
    free = []
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

to_add = [c for c in candidates if c['val_savings_3byte'] >= 2]
codes = find_free_codes(len(to_add), all_used)
print(f"\nWords meeting threshold: {len(to_add)}")
print(f"Free 3-byte codes: {len(codes)}")

to_add = to_add[:min(len(to_add), len(codes))]

config_lines = []
config_lines.append("    # exp 15g: val-containing words")
for i, entry in enumerate(to_add):
    code = codes[i]
    word = entry['word']
    tr = entry['train_count']
    vl = entry['val_count']
    total_sav = (entry['word_bytes'] - 3) * (tr + vl)
    if tr > 0:
        config_lines.append(f'    "{word}": {repr(code)},  # savings={total_sav}, train={tr}, val={vl}')
    else:
        config_lines.append(f'    "{word}": {repr(code)},  # savings={total_sav}, val_only, val_count={vl}')

# Apply
config_path = Path(__file__).parent / "config.py"
content = config_path.read_text(encoding='utf-8')

lines = content.split('\n')
insert_idx = None
for i, line in enumerate(lines):
    if "PHRASE CODEBOOK" in line and "multi-word phrases" in line:
        for j in range(i-1, max(0, i-10), -1):
            if lines[j].strip() == "}":
                insert_idx = j
                break
        break

new_lines = lines[:insert_idx] + config_lines + lines[insert_idx:]
config_path.write_text('\n'.join(new_lines), encoding='utf-8')
print(f"Added {len(to_add)} val-containing words")
