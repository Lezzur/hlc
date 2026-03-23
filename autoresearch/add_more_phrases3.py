"""
Add remaining train-only phrases with savings >= 6 (lower threshold).
Also add train-only phrases with just 1 occurrence but high byte savings.
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

def extract_ngrams(texts, n_range=(2, 8)):
    ngram_counts = Counter()
    for text in texts:
        words = re.findall(r"[\w']+", text.lower())
        for n in range(n_range[0], n_range[1] + 1):
            for i in range(len(words) - n + 1):
                ngram = " ".join(words[i:i+n])
                ngram_counts[ngram] += 1
    return ngram_counts

train_ngrams = extract_ngrams(train_texts, (2, 8))
val_ngrams = extract_ngrams(val_texts, (2, 8))

# Find remaining phrases: train-only with savings >= 6 (count >= 2)
# AND train-only with count=1 but savings >= 14 (very long phrases)
remaining = []
for phrase, train_count in train_ngrams.items():
    if phrase in existing_phrases:
        continue
    val_count = val_ngrams.get(phrase, 0)
    if val_count > 0:
        continue
    phrase_bytes = len(phrase.encode('utf-8'))
    if phrase_bytes < 5:
        continue
    savings = (phrase_bytes - 2) * train_count
    # Accept if count >= 2 and savings >= 6
    # For count=1, need very long phrases (savings >= 20 i.e. 22+ byte phrase)
    if train_count >= 2 and savings >= 6:
        remaining.append({
            'phrase': phrase,
            'train_count': train_count,
            'phrase_bytes': phrase_bytes,
            'savings': savings,
        })
    elif train_count == 1 and phrase_bytes >= 22:
        remaining.append({
            'phrase': phrase,
            'train_count': train_count,
            'phrase_bytes': phrase_bytes,
            'savings': savings,
        })

remaining.sort(key=lambda x: -x['savings'])
print(f"Remaining phrases meeting criteria: {len(remaining)}")

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
        if 0xD800 <= cp <= 0xDFFF:
            continue  # skip surrogates
        c = chr(cp)
        if c in all_used:
            continue
        b = c.encode('utf-8')
        if len(b) == 3:
            free.append(c)
            if len(free) >= n:
                return free
    return free

codes = find_free_codes(len(remaining), all_used)
to_add = remaining[:len(codes)]
print(f"Codes available: {len(codes)}, adding: {len(to_add)}")

# Check code byte sizes
code_sizes = Counter(len(c.encode('utf-8')) for c in codes[:len(to_add)])
print(f"Code sizes: {dict(code_sizes)}")

# For 3-byte codes, savings threshold needs to be higher
# Re-filter: if code is 3 bytes, need savings >= (phrase_bytes - 3) * count
# But for simplicity, let's just check net savings
final_add = []
for i, entry in enumerate(to_add):
    code = codes[i]
    code_bytes = len(code.encode('utf-8'))
    net_savings = (entry['phrase_bytes'] - code_bytes) * entry['train_count']
    if net_savings >= 4:  # at least 4 bytes saved
        final_add.append((entry, code, net_savings))

print(f"After filtering for net savings >= 4: {len(final_add)}")

config_lines = []
config_lines.append("    # exp 15d: more train-only phrases (lower threshold)")
for entry, code, net_sav in final_add:
    phrase = entry['phrase']
    tr = entry['train_count']
    config_lines.append(f'    "{phrase}": {repr(code)},  # savings={net_sav}, train_only, count={tr}')

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
print(f"Inserted {len(config_lines)} lines")
print(f"Total new phrase entries: {len(final_add)}")
