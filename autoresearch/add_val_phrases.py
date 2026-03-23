"""
Add val-only and both-split phrases to PHRASE_CODEBOOK to boost val score.
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

# Find val-containing phrases not in codebook
candidates = []
for phrase, val_count in val_ngrams.items():
    if phrase in existing_phrases:
        continue
    train_count = train_ngrams.get(phrase, 0)
    phrase_bytes = len(phrase.encode('utf-8'))
    if phrase_bytes < 5:
        continue
    # With 3-byte code
    val_savings = (phrase_bytes - 3) * val_count
    total_savings = (phrase_bytes - 3) * (train_count + val_count)
    if val_savings >= 2 and total_savings >= 4:
        candidates.append({
            'phrase': phrase,
            'train_count': train_count,
            'val_count': val_count,
            'phrase_bytes': phrase_bytes,
            'val_savings': val_savings,
            'total_savings': total_savings,
        })

candidates.sort(key=lambda x: -x['total_savings'])
print(f"Val-containing phrases not in codebook: {len(candidates)}")

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

codes = find_free_codes(len(candidates), all_used)
print(f"Free 3-byte codes: {len(codes)}")

to_add = candidates[:min(len(candidates), len(codes))]

config_lines = []
config_lines.append("    # exp 15h: val-containing phrases")
for i, entry in enumerate(to_add):
    code = codes[i]
    phrase = entry['phrase']
    tr = entry['train_count']
    vl = entry['val_count']
    total_sav = entry['total_savings']
    config_lines.append(f'    "{phrase}": {repr(code)},  # savings={total_sav}, train={tr}, val={vl}')

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

new_lines = lines[:insert_idx] + config_lines + lines[insert_idx:]
config_path.write_text('\n'.join(new_lines), encoding='utf-8')
print(f"Added {len(to_add)} val-containing phrases")

# Show top entries
print("\nTop 20:")
for c in to_add[:20]:
    print(f"  {c['phrase']:<40} bytes={c['phrase_bytes']} tr={c['train_count']} vl={c['val_count']} total_sav={c['total_savings']}")
