"""
Deep analysis v4: What exactly is causing the train/val gap?
- Compare byte-level compression stats
- Look at remaining text after compression
- Check if there are common PATTERNS (not exact phrases) that could help
- Look at character-level remaining bytes breakdown
"""

import json
import re
import sys
import importlib
from pathlib import Path
from collections import Counter

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

corpus_dir = Path(__file__).parent / "corpus"
with open(corpus_dir / "train.json") as f:
    train_samples = json.load(f)
with open(corpus_dir / "val.json") as f:
    val_samples = json.load(f)

sys.path.insert(0, str(Path(__file__).parent))
import config
importlib.reload(config)

symbol_words = set(config.SYMBOL_MAP.keys())
existing_phrases = {p.lower() for p in config.PHRASE_CODEBOOK.keys()}

VOWELS_SET = set("aeiouAEIOU")

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
    result = "".join(rebuilt)
    tokens = re.findall(r"[\w']+|[^\w\s]|\s+", result)
    rebuilt = []
    for token in tokens:
        if re.match(r"[a-zA-Z]+$", token):
            lower = token.lower()
            if lower in cfg.PROTECTED_SHORTHAND:
                rebuilt.append(token)
                continue
            if lower in cfg.VOWEL_STRIP_EXCEPTIONS:
                rebuilt.append(token)
                continue
            if len(token) < cfg.MIN_VOWEL_STRIP_LENGTH:
                rebuilt.append(token)
                continue
            if len(token) == 1:
                rebuilt.append(token)
                continue
            first = token[0]
            last = token[-1]
            middle = token[1:-1]
            stripped = "".join(c for c in middle if c not in VOWELS_SET)
            if stripped:
                rebuilt.append(first + stripped + last)
            else:
                rebuilt.append(token)
        else:
            rebuilt.append(token)
    result = "".join(rebuilt)
    return result

# ═══════════════════════════════════════════════════════════
# PART 1: Train vs Val summary statistics
# ═══════════════════════════════════════════════════════════

print("=" * 100)
print("TRAIN vs VAL COMPRESSION COMPARISON")
print("=" * 100)

def analyze_split(samples, name):
    total_orig = 0
    total_comp = 0
    ratios = []
    all_remaining_words = Counter()
    all_remaining_bytes = 0
    all_symbol_bytes = 0
    all_space_bytes = 0
    all_punct_bytes = 0
    all_short_word_bytes = 0

    for sample_item in samples:
        text = sample_item["text"]
        orig = len(text.encode("utf-8"))
        comp = compress_text(text, config)
        comp_bytes = len(comp.encode("utf-8"))
        total_orig += orig
        total_comp += comp_bytes
        ratios.append((orig - comp_bytes) / orig * 100)

        # Analyze what's in the compressed output
        for ch in comp:
            b = len(ch.encode("utf-8"))
            if ch.isspace():
                all_space_bytes += b
            elif ch.isalpha():
                pass  # counted below in words
            elif ord(ch) < 128 and not ch.isalnum():
                all_punct_bytes += b

        # Count remaining text words
        tokens = re.findall(r"[a-zA-Z]+", comp)
        for t in tokens:
            tb = len(t.encode("utf-8"))
            all_remaining_bytes += tb
            all_remaining_words[t.lower()] += 1

    ratio = (total_orig - total_comp) / total_orig * 100

    print(f"\n{name}:")
    print(f"  Total original bytes: {total_orig}")
    print(f"  Total compressed bytes: {total_comp}")
    print(f"  Overall compression: {ratio:.1f}%")
    print(f"  Avg per-sample ratio: {sum(ratios)/len(ratios):.1f}%")
    print(f"  Min sample ratio: {min(ratios):.1f}%")
    print(f"  Max sample ratio: {max(ratios):.1f}%")
    print(f"  Remaining text words (unique): {len(all_remaining_words)}")
    print(f"  Remaining text bytes: {all_remaining_bytes}")

    return total_orig, total_comp, all_remaining_words

train_orig, train_comp, train_remaining = analyze_split(
    [{"text": s["text"]} for s in train_samples], "TRAIN")
val_orig, val_comp, val_remaining = analyze_split(
    [{"text": s["text"]} for s in val_samples], "VAL")


# ═══════════════════════════════════════════════════════════
# PART 2: What remaining words are unique to train?
# These are the main driver of the gap.
# ═══════════════════════════════════════════════════════════

