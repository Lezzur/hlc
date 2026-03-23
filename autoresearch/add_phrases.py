"""
Add high-value phrases to PHRASE_CODEBOOK.
Generates unique 2-byte Unicode code points for each new entry.
Adds both-split phrases first (best ROI), then train-only.
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

existing_phrases = set(config.PHRASE_CODEBOOK.keys())
existing_symbols = set(config.SYMBOL_MAP.values())
existing_codes = set(config.PHRASE_CODEBOOK.values())
all_used = existing_symbols | existing_codes

# Extract n-grams
def extract_ngrams(texts, n_range=(2, 6)):
    ngram_counts = Counter()
    for text in texts:
        words = re.findall(r"[\w']+", text.lower())
        for n in range(n_range[0], n_range[1] + 1):
            for i in range(len(words) - n + 1):
                ngram = " ".join(words[i:i+n])
                ngram_counts[ngram] += 1
    return ngram_counts

train_ngrams = extract_ngrams(train_texts, (2, 6))
val_ngrams = extract_ngrams(val_texts, (2, 6))

# Find available 2-byte Unicode code points
def find_free_codes(n, all_used):
    """Find n unused 2-byte Unicode code points."""
    free = []
    # Use Georgian, Armenian, Syriac, Thaana ranges and others
    ranges = [
        (0x10A0, 0x10FF),  # Georgian
        (0x1100, 0x11FF),  # Hangul Jamo
        (0x1200, 0x137F),  # Ethiopic
        (0x13A0, 0x13FF),  # Cherokee
        (0x1400, 0x167F),  # Canadian Aboriginal
        (0x1680, 0x169F),  # Ogham
        (0x16A0, 0x16FF),  # Runic
        (0x1700, 0x171F),  # Tagalog
        (0x1720, 0x173F),  # Hanunoo
        (0x1740, 0x175F),  # Buhid
        (0x1760, 0x177F),  # Tagbanwa
        (0x1780, 0x17FF),  # Khmer
        (0x1800, 0x18AF),  # Mongolian
        (0x1900, 0x194F),  # Limbu
        (0x1950, 0x197F),  # Tai Le
        (0x1980, 0x19DF),  # New Tai Lue
        (0x19E0, 0x19FF),  # Khmer Symbols
        (0x1A00, 0x1A1F),  # Buginese
    ]
    for start, end in ranges:
        for cp in range(start, end + 1):
            c = chr(cp)
            if c in all_used:
                continue
            # Check it's a valid character and 2 bytes in UTF-8
            # Actually, these are 3-byte in UTF-8 (U+0800 to U+FFFF are 3 bytes)
            # Let me find 2-byte ones (U+0080 to U+07FF)
            pass

    # 2-byte UTF-8: U+0080 to U+07FF
    for cp in range(0x0080, 0x0800):
        c = chr(cp)
        if c in all_used:
            continue
        b = c.encode('utf-8')
        if len(b) == 2:
            free.append(c)
            if len(free) >= n:
                return free

    # If not enough 2-byte, use 3-byte
    for cp in range(0x0800, 0x10000):
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
# Collect both-split phrases (highest ROI)
# ============================================================

both_phrases = []
for phrase, train_count in train_ngrams.items():
    if phrase in existing_phrases:
        continue
    val_count = val_ngrams.get(phrase, 0)
    if val_count == 0:
        continue
    phrase_bytes = len(phrase.encode('utf-8'))
    if phrase_bytes < 5:
        continue
    both_phrases.append({
        'phrase': phrase,
        'train_count': train_count,
        'val_count': val_count,
        'phrase_bytes': phrase_bytes,
        'savings_2byte': (phrase_bytes - 2) * (train_count + val_count),
        'type': 'both',
    })

both_phrases.sort(key=lambda x: -x['savings_2byte'])

# ============================================================
# Collect train-only phrases (savings >= 20)
# ============================================================

train_only_phrases = []
for phrase, train_count in train_ngrams.items():
    if phrase in existing_phrases:
        continue
    val_count = val_ngrams.get(phrase, 0)
    if val_count > 0:
        continue
    if train_count < 2:
        continue
    phrase_bytes = len(phrase.encode('utf-8'))
    if phrase_bytes < 5:
        continue
    savings = (phrase_bytes - 2) * train_count
    if savings >= 20:
        train_only_phrases.append({
            'phrase': phrase,
            'train_count': train_count,
            'val_count': 0,
            'phrase_bytes': phrase_bytes,
            'savings_2byte': savings,
            'type': 'train_only',
        })

train_only_phrases.sort(key=lambda x: -x['savings_2byte'])

# ============================================================
# Determine how many to add
# We need to be careful about gap. Both-split are safe.
# Train-only increase gap but score still improves if gap stays under 8.
# ============================================================

# Add all both-split phrases with savings >= 10
new_entries = []
for p in both_phrases:
    if p['savings_2byte'] >= 10:
        new_entries.append(p)

print(f"Both-split phrases to add: {len(new_entries)}")

# Add top train-only phrases (be conservative -- keep gap manageable)
# Add top 100 train-only phrases
train_to_add = train_only_phrases[:100]
new_entries.extend(train_to_add)

print(f"Train-only phrases to add: {len(train_to_add)}")
print(f"Total new phrase entries: {len(new_entries)}")

# ============================================================
# Assign codes and generate config additions
# ============================================================

codes = find_free_codes(len(new_entries), all_used)
if len(codes) < len(new_entries):
    print(f"WARNING: Only {len(codes)} free codes available, need {len(new_entries)}")
    new_entries = new_entries[:len(codes)]

config_lines = []
config_lines.append("    # exp 15: new both-split and train-only phrases")
for i, entry in enumerate(new_entries):
    code = codes[i]
    phrase = entry['phrase']
    savings = entry['savings_2byte']
    tr = entry['train_count']
    vl = entry['val_count']
    ptype = entry['type']
    code_repr = repr(code)

    if ptype == 'both':
        comment = f"# savings={savings}, train={tr}, val={vl}"
    else:
        comment = f"# savings={savings}, train_only, count={tr}"

    config_lines.append(f'    "{phrase}": {code_repr},  {comment}')

# ============================================================
# Apply to config.py
# ============================================================

config_path = Path(__file__).parent / "config.py"
content = config_path.read_text(encoding='utf-8')

# Find the end of PHRASE_CODEBOOK -- insert before the closing brace
# Find the line with just "}" that closes PHRASE_CODEBOOK
# The PHRASE_CODEBOOK ends before the VOWEL_STRIP section

# Find "VOWEL STRIPPING PARAMETERS" and insert before it
insert_marker = "# ═══════════════════════════════════════════════════════════\n# VOWEL STRIPPING PARAMETERS"

# Find the closing brace of PHRASE_CODEBOOK
# It should be right before the vowel stripping section
lines = content.split('\n')
insert_idx = None
for i, line in enumerate(lines):
    if "VOWEL STRIPPING PARAMETERS" in line:
        # Go back to find the closing "}"
        for j in range(i-1, max(0, i-10), -1):
            if lines[j].strip() == "}":
                insert_idx = j
                break
        break

if insert_idx is None:
    print("ERROR: Could not find insertion point in config.py")
    sys.exit(1)

# Insert new entries before the closing brace
new_lines = lines[:insert_idx] + config_lines + lines[insert_idx:]
new_content = '\n'.join(new_lines)

config_path.write_text(new_content, encoding='utf-8')
print(f"\nInserted {len(config_lines)} lines at line {insert_idx}")
print("Config.py updated successfully.")

# Update the all_used set
for i, entry in enumerate(new_entries):
    all_used.add(codes[i])

print(f"\nSample additions:")
for line in config_lines[:20]:
    print(f"  {line.strip()}")
