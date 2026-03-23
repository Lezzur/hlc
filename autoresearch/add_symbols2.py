"""
Add more train-only words to SYMBOL_MAP using 3-byte codes.
Lower threshold to pick up more words.
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

# Find words not in symbol map
candidates = []
for word, train_count in all_train_words.items():
    if word in existing_words:
        continue
    val_count = all_val_words.get(word, 0)
    word_bytes = len(word.encode('utf-8'))
    if word_bytes < 4:  # need at least 4 bytes to save 1 byte with 3-byte code
        continue
    total_count = train_count + val_count
    if total_count < 1:
        continue
    # With 3-byte code: savings = (word_bytes - 3) * total_count
    savings_3byte = (word_bytes - 3) * total_count
    if savings_3byte >= 4:
        candidates.append({
            'word': word,
            'train_count': train_count,
            'val_count': val_count,
            'word_bytes': word_bytes,
            'savings_3byte': savings_3byte,
        })

candidates.sort(key=lambda x: -x['savings_3byte'])
print(f"Remaining candidates (savings@3B >= 4): {len(candidates)}")

# Find free 3-byte codes
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

codes = find_free_codes(len(candidates), all_used)
print(f"Free 3-byte codes available: {len(codes)}")

to_add = candidates[:min(len(candidates), len(codes))]
print(f"Will add: {len(to_add)}")

# Generate config lines
config_lines = []
config_lines.append("    # exp 15f: more symbol map entries (3-byte codes)")
for i, entry in enumerate(to_add):
    code = codes[i]
    word = entry['word']
    savings = entry['savings_3byte']
    tr = entry['train_count']
    vl = entry['val_count']
    if vl > 0:
        config_lines.append(f'    "{word}": {repr(code)},  # savings={savings}, train={tr}, val={vl}')
    else:
        config_lines.append(f'    "{word}": {repr(code)},  # savings={savings}, train_only, count={tr}')

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

if insert_idx is None:
    print("ERROR: Could not find SYMBOL_MAP end")
    sys.exit(1)

new_lines = lines[:insert_idx] + config_lines + lines[insert_idx:]
new_content = '\n'.join(new_lines)
config_path.write_text(new_content, encoding='utf-8')
print(f"Inserted {len(to_add)} entries")
