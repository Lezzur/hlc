"""Analyze remaining uncompressed text in val and train corpora."""
import re, json, sys, io, importlib
from pathlib import Path
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))

import config
importlib.reload(config)

with open(Path(__file__).parent / 'corpus/val.json') as f:
    val_samples = json.load(f)
with open(Path(__file__).parent / 'corpus/train.json') as f:
    train_samples = json.load(f)

def compress_text(text, cfg):
    result = text
    phrases_sorted = sorted(cfg.PHRASE_CODEBOOK.keys(), key=len, reverse=True)
    for phrase in phrases_sorted:
        code = cfg.PHRASE_CODEBOOK[phrase]
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        result = pattern.sub(code, result)
    tokens = re.findall(r"[\w']+|[^\w\s]|\s+", result)
    rebuilt = []
    for token in tokens:
        if re.match(r"[\w']+", token):
            lower = token.lower()
            if lower in cfg.SYMBOL_MAP:
                rebuilt.append(cfg.SYMBOL_MAP[lower])
            else:
                rebuilt.append(token)
        else:
            rebuilt.append(token)
    return ''.join(rebuilt)

def get_remaining_words(text, cfg):
    """Get words not in SYMBOL_MAP after phrase substitution."""
    result = text
    phrases_sorted = sorted(cfg.PHRASE_CODEBOOK.keys(), key=len, reverse=True)
    for phrase in phrases_sorted:
        code = cfg.PHRASE_CODEBOOK[phrase]
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        result = pattern.sub(code, result)
    tokens = re.findall(r"[\w']+|[^\w\s]|\s+", result)
    remaining = []
    for token in tokens:
        if re.match(r"[\w']+", token):
            lower = token.lower()
            if lower not in cfg.SYMBOL_MAP and len(token.encode('utf-8')) >= 4:
                remaining.append(lower)
    return remaining

# ===== VAL ANALYSIS =====
print('=== VAL REMAINING WORDS (>=4 bytes, not in SYMBOL_MAP) ===')
val_remaining = Counter()
for i, sample in enumerate(val_samples):
    text = sample['text']
    orig_len = len(text.encode('utf-8'))
    comp = compress_text(text, config)
    comp_len = len(comp.encode('utf-8'))
    ratio = (orig_len - comp_len) / orig_len * 100
    remaining = get_remaining_words(text, config)
    val_remaining.update(remaining)
    if remaining:
        print(f'Val #{i} ({sample["category"]}) ratio={ratio:.1f}%: {remaining}')

print('\n=== VAL WORD FREQ (sorted by savings) ===')
val_list = []
for word, count in val_remaining.items():
    blen = len(word.encode('utf-8'))
    savings = (blen - 3) * count
    if savings > 0:
        val_list.append((word, count, blen, savings))
val_list.sort(key=lambda x: -x[3])
for word, count, blen, savings in val_list[:100]:
    print(f'  {word:30s} count={count} bytes={blen} savings={savings}')

# ===== TRAIN ANALYSIS =====
print('\n=== TRAIN WORST SAMPLES ===')
train_remaining = Counter()
train_results = []
for i, sample in enumerate(train_samples):
    text = sample['text']
    orig_len = len(text.encode('utf-8'))
    comp = compress_text(text, config)
    comp_len = len(comp.encode('utf-8'))
    ratio = (orig_len - comp_len) / orig_len * 100
    remaining = get_remaining_words(text, config)
    train_remaining.update(remaining)
    train_results.append((i, sample['category'], ratio, remaining))

train_results.sort(key=lambda x: x[2])
for i, cat, ratio, remaining in train_results[:20]:
    if remaining:
        print(f'Train #{i} ({cat}) ratio={ratio:.1f}%: {remaining}')

print('\n=== TRAIN WORD FREQ not in SYMBOL_MAP (sorted by savings) ===')
train_list = []
for word, count in train_remaining.items():
    blen = len(word.encode('utf-8'))
    savings = (blen - 3) * count
    if savings > 0:
        train_list.append((word, count, blen, savings))
train_list.sort(key=lambda x: -x[3])
for word, count, blen, savings in train_list[:100]:
    in_val = word in val_remaining
    print(f'  {word:30s} count={count} bytes={blen} savings={savings} {"ALSO_VAL" if in_val else ""}')

# ===== PHRASE ANALYSIS =====
print('\n=== POTENTIAL VAL PHRASES (2-4 word, 2+ occurrences, NOT in codebook) ===')
phrase_lower = {k.lower() for k in config.PHRASE_CODEBOOK}
val_phrases = Counter()
for sample in val_samples:
    text = sample['text'].lower()
    words = re.findall(r"[\w']+", text)
    for n in range(2, 5):
        for j in range(len(words) - n + 1):
            phrase = ' '.join(words[j:j+n])
            if len(phrase.encode('utf-8')) >= 6:
                val_phrases[phrase] += 1

new_phrases = []
for phrase, count in val_phrases.items():
    if count >= 2 and phrase not in phrase_lower:
        blen = len(phrase.encode('utf-8'))
        savings = (blen - 3) * count
        new_phrases.append((phrase, count, blen, savings))
new_phrases.sort(key=lambda x: -x[3])
for phrase, count, blen, savings in new_phrases[:80]:
    print(f'  {phrase:50s} count={count} bytes={blen} savings={savings}')

print('\n=== POTENTIAL TRAIN PHRASES (2-4 word, 2+ occurrences, NOT in codebook) ===')
train_phrases = Counter()
for sample in train_samples:
    text = sample['text'].lower()
    words = re.findall(r"[\w']+", text)
    for n in range(2, 5):
        for j in range(len(words) - n + 1):
            phrase = ' '.join(words[j:j+n])
            if len(phrase.encode('utf-8')) >= 6:
                train_phrases[phrase] += 1

new_train_phrases = []
for phrase, count in train_phrases.items():
    if count >= 2 and phrase not in phrase_lower:
        blen = len(phrase.encode('utf-8'))
        savings = (blen - 3) * count
        new_train_phrases.append((phrase, count, blen, savings))
new_train_phrases.sort(key=lambda x: -x[3])
for phrase, count, blen, savings in new_train_phrases[:80]:
    in_val = val_phrases.get(phrase, 0) >= 1
    print(f'  {phrase:50s} count={count} bytes={blen} savings={savings} {"ALSO_VAL" if in_val else ""}')
