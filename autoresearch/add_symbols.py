"""
Add new high-value train-only words to SYMBOL_MAP.
Find words not in the map that have high byte savings.
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

# Find train-only words not in symbol map
candidates = []
for word, train_count in all_train_words.items():
    if word in existing_words:
        continue
    val_count = all_val_words.get(word, 0)
    word_bytes = len(word.encode('utf-8'))
    if word_bytes < 3:
        continue
    if train_count < 2 and val_count == 0:
        continue
    candidates.append({
        'word': word,
        'train_count': train_count,
        'val_count': val_count,
        'word_bytes': word_bytes,
    })

# Sort by total savings with 2-byte symbol
for c in candidates:
    c['savings_2byte'] = (c['word_bytes'] - 2) * (c['train_count'] + c['val_count'])
candidates.sort(key=lambda x: -x['savings_2byte'])

print(f"Candidate words not in symbol map: {len(candidates)}")
print(f"\nTop 50:")
for c in candidates[:50]:
    vl = c['val_count']
    tag = 'both' if vl > 0 else 'train_only'
    print(f"  {c['word']:<25} bytes={c['word_bytes']} tr={c['train_count']} vl={vl} sav={c['savings_2byte']} [{tag}]")

# Find free codes (2-byte first, then 3-byte)
def find_free_codes(n, all_used):
    free = []
    # 2-byte first
    for cp in range(0x0080, 0x0800):
        c = chr(cp)
        if c in all_used:
            continue
        b = c.encode('utf-8')
        if len(b) == 2:
            free.append(c)
            if len(free) >= n:
                return free
    # Then 3-byte
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

# Filter: only add words with savings >= 8 (with 2-byte code)
# Recompute savings based on actual code size later
to_add = [c for c in candidates if c['savings_2byte'] >= 8]
codes = find_free_codes(len(to_add), all_used)
print(f"\nFree 2-byte codes available: {len(codes)}")
print(f"Words with savings >= 8: {len(to_add)}")

if len(codes) < len(to_add):
    to_add = to_add[:len(codes)]

# Generate config lines, filtering by actual net savings
config_lines = []
config_lines.append("    # exp 15e: new symbol map entries")
added = 0
for i, entry in enumerate(to_add):
    if i >= len(codes):
        break
    code = codes[i]
    code_bytes = len(code.encode('utf-8'))
    word = entry['word']
    tr = entry['train_count']
    vl = entry['val_count']
    actual_savings = (entry['word_bytes'] - code_bytes) * (tr + vl)
    if actual_savings < 6:
        continue
    if vl > 0:
        config_lines.append(f'    "{word}": {repr(code)},  # savings={actual_savings}, train={tr}, val={vl}')
    else:
        config_lines.append(f'    "{word}": {repr(code)},  # savings={actual_savings}, train_only, count={tr}')
    added += 1

print(f"Symbol entries to add: {added}")

# Apply to config.py
config_path = Path(__file__).parent / "config.py"
content = config_path.read_text(encoding='utf-8')

# Find end of SYMBOL_MAP (line with just "}")
# SYMBOL_MAP ends before PHRASE_CODEBOOK section
lines = content.split('\n')
insert_idx = None
for i, line in enumerate(lines):
    if "PHRASE CODEBOOK" in line and "multi-word phrases" in line:
        # Go back to find the closing "}" of SYMBOL_MAP
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
print(f"\nInserted {len(config_lines)} symbol entries at line {insert_idx}")
