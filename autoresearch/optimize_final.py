"""
Final comprehensive optimization.
1. Symbol swaps (val_count=0 entries)
2. New phrase entries (both-split + train-only, savings >= 10, count >= 2)
3. New symbol entries (train-only, 3-byte codes)
4. Val-only/both-split words (to boost val)
5. Val-containing phrases (moderate count, savings >= 8, capped)
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

import config

def count_word_occurrences(word, texts):
    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
    total = 0
    for text in texts:
        total += len(pattern.findall(text))
    return total

def extract_ngrams(texts, n_range=(2, 6)):
    ngram_counts = Counter()
    for text in texts:
        words = re.findall(r"[\w']+", text.lower())
        for n in range(n_range[0], n_range[1] + 1):
            for i in range(len(words) - n + 1):
                ngram = " ".join(words[i:i+n])
                ngram_counts[ngram] += 1
    return ngram_counts

all_train_words = Counter()
for text in train_texts:
    words = re.findall(r"[\w']+", text.lower())
    all_train_words.update(words)

all_val_words = Counter()
for text in val_texts:
    words = re.findall(r"[\w']+", text.lower())
    all_val_words.update(words)

train_ngrams = extract_ngrams(train_texts, (2, 6))
val_ngrams = extract_ngrams(val_texts, (2, 6))

existing_words = set(config.SYMBOL_MAP.keys())
existing_phrases = set(config.PHRASE_CODEBOOK.keys())
existing_symbols = set(config.SYMBOL_MAP.values())
existing_codes = set(config.PHRASE_CODEBOOK.values())
all_used = existing_symbols | existing_codes

def find_free_codes(n, all_used, byte_size=None):
    free = []
    if byte_size is None or byte_size == 2:
        for cp in range(0x0080, 0x0800):
            c = chr(cp)
            if c in all_used:
                continue
            b = c.encode('utf-8')
            if len(b) == 2:
                free.append(c)
                if len(free) >= n:
                    return free
    if byte_size is None or byte_size == 3:
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

# ============================================================
# PART 1: Symbol swaps (val_count=0 only)
# ============================================================
print("PART 1: SYMBOL SWAPS")

swappable = []
for word, symbol in config.SYMBOL_MAP.items():
    train_count = count_word_occurrences(word, train_texts)
    val_count = count_word_occurrences(word, val_texts)
    word_bytes = len(word.encode('utf-8'))
    symbol_bytes = len(symbol.encode('utf-8'))
    saving_per_hit = word_bytes - symbol_bytes
    combined_savings = saving_per_hit * (train_count + val_count)
    if val_count == 0 and combined_savings < 10:
        swappable.append({
            'word': word, 'symbol': symbol, 'symbol_bytes': symbol_bytes,
            'combined_savings': combined_savings,
        })

swappable.sort(key=lambda x: x['combined_savings'])

sym_candidates = []
for word, train_count in all_train_words.items():
    if word in existing_words:
        continue
    if all_val_words.get(word, 0) > 0:
        continue
    if train_count < 2:
        continue
    word_bytes = len(word.encode('utf-8'))
    if word_bytes < 3:
        continue
    sym_candidates.append({'word': word, 'train_count': train_count, 'word_bytes': word_bytes,
                          'savings_2byte': (word_bytes - 2) * train_count})
sym_candidates.sort(key=lambda x: -x['savings_2byte'])

sym_swaps = []
used_sym = set()
for entry in swappable:
    best = None; best_gain = 0; best_sav = 0
    for c in sym_candidates:
        if c['word'] in used_sym: continue
        new_sav = (c['word_bytes'] - entry['symbol_bytes']) * c['train_count']
        if new_sav <= 0: continue
        gain = new_sav - entry['combined_savings']
        if gain >= 5 and gain > best_gain:
            best = c; best_gain = gain; best_sav = new_sav
    if best:
        sym_swaps.append({
            'old_word': entry['word'], 'new_word': best['word'],
            'symbol': entry['symbol'], 'old_savings': entry['combined_savings'],
            'new_savings': best_sav, 'net_gain': best_gain,
            'train_count': best['train_count'],
        })
        used_sym.add(best['word'])
        existing_words.add(best['word'])

print(f"  Symbol swaps: {len(sym_swaps)}")

# ============================================================
# PART 2: New train-only phrases (count >= 2, savings >= 10)
# ============================================================
print("PART 2: NEW TRAIN-ONLY PHRASES")

new_phrases = []
for phrase, train_count in train_ngrams.items():
    if phrase in existing_phrases: continue
    if val_ngrams.get(phrase, 0) > 0: continue
    if train_count < 2: continue
    phrase_bytes = len(phrase.encode('utf-8'))
    if phrase_bytes < 5: continue
    savings = (phrase_bytes - 2) * train_count
    if savings >= 10:
        new_phrases.append({
            'phrase': phrase, 'train_count': train_count, 'val_count': 0,
            'phrase_bytes': phrase_bytes, 'savings': savings, 'type': 'train_only',
        })

# Both-split phrases
both_phrases = []
for phrase, train_count in train_ngrams.items():
    if phrase in existing_phrases: continue
    val_count = val_ngrams.get(phrase, 0)
    if val_count == 0: continue
    phrase_bytes = len(phrase.encode('utf-8'))
    if phrase_bytes < 5: continue
    savings = (phrase_bytes - 2) * (train_count + val_count)
    if savings >= 10:
        both_phrases.append({
            'phrase': phrase, 'train_count': train_count, 'val_count': val_count,
            'phrase_bytes': phrase_bytes, 'savings': savings, 'type': 'both',
        })

both_phrases.sort(key=lambda x: -x['savings'])
new_phrases.sort(key=lambda x: -x['savings'])

all_new_phrases = both_phrases + new_phrases

# Get codes for phrases
phrase_codes = find_free_codes(len(all_new_phrases), all_used)
# Filter by actual savings
final_phrases = []
for i, entry in enumerate(all_new_phrases):
    if i >= len(phrase_codes): break
    code = phrase_codes[i]
    code_bytes = len(code.encode('utf-8'))
    total_count = entry['train_count'] + entry['val_count']
    net_sav = (entry['phrase_bytes'] - code_bytes) * total_count
    if net_sav >= 6:
        final_phrases.append((entry, code, net_sav))
        all_used.add(code)

print(f"  Both-split phrases: {len(both_phrases)}")
print(f"  Train-only phrases: {len(new_phrases)}")
print(f"  Final phrases (after filtering): {len(final_phrases)}")

# ============================================================
# PART 3: New symbol entries (train-only, 3-byte codes)
# ============================================================
print("PART 3: NEW TRAIN-ONLY SYMBOLS")

new_sym = []
for word, train_count in all_train_words.items():
    if word in existing_words: continue
    if all_val_words.get(word, 0) > 0: continue
    if train_count < 2: continue
    word_bytes = len(word.encode('utf-8'))
    if word_bytes < 4: continue
    savings_3byte = (word_bytes - 3) * train_count
    if savings_3byte >= 4:
        new_sym.append({
            'word': word, 'train_count': train_count, 'val_count': 0,
            'word_bytes': word_bytes, 'savings': savings_3byte,
        })

new_sym.sort(key=lambda x: -x['savings'])

sym_codes = find_free_codes(len(new_sym), all_used, byte_size=3)
final_sym = []
for i, entry in enumerate(new_sym):
    if i >= len(sym_codes): break
    code = sym_codes[i]
    all_used.add(code)
    final_sym.append((entry, code))
    existing_words.add(entry['word'])

print(f"  New train-only symbols: {len(final_sym)}")

# ============================================================
# PART 4: Val-only/both-split words
# ============================================================
print("PART 4: VAL WORDS")

val_words = []
for word, val_count in all_val_words.items():
    if word in existing_words: continue
    train_count = all_train_words.get(word, 0)
    word_bytes = len(word.encode('utf-8'))
    if word_bytes < 4: continue
    savings_3byte = (word_bytes - 3) * (val_count + train_count)
    val_savings = (word_bytes - 3) * val_count
    if val_savings >= 2 and savings_3byte >= 4:
        val_words.append({
            'word': word, 'train_count': train_count, 'val_count': val_count,
            'word_bytes': word_bytes, 'savings': savings_3byte,
        })

val_words.sort(key=lambda x: -x['savings'])

val_codes = find_free_codes(len(val_words), all_used, byte_size=3)
final_val = []
for i, entry in enumerate(val_words):
    if i >= len(val_codes): break
    code = val_codes[i]
    all_used.add(code)
    final_val.append((entry, code))

print(f"  Val words: {len(final_val)}")

# ============================================================
# PART 5: Val-containing phrases (SELECTIVE - max n-gram size 5, savings >= 8)
# ============================================================
print("PART 5: VAL PHRASES")

val_phrase_cands = []
for phrase, val_count in val_ngrams.items():
    if phrase in existing_phrases: continue
    # Skip if already added in part 2
    if any(e['phrase'] == phrase for e, _, _ in final_phrases): continue
    train_count = train_ngrams.get(phrase, 0)
    phrase_bytes = len(phrase.encode('utf-8'))
    if phrase_bytes < 5 or phrase_bytes > 40:  # cap phrase length
        continue
    total_count = train_count + val_count
    val_savings = (phrase_bytes - 3) * val_count
    total_savings = (phrase_bytes - 3) * total_count
    if val_savings >= 4 and total_savings >= 8:
        val_phrase_cands.append({
            'phrase': phrase, 'train_count': train_count, 'val_count': val_count,
            'phrase_bytes': phrase_bytes, 'savings': total_savings,
        })

val_phrase_cands.sort(key=lambda x: -x['savings'])
# Cap at 500 to avoid slowdown
val_phrase_cands = val_phrase_cands[:500]

val_phrase_codes = find_free_codes(len(val_phrase_cands), all_used, byte_size=3)
final_val_phrases = []
for i, entry in enumerate(val_phrase_cands):
    if i >= len(val_phrase_codes): break
    code = val_phrase_codes[i]
    code_bytes = len(code.encode('utf-8'))
    total_count = entry['train_count'] + entry['val_count']
    net_sav = (entry['phrase_bytes'] - code_bytes) * total_count
    if net_sav >= 4:
        final_val_phrases.append((entry, code, net_sav))
        all_used.add(code)

print(f"  Val phrases: {len(final_val_phrases)}")

# ============================================================
# APPLY ALL CHANGES
# ============================================================
print("\nAPPLYING CHANGES...")

config_path = Path(__file__).parent / "config.py"
content = config_path.read_text(encoding='utf-8')

# 1. Symbol swaps
swap_map = {s['old_word']: s for s in sym_swaps}
lines = content.split('\n')
new_lines = []
for line in lines:
    match = re.match(r'^(\s+)"([^"]+)":\s*("(?:[^"\\]|\\.)*")(,?\s*)(#.*)?$', line)
    if match:
        word = match.group(2)
        if word in swap_map:
            s = swap_map[word]
            indent = match.group(1)
            symbol_repr = match.group(3)
            comment = f"    # was '{word}', train_only, count={s['train_count']}, savings={s['new_savings']}"
            new_lines.append(f'{indent}"{s["new_word"]}": {symbol_repr},{comment}')
            continue
    new_lines.append(line)

content = '\n'.join(new_lines)

# 2. Insert new symbol entries before PHRASE_CODEBOOK
lines = content.split('\n')
sym_insert_idx = None
for i, line in enumerate(lines):
    if "PHRASE CODEBOOK" in line and "multi-word phrases" in line:
        for j in range(i-1, max(0, i-10), -1):
            if lines[j].strip() == "}":
                sym_insert_idx = j
                break
        break

sym_lines = ["    # exp 15: new train-only symbols"]
for entry, code in final_sym:
    sym_lines.append(f'    "{entry["word"]}": {repr(code)},  # savings={entry["savings"]}, train_only, count={entry["train_count"]}')

sym_lines2 = ["    # exp 15: val-containing symbols"]
for entry, code in final_val:
    tr = entry['train_count']; vl = entry['val_count']
    if tr > 0:
        sym_lines2.append(f'    "{entry["word"]}": {repr(code)},  # savings={entry["savings"]}, train={tr}, val={vl}')
    else:
        sym_lines2.append(f'    "{entry["word"]}": {repr(code)},  # savings={entry["savings"]}, val_only, count={vl}')

lines = lines[:sym_insert_idx] + sym_lines + sym_lines2 + lines[sym_insert_idx:]
content = '\n'.join(lines)

# 3. Insert new phrase entries before VOWEL STRIPPING
lines = content.split('\n')
phrase_insert_idx = None
for i, line in enumerate(lines):
    if "VOWEL STRIPPING PARAMETERS" in line:
        for j in range(i-1, max(0, i-10), -1):
            if lines[j].strip() == "}":
                phrase_insert_idx = j
                break
        break

phrase_lines = ["    # exp 15: new both-split + train-only phrases"]
for entry, code, net_sav in final_phrases:
    tr = entry['train_count']; vl = entry['val_count']
    if vl > 0:
        phrase_lines.append(f'    "{entry["phrase"]}": {repr(code)},  # savings={net_sav}, train={tr}, val={vl}')
    else:
        phrase_lines.append(f'    "{entry["phrase"]}": {repr(code)},  # savings={net_sav}, train_only, count={tr}')

phrase_lines.append("    # exp 15: val-containing phrases")
for entry, code, net_sav in final_val_phrases:
    tr = entry['train_count']; vl = entry['val_count']
    phrase_lines.append(f'    "{entry["phrase"]}": {repr(code)},  # savings={net_sav}, train={tr}, val={vl}')

lines = lines[:phrase_insert_idx] + phrase_lines + lines[phrase_insert_idx:]
content = '\n'.join(lines)

config_path.write_text(content, encoding='utf-8')

print(f"\nDone!")
print(f"  Symbol swaps: {len(sym_swaps)}")
print(f"  New train-only symbols: {len(final_sym)}")
print(f"  Val-containing symbols: {len(final_val)}")
print(f"  New phrases: {len(final_phrases)}")
print(f"  Val phrases: {len(final_val_phrases)}")
print(f"  Total new entries: {len(final_sym) + len(final_val) + len(final_phrases) + len(final_val_phrases)}")
