"""Analyze word frequencies across train.json and val.json corpus files."""
import json
import re
import unicodedata
from collections import Counter

# Load corpus
with open(r"F:\claude-code\claude_projects\hlc-release\autoresearch\corpus\train.json", "r", encoding="utf-8") as f:
    train_data = json.load(f)
with open(r"F:\claude-code\claude_projects\hlc-release\autoresearch\corpus\val.json", "r", encoding="utf-8") as f:
    val_data = json.load(f)

# Extract all text
train_text = " ".join(item["text"] for item in train_data)
val_text = " ".join(item["text"] for item in val_data)

# Tokenize: case-insensitive, pattern [\w']+
train_words = [w.lower() for w in re.findall(r"[\w']+", train_text)]
val_words = [w.lower() for w in re.findall(r"[\w']+", val_text)]

train_counts = Counter(train_words)
val_counts = Counter(val_words)

# Words in SYMBOL_MAP (from config.py)
import sys
sys.path.insert(0, r"F:\claude-code\claude_projects\hlc-release\autoresearch")
from config import SYMBOL_MAP, PHRASE_CODEBOOK

symbol_map_words = set(SYMBOL_MAP.keys())

# Get all words that appear in BOTH train and val
all_words = set(train_counts.keys()) & set(val_counts.keys())

# Exclude words already in SYMBOL_MAP
candidates = all_words - symbol_map_words

# Calculate byte_savings
results = []
for word in candidates:
    total = train_counts[word] + val_counts[word]
    word_bytes = len(word.encode('utf-8'))
    byte_savings = total * (word_bytes - 2)
    if byte_savings > 0:
        results.append({
            'word': word,
            'train_count': train_counts[word],
            'val_count': val_counts[word],
            'total_count': total,
            'word_bytes': word_bytes,
            'byte_savings': byte_savings,
        })

results.sort(key=lambda x: -x['byte_savings'])

# Write results to file
outpath = r"F:\claude-code\claude_projects\hlc-release\autoresearch\word_analysis_results.txt"
with open(outpath, "w", encoding="utf-8") as out:
    out.write(f"{'#':<4} {'Word':<25} {'Train':>6} {'Val':>6} {'Total':>6} {'Bytes':>5} {'Savings':>8}\n")
    out.write("-" * 65 + "\n")
    for i, r in enumerate(results[:200], 1):
        out.write(f"{i:<4} {r['word']:<25} {r['train_count']:>6} {r['val_count']:>6} {r['total_count']:>6} {r['word_bytes']:>5} {r['byte_savings']:>8}\n")

    out.write(f"\nTotal candidate words (in both train & val, not in SYMBOL_MAP, savings > 0): {len(results)}\n")

    # Part 2: Find 500 unused 2-byte Unicode characters
    # Exclude: control chars, combining marks, surrogates, format chars
    used_symbols = set(SYMBOL_MAP.values())
    used_phrase_codes = set(PHRASE_CODEBOOK.values())
    all_used = used_symbols | used_phrase_codes

    all_used_chars = set()
    for s in all_used:
        for ch in s:
            all_used_chars.add(ch)

    # Also exclude chars that appear in corpus text
    corpus_chars = set(train_text) | set(val_text)

    unused_2byte = []
    for cp in range(0x0080, 0x0800):
        ch = chr(cp)
        if ch in all_used_chars:
            continue
        if ch in corpus_chars:
            continue
        if len(ch.encode('utf-8')) != 2:
            continue
        # Skip C0/C1 control characters
        cat = unicodedata.category(ch)
        if cat.startswith('C'):  # Control, format, surrogate, private use, unassigned
            continue
        if cat.startswith('M'):  # Combining marks (Mn, Mc, Me)
            continue
        unused_2byte.append(ch)

    out.write(f"\n\nTotal unused safe 2-byte Unicode chars (U+0080-U+07FF, no control/combining): {len(unused_2byte)}\n")

    chars_500 = unused_2byte[:500]
    chars_string = ''.join(chars_500)
    out.write(f"\nUNUSED_2BYTE_CHARS = \"{chars_string}\"\n")
    out.write(f"\nLength of string: {len(chars_500)}\n")
    if chars_500:
        out.write(f"Codepoint range of first 500: U+{ord(chars_500[0]):04X} to U+{ord(chars_500[-1]):04X}\n")
    out.write(f"Codepoint range of all unused: U+{ord(unused_2byte[0]):04X} to U+{ord(unused_2byte[-1]):04X}\n")

    out.write(f"\nTotal used chars from SYMBOL_MAP + PHRASE_CODEBOOK: {len(all_used_chars)}\n")

    # Show codepoints of the 500 unused chars
    out.write(f"\nCodepoints of first 500 unused 2-byte chars:\n")
    for i, ch in enumerate(chars_500):
        if i > 0 and i % 20 == 0:
            out.write("\n")
        out.write(f"U+{ord(ch):04X} ")
    out.write("\n")

print(f"Results written to {outpath}")