print("\n\n" + "=" * 100)
print("REMAINING WORDS ANALYSIS (post-compression)")
print("=" * 100)

# Words remaining in train but NOT in val (compressed forms)
train_only_remaining = Counter()
shared_remaining = Counter()

for word, count in train_remaining.items():
    if word in val_remaining:
        shared_remaining[word] += count
    else:
        train_only_remaining[word] += count

val_only_remaining = Counter()
for word, count in val_remaining.items():
    if word not in train_remaining:
        val_only_remaining[word] += count

train_only_bytes = sum(len(w.encode("utf-8")) * c for w, c in train_only_remaining.items())
val_only_bytes = sum(len(w.encode("utf-8")) * c for w, c in val_only_remaining.items())
shared_bytes_train = sum(len(w.encode("utf-8")) * c for w, c in shared_remaining.items())

print(f"\nTrain-only remaining words: {len(train_only_remaining)} unique, {sum(train_only_remaining.values())} occurrences, {train_only_bytes} bytes")
print(f"Val-only remaining words: {len(val_only_remaining)} unique, {sum(val_only_remaining.values())} occurrences, {val_only_bytes} bytes")
print(f"Shared remaining words: {len(shared_remaining)} unique")

print(f"\nTop 30 train-only remaining words (by bytes):")
train_only_by_bytes = [(w, c, len(w.encode("utf-8")) * c) for w, c in train_only_remaining.items()]
train_only_by_bytes.sort(key=lambda x: -x[2])

print(f"{'#':>3} {'Word':<25} {'Count':>5} {'Bytes':>6}")
print("-" * 45)
for i, (w, c, b) in enumerate(train_only_by_bytes[:30]):
    print(f"{i+1:>3} {w:<25} {c:>5} {b:>6}")


# ═══════════════════════════════════════════════════════════
# PART 3: Check if short (1-3 letter) words that aren't in
# SYMBOL_MAP have enough cross-corpus frequency to be worth adding
# ═══════════════════════════════════════════════════════════

print("\n\n" + "=" * 100)
print("SHORT WORDS (1-3 chars) NOT IN SYMBOL_MAP — check cross-corpus frequency")
print("=" * 100)

train_words_full = Counter()
for sample in train_samples:
    for w in re.findall(r"[a-z']+", sample["text"].lower()):
        train_words_full[w] += 1

val_words_full = Counter()
for sample in val_samples:
    for w in re.findall(r"[a-z']+", sample["text"].lower()):
        val_words_full[w] += 1

short_candidates = []
for word, tc in train_words_full.items():
    if word in symbol_words:
        continue
    if len(word) > 3:
        continue
    vc = val_words_full.get(word, 0)
    wb = len(word.encode("utf-8"))
    # For short words, symbol saves (wb - symbol_bytes)
    # But symbols are typically 1-2 bytes for single char
    # A 3-letter word -> 1 byte symbol saves 2 bytes per occurrence
    if wb <= 1:
        continue
    total = tc + vc
    savings = total * (wb - 1)  # 1-byte symbol
    short_candidates.append({
        "word": word,
        "train": tc,
        "val": vc,
        "bytes": wb,
        "savings": savings,
    })

short_candidates.sort(key=lambda x: -x["savings"])

print(f"\n{'#':>3} {'Word':<10} {'Train':>5} {'Val':>4} {'Bytes':>5} {'Savings':>7}")
print("-" * 40)
for i, w in enumerate(short_candidates[:30]):
    marker = " <-- in val" if w["val"] > 0 else ""
    print(f"{i+1:>3} {w['word']:<10} {w['train']:>5} {w['val']:>4} "
          f"{w['bytes']:>5} {w['savings']:>7}{marker}")


# ═══════════════════════════════════════════════════════════
# PART 4: Detailed breakdown of what bytes are in compressed output
# ═══════════════════════════════════════════════════════════

print("\n\n" + "=" * 100)
print("BYTE BREAKDOWN OF COMPRESSED OUTPUT")
print("=" * 100)

