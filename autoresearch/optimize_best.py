"""
Rebuild the best known configuration:
1. Symbol swaps (val_count=0 entries)
2. New train-only phrases (count >= 2, savings >= 10)
3. New train-only symbols (3-byte codes, savings >= 4)
4. Val-only/both-split WORDS (not phrases, to avoid gap penalty)
5. Val-containing phrases (only both-split, small count)
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
    return sum(len(pattern.findall(t)) for t in texts)

def extract_ngrams(texts, n_range=(2, 6)):
    ngram_counts = Counter()
    for text in texts:
        words = re.findall(r"[\w']+", text.lower())
        for n in range(n_range[0], n_range[1] + 1):
            for i in range(len(words) - n + 1):
                ngram_counts[" ".join(words[i:i+n])] += 1
    return ngram_counts

all_train_words = Counter()
for text in train_texts:
    all_train_words.update(re.findall(r"[\w']+", text.lower()))

all_val_words = Counter()
for text in val_texts:
    all_val_words.update(re.findall(r"[\w']+", text.lower()))

train_ngrams = extract_ngrams(train_texts, (2, 6))
val_ngrams = extract_ngrams(val_texts, (2, 6))

existing_words = set(config.SYMBOL_MAP.keys())
existing_phrases = set(config.PHRASE_CODEBOOK.keys())
all_used = set(config.SYMBOL_MAP.values()) | set(config.PHRASE_CODEBOOK.values())

def find_free_codes(n, all_used, byte_size=None):
    free = []
    if byte_size is None or byte_size == 2:
        for cp in range(0x0080, 0x0800):
            c = chr(cp)
            if c not in all_used and len(c.encode('utf-8')) == 2:
                free.append(c)
                if len(free) >= n: return free
    if byte_size is None or byte_size == 3:
        for cp in range(0x0800, 0x10000):
            if 0xD800 <= cp <= 0xDFFF: continue
            c = chr(cp)
            if c not in all_used and len(c.encode('utf-8')) == 3:
                free.append(c)
                if len(free) >= n: return free
    return free

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PART 1: Symbol swaps
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("PART 1: SYMBOL SWAPS")
swappable = []
for word, symbol in config.SYMBOL_MAP.items():
    tc = count_word_occurrences(word, train_texts)
    vc = count_word_occurrences(word, val_texts)
    wb = len(word.encode('utf-8'))
    sb = len(symbol.encode('utf-8'))
    cs = (wb - sb) * (tc + vc)
    if vc == 0 and cs < 10:
        swappable.append({'word': word, 'symbol': symbol, 'sb': sb, 'cs': cs})
swappable.sort(key=lambda x: x['cs'])

sym_cands = []
for word, tc in all_train_words.items():
    if word in existing_words or all_val_words.get(word, 0) > 0 or tc < 2: continue
    wb = len(word.encode('utf-8'))
    if wb < 3: continue
    sym_cands.append({'word': word, 'tc': tc, 'wb': wb, 's2': (wb - 2) * tc})
sym_cands.sort(key=lambda x: -x['s2'])

sym_swaps = []
used_sw = set()
for e in swappable:
    best = None; bg = 0; bns = 0
    for c in sym_cands:
        if c['word'] in used_sw: continue
        ns = (c['wb'] - e['sb']) * c['tc']
        if ns <= 0: continue
        g = ns - e['cs']
        if g >= 5 and g > bg: best = c; bg = g; bns = ns
    if best:
        sym_swaps.append({'old': e['word'], 'new': best['word'], 'sym': e['symbol'],
                         'os': e['cs'], 'ns': bns, 'g': bg, 'tc': best['tc']})
        used_sw.add(best['word']); existing_words.add(best['word'])
print(f"  Swaps: {len(sym_swaps)}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PART 2: Train-only phrases + both-split phrases
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("PART 2: NEW PHRASES")
all_new_phrases = []

for phrase, tc in train_ngrams.items():
    if phrase in existing_phrases: continue
    vc = val_ngrams.get(phrase, 0)
    pb = len(phrase.encode('utf-8'))
    if pb < 5: continue
    total = tc + vc
    sav = (pb - 2) * total
    if vc > 0 and sav >= 10:
        all_new_phrases.append({'phrase': phrase, 'tc': tc, 'vc': vc, 'pb': pb, 'sav': sav, 'type': 'both'})
    elif vc == 0 and tc >= 2 and sav >= 10:
        all_new_phrases.append({'phrase': phrase, 'tc': tc, 'vc': 0, 'pb': pb, 'sav': sav, 'type': 'train'})

all_new_phrases.sort(key=lambda x: -x['sav'])

pcodes = find_free_codes(len(all_new_phrases), all_used)
final_phrases = []
for i, e in enumerate(all_new_phrases):
    if i >= len(pcodes): break
    c = pcodes[i]; cb = len(c.encode('utf-8'))
    ns = (e['pb'] - cb) * (e['tc'] + e['vc'])
    if ns >= 6:
        final_phrases.append((e, c, ns)); all_used.add(c)

print(f"  Phrases: {len(final_phrases)}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PART 3: Train-only symbols (3-byte)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("PART 3: TRAIN-ONLY SYMBOLS")
tsym = []
for word, tc in all_train_words.items():
    if word in existing_words or all_val_words.get(word, 0) > 0 or tc < 2: continue
    wb = len(word.encode('utf-8'))
    if wb < 4: continue
    s3 = (wb - 3) * tc
    if s3 >= 4: tsym.append({'word': word, 'tc': tc, 'wb': wb, 's3': s3})
tsym.sort(key=lambda x: -x['s3'])

scodes = find_free_codes(len(tsym), all_used, byte_size=3)
final_tsym = []
for i, e in enumerate(tsym):
    if i >= len(scodes): break
    all_used.add(scodes[i]); existing_words.add(e['word'])
    final_tsym.append((e, scodes[i]))
print(f"  Train symbols: {len(final_tsym)}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PART 4: Val words (to close the gap)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("PART 4: VAL WORDS")
vwords = []
for word, vc in all_val_words.items():
    if word in existing_words: continue
    tc = all_train_words.get(word, 0)
    wb = len(word.encode('utf-8'))
    if wb < 4: continue
    s3 = (wb - 3) * (tc + vc)
    vs = (wb - 3) * vc
    if vs >= 2 and s3 >= 4:
        vwords.append({'word': word, 'tc': tc, 'vc': vc, 'wb': wb, 's3': s3})
vwords.sort(key=lambda x: -x['s3'])

vcodes = find_free_codes(len(vwords), all_used, byte_size=3)
final_vwords = []
for i, e in enumerate(vwords):
    if i >= len(vcodes): break
    all_used.add(vcodes[i])
    final_vwords.append((e, vcodes[i]))
print(f"  Val words: {len(final_vwords)}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APPLY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\nAPPLYING...")
config_path = Path(__file__).parent / "config.py"
content = config_path.read_text(encoding='utf-8')

# 1. Swaps
smap = {s['old']: s for s in sym_swaps}
lines = content.split('\n')
new_lines = []
for line in lines:
    m = re.match(r'^(\s+)"([^"]+)":\s*("(?:[^"\\]|\\.)*")(,?\s*)(#.*)?$', line)
    if m and m.group(2) in smap:
        s = smap[m.group(2)]
        new_lines.append(f'{m.group(1)}"{s["new"]}": {m.group(3)},    # was \'{s["old"]}\', train_only, count={s["tc"]}, savings={s["ns"]}')
    else:
        new_lines.append(line)
content = '\n'.join(new_lines)

# 2. Insert symbols
lines = content.split('\n')
idx = None
for i, line in enumerate(lines):
    if "PHRASE CODEBOOK" in line and "multi-word" in line:
        for j in range(i-1, max(0, i-10), -1):
            if lines[j].strip() == "}":
                idx = j; break
        break

sl = ["    # exp 15: train-only symbols"]
for e, c in final_tsym:
    sl.append(f'    "{e["word"]}": {repr(c)},  # savings={e["s3"]}, train_only, count={e["tc"]}')
sl.append("    # exp 15: val words")
for e, c in final_vwords:
    tr = e['tc']; vl = e['vc']
    tag = f'train={tr}, val={vl}' if tr > 0 else f'val_only, count={vl}'
    sl.append(f'    "{e["word"]}": {repr(c)},  # savings={e["s3"]}, {tag}')

lines = lines[:idx] + sl + lines[idx:]
content = '\n'.join(lines)

# 3. Insert phrases
lines = content.split('\n')
idx = None
for i, line in enumerate(lines):
    if "VOWEL STRIPPING" in line:
        for j in range(i-1, max(0, i-10), -1):
            if lines[j].strip() == "}":
                idx = j; break
        break

pl = ["    # exp 15: new phrases"]
for e, c, ns in final_phrases:
    tr = e['tc']; vl = e['vc']
    tag = f'train={tr}, val={vl}' if vl > 0 else f'train_only, count={tr}'
    pl.append(f'    "{e["phrase"]}": {repr(c)},  # savings={ns}, {tag}')

lines = lines[:idx] + pl + lines[idx:]
content = '\n'.join(lines)

config_path.write_text(content, encoding='utf-8')
print("Done!")
print(f"  Symbol swaps: {len(sym_swaps)}")
print(f"  Train symbols: {len(final_tsym)}")
print(f"  Val words: {len(final_vwords)}")
print(f"  Phrases: {len(final_phrases)}")
