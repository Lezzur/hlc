"""
Apply beneficial symbol swaps to config.py.
ONLY swaps entries with ZERO val occurrences (to avoid hurting val score).
"""
import re
import json
import sys
import io
from pathlib import Path
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load corpus
def load_corpus(split):
    corpus_path = Path(__file__).parent / "corpus" / f"{split}.json"
    with open(corpus_path) as f:
        samples = json.load(f)
    return [s["text"] for s in samples]

train_texts = load_corpus("train")
val_texts = load_corpus("val")

# Load config
import config

# Helper functions
def count_word_occurrences(word, texts):
    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
    total = 0
    for text in texts:
        total += len(pattern.findall(text))
    return total

# ============================================================
# STEP 1: Identify low-value entries with ZERO val occurrences
# ============================================================

sym_entries = []
for word, symbol in config.SYMBOL_MAP.items():
    train_count = count_word_occurrences(word, train_texts)
    val_count = count_word_occurrences(word, val_texts)
    word_bytes = len(word.encode('utf-8'))
    symbol_bytes = len(symbol.encode('utf-8'))
    saving_per_hit = word_bytes - symbol_bytes
    total_train_savings = saving_per_hit * train_count
    total_val_savings = saving_per_hit * val_count
    combined_savings = total_train_savings + total_val_savings

    sym_entries.append({
        'word': word,
        'symbol': symbol,
        'symbol_bytes': symbol_bytes,
        'word_bytes': word_bytes,
        'saving_per_hit': saving_per_hit,
        'train_count': train_count,
        'val_count': val_count,
        'total_train_savings': total_train_savings,
        'total_val_savings': total_val_savings,
        'combined_savings': combined_savings,
    })

# ONLY swap entries that have ZERO val occurrences AND low total savings
# This way we don't lose any val compression
swappable = [e for e in sym_entries if e['val_count'] == 0 and e['combined_savings'] < 10]
swappable.sort(key=lambda x: x['combined_savings'])

print(f"Total entries with val_count=0 and savings<10: {len(swappable)}")

# ============================================================
# STEP 2: Find train-only replacement candidates
# ============================================================

all_train_words = Counter()
for text in train_texts:
    words = re.findall(r"[\w']+", text.lower())
    all_train_words.update(words)

all_val_words = Counter()
for text in val_texts:
    words = re.findall(r"[\w']+", text.lower())
    all_val_words.update(words)

existing_words = set(config.SYMBOL_MAP.keys())

candidates = []
for word, train_count in all_train_words.items():
    if word in existing_words:
        continue
    val_count = all_val_words.get(word, 0)
    if val_count > 0:
        continue  # only train-only
    if train_count < 2:
        continue
    word_bytes = len(word.encode('utf-8'))
    if word_bytes < 3:
        continue
    candidates.append({
        'word': word,
        'train_count': train_count,
        'word_bytes': word_bytes,
    })

# Sort by potential savings descending
for c in candidates:
    c['savings_2byte'] = (c['word_bytes'] - 2) * c['train_count']
candidates.sort(key=lambda x: -x['savings_2byte'])

# ============================================================
# STEP 3: Match entries to best candidates (gain >= 5)
# ============================================================

swaps = []
used_candidates = set()

for entry in swappable:
    sym_bytes = entry['symbol_bytes']
    best = None
    best_gain = 0
    best_new_savings = 0

    for c in candidates:
        if c['word'] in used_candidates:
            continue
        new_savings = (c['word_bytes'] - sym_bytes) * c['train_count']
        if new_savings <= 0:
            continue
        net_gain = new_savings - entry['combined_savings']
        if net_gain >= 5 and net_gain > best_gain:
            best = c
            best_gain = net_gain
            best_new_savings = new_savings

    if best:
        swaps.append({
            'old_word': entry['word'],
            'new_word': best['word'],
            'symbol': entry['symbol'],
            'old_savings': entry['combined_savings'],
            'new_savings': best_new_savings,
            'net_gain': best_gain,
            'train_count': best['train_count'],
        })
        used_candidates.add(best['word'])

print(f"Total swaps to apply: {len(swaps)}")
total_gain = sum(s['net_gain'] for s in swaps)
print(f"Total net gain: {total_gain}")

# ============================================================
# STEP 4: Read config.py and apply swaps
# ============================================================

config_path = Path(__file__).parent / "config.py"
content = config_path.read_text(encoding='utf-8')

swap_map = {}
for s in swaps:
    swap_map[s['old_word']] = s

lines = content.split('\n')
new_lines = []
swaps_applied = 0

for line in lines:
    # Check if this line is a SYMBOL_MAP entry
    # Match lines like:     "word": "symbol",    # optional comment
    # or:                   "word": "\x08",       # optional comment
    match = re.match(r'^(\s+)"([^"]+)":\s*("(?:[^"\\]|\\.)*")(,?\s*)(#.*)?$', line)

    if match:
        word = match.group(2)

        if word in swap_map:
            s = swap_map[word]
            new_word = s['new_word']
            indent = match.group(1)
            symbol_repr = match.group(3)
            comment = f"    # was '{word}', train_only, count={s['train_count']}, savings={s['new_savings']}"

            new_line = f'{indent}"{new_word}": {symbol_repr},{comment}'
            new_lines.append(new_line)
            swaps_applied += 1
            continue

    new_lines.append(line)

print(f"Swaps applied in config.py: {swaps_applied}")

# Write the updated config
new_content = '\n'.join(new_lines)
config_path.write_text(new_content, encoding='utf-8')
print("Config.py updated successfully.")

# Print swap summary
swaps.sort(key=lambda x: -x['net_gain'])
for s in swaps[:30]:
    print(f"  {s['old_word']:<20} -> {s['new_word']:<20} (gain: {s['net_gain']}, old_sav: {s['old_savings']}, new_sav: {s['new_savings']})")