def byte_breakdown(samples, name):
    symbol_bytes = 0
    space_bytes = 0
    punct_bytes = 0
    remaining_word_bytes = 0
    short_word_bytes = 0  # <= 3 char words
    total_bytes = 0

    for sample_item in samples:
        text = sample_item["text"]
        comp = compress_text(text, config)

        # tokenize
        tokens = re.findall(r"[\w']+|[^\w\s]|\s+", comp)
        for token in tokens:
            tb = len(token.encode("utf-8"))
            total_bytes += tb

            if token.isspace() or (len(token) > 0 and token[0] == ' '):
                space_bytes += tb
            elif re.match(r"^[a-zA-Z]+$", token):
                remaining_word_bytes += tb
                if len(token) <= 3:
                    short_word_bytes += tb
            elif re.match(r"^[a-zA-Z']+$", token):
                remaining_word_bytes += tb
            elif len(token) == 1 and ord(token) > 127:
                symbol_bytes += tb
            elif len(token) == 1 and not token.isalnum() and not token.isspace():
                # Could be ASCII symbol OR punctuation
                if token in config.SYMBOL_MAP.values() or token in config.PHRASE_CODEBOOK.values():
                    symbol_bytes += tb
                else:
                    punct_bytes += tb
            else:
                # Multi-byte symbol or other
                symbol_bytes += tb

    print(f"\n{name}:")
    print(f"  Total compressed bytes:   {total_bytes}")
    print(f"  Space bytes:              {space_bytes} ({space_bytes/total_bytes*100:.1f}%)")
    print(f"  Remaining word bytes:     {remaining_word_bytes} ({remaining_word_bytes/total_bytes*100:.1f}%)")
    print(f"    of which <=3 char:      {short_word_bytes} ({short_word_bytes/total_bytes*100:.1f}%)")
    print(f"  Symbol/code bytes:        {symbol_bytes} ({symbol_bytes/total_bytes*100:.1f}%)")
    print(f"  Punctuation bytes:        {punct_bytes} ({punct_bytes/total_bytes*100:.1f}%)")

byte_breakdown([{"text": s["text"]} for s in train_samples], "TRAIN")
byte_breakdown([{"text": s["text"]} for s in val_samples], "VAL")


# ═══════════════════════════════════════════════════════════
# PART 5: Words in val but NOT train (check both directions)
# ═══════════════════════════════════════════════════════════

print("\n\n" + "=" * 100)
print("CROSS-CHECK: Phrases that appear 1+ train, 1+ val (ANY overlap)")
print("Looking for phrases where combined count >= 3, not in codebook")
print("=" * 100)

def extract_ngrams(text, min_n=2, max_n=5):
    words = re.findall(r"[a-z']+", text.lower())
    ngrams = Counter()
    for n in range(min_n, max_n + 1):
        for i in range(len(words) - n + 1):
            phrase = " ".join(words[i:i+n])
            ngrams[phrase] += 1
    return ngrams

train_ng = Counter()
for s in train_samples:
    train_ng += extract_ngrams(s["text"])

val_ng = Counter()
for s in val_samples:
    val_ng += extract_ngrams(s["text"])

# Relaxed criteria: 1+ in each, total >= 3
relaxed = []
for phrase, tc in train_ng.items():
    if tc < 1:
        continue
    vc = val_ng.get(phrase, 0)
    if vc < 1:
        continue
    total = tc + vc
    if total < 3:
        continue
    if phrase in existing_phrases:
        continue

    pb = len(phrase.encode("utf-8"))
    words = phrase.split()
    # Estimate compressed size
    est = 0
    for w in words:
        if w in symbol_words:
            est += len(config.SYMBOL_MAP[w].encode("utf-8"))
        else:
            wb = len(w.encode("utf-8"))
            est += max(2, int(wb * 0.65)) if len(w) >= 4 else wb
    est += len(words) - 1

    savings = total * max(0, est - 2)
    if savings <= 0:
        continue

    relaxed.append({
        "phrase": phrase,
        "train": tc,
        "val": vc,
        "total": total,
        "bytes": pb,
        "est": est,
        "savings": savings,
    })

relaxed.sort(key=lambda x: -x["savings"])

print(f"\nFound {len(relaxed)} candidates with train>=1, val>=1, total>=3")
print(f"\n{'#':>3} {'Phrase':<50} {'Tr':>3} {'Vl':>3} {'Tot':>3} {'Bytes':>5} {'Est':>4} {'Savings':>7}")
print("-" * 100)
for i, c in enumerate(relaxed[:100]):
    print(f"{i+1:>3} {c['phrase']:<50} {c['train']:>3} {c['val']:>3} {c['total']:>3} "
          f"{c['bytes']:>5} {c['est']:>4} {c['savings']:>7}")
