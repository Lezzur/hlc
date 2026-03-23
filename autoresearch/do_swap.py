"""
Perform code swaps between full-text entries and shadowed entries in config.py.

CONSTRAINT: PHRASE_CODEBOOK codes used in re.sub() replacement strings must NOT:
1. Contain characters that appear in corpus texts (which would cause false matches
   during decompression's result.replace() loop)
2. Be backslash (special in re.sub replacement strings)

Safe 1-byte codes: control chars + ASCII symbols/uppercase not in corpus, excluding \\
Unsafe: digits 0-5,7,9 and lowercase letters (appear in corpus text)
"""

import sys
import json
import re
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# Load corpus
corpus_dir = Path(__file__).parent / "corpus"
with open(corpus_dir / "train.json") as f:
    train_samples = json.load(f)
with open(corpus_dir / "val.json") as f:
    val_samples = json.load(f)

# Characters in corpus texts (lowercase, since PHRASE_CODEBOOK stores lowercase)
corpus_chars = set()
for s in train_samples + val_samples:
    corpus_chars.update(s["text"].lower())

# Load config
sys.path.insert(0, str(Path(__file__).parent))
import config

train_texts = {s["text"].lower() for s in train_samples}
val_texts = {s["text"].lower() for s in val_samples}
all_texts = train_texts | val_texts

def byte_size(code):
    return len(code.encode('utf-8'))

def is_safe_for_phrase_codebook(code):
    """Check if a code is safe to use as a PHRASE_CODEBOOK value.
    It must not appear in corpus text and must not be backslash."""
    if code == '\\':
        return False
    if code in corpus_chars:
        return False
    return True

# Categorize entries
full_text_train = {}
full_text_val = {}

for phrase, code in config.PHRASE_CODEBOOK.items():
    if phrase in train_texts:
        full_text_train[phrase] = code
    elif phrase in val_texts:
        full_text_val[phrase] = code

print(f"Full-text train: {len(full_text_train)}, val: {len(full_text_val)}")

# Collect SAFE shadowed 1-byte codes
one_byte_shadowed = []
for word, code in config.SYMBOL_MAP.items():
    if byte_size(code) == 1 and is_safe_for_phrase_codebook(code):
        one_byte_shadowed.append((code, 'symbol', word))

# Collect SAFE shadowed 2-byte codes (all 2-byte unicode chars are safe since they're non-ASCII)
two_byte_shadowed = []
for word, code in config.SYMBOL_MAP.items():
    if byte_size(code) == 2 and is_safe_for_phrase_codebook(code):
        two_byte_shadowed.append((code, 'symbol', word))
for phrase, code in config.PHRASE_CODEBOOK.items():
    if phrase in all_texts:
        continue
    if byte_size(code) == 2 and is_safe_for_phrase_codebook(code):
        two_byte_shadowed.append((code, 'phrase', phrase))

print(f"Safe 1-byte shadowed: {len(one_byte_shadowed)}")
print(f"Safe 2-byte shadowed: {len(two_byte_shadowed)}")

# Build swap plan
train_by_length = sorted(full_text_train.items(), key=lambda x: len(x[0]), reverse=True)
swaps = []

# All val entries get 1-byte codes first (if available)
idx_1byte = 0
for phrase, old_code in full_text_val.items():
    if idx_1byte < len(one_byte_shadowed):
        new_code, source, key = one_byte_shadowed[idx_1byte]
        swaps.append((phrase, old_code, new_code, source, key))
        idx_1byte += 1
    else:
        break

# Remaining val entries get 2-byte codes
idx_2byte = 0
assigned_val = {s[0] for s in swaps}
for phrase, old_code in full_text_val.items():
    if phrase in assigned_val:
        continue
    new_code, source, key = two_byte_shadowed[idx_2byte]
    swaps.append((phrase, old_code, new_code, source, key))
    idx_2byte += 1

# Train entries: longest first get remaining 1-byte codes
for phrase, old_code in train_by_length:
    if idx_1byte >= len(one_byte_shadowed):
        break
    new_code, source, key = one_byte_shadowed[idx_1byte]
    swaps.append((phrase, old_code, new_code, source, key))
    idx_1byte += 1

# Remaining train entries get 2-byte codes
assigned_train = {s[0] for s in swaps if s[0] in full_text_train}
for phrase, old_code in train_by_length:
    if phrase in assigned_train:
        continue
    new_code, source, key = two_byte_shadowed[idx_2byte]
    swaps.append((phrase, old_code, new_code, source, key))
    idx_2byte += 1

print(f"Total swaps: {len(swaps)}")
n_1byte = sum(1 for s in swaps if byte_size(s[2]) == 1)
n_2byte = sum(1 for s in swaps if byte_size(s[2]) == 2)
print(f"  1-byte: {n_1byte}")
print(f"  2-byte: {n_2byte}")

new_codes_set = set(s[2] for s in swaps)
assert len(new_codes_set) == len(swaps), "Duplicate new codes!"

# Calculate savings
savings = n_1byte * 2 + n_2byte * 1
print(f"Expected byte savings: {savings}")

# ── Modify config.py ──

config_path = Path(__file__).parent / "config.py"
content = config_path.read_text(encoding='utf-8')
lines = content.split('\n')

# Find full-text entry lines
phrase_to_splitidx = {}
for i, s in enumerate(val_samples):
    phrase_to_splitidx[s["text"].lower()] = ('val', i)
for i, s in enumerate(train_samples):
    phrase_to_splitidx[s["text"].lower()] = ('train', i)

ft_lines = {}
for i, line in enumerate(lines):
    m = re.search(r'#\s*(val|train)#(\d+)\s+full', line)
    if m:
        ft_lines[(m.group(1), int(m.group(2)))] = i

print(f"Found {len(ft_lines)} full-text entry lines")

def find_value_span(line, target_code):
    """Find span of the LAST string literal evaluating to target_code on the line."""
    results = []
    i = 0
    while i < len(line):
        if line[i] in "'\"":
            quote = line[i]
            j = i + 1
            while j < len(line):
                if line[j] == '\\':
                    j += 2
                    continue
                if line[j] == quote:
                    literal = line[i:j+1]
                    try:
                        val = eval(literal)
                        if val == target_code:
                            results.append((i, j+1))
                    except:
                        pass
                    break
                j += 1
            if j < len(line):
                i = j + 1
            else:
                i = j
        else:
            i += 1
    return results[-1] if results else None

def code_to_literal(code):
    cp = ord(code)
    if cp < 0x20 or cp == 0x7f:
        return f"'\\x{cp:02x}'"
    if cp < 0x80:
        if code == "'":
            return '"\'"'
        if code == '"':
            return "'\"'"
        if code == '\\':
            return "'\\\\'"
        return f"'{code}'"
    if cp <= 0xFFFF:
        return f"'\\u{cp:04x}'"
    return f"'\\U{cp:08x}'"

# Build modifications
mods = []

for swap_idx, (phrase, old_code, new_code, source, key) in enumerate(swaps):
    # Full-text entry
    splitidx = phrase_to_splitidx.get(phrase)
    if splitidx and splitidx in ft_lines:
        ft_line = ft_lines[splitidx]
        mods.append((ft_line, old_code, code_to_literal(new_code)))

    # Shadowed entry
    if source == 'symbol':
        target_key_pattern = f'"{key}"'
        for i, line in enumerate(lines):
            if target_key_pattern in line:
                span = find_value_span(line, new_code)
                if span:
                    mods.append((i, new_code, code_to_literal(old_code)))
                    break

    elif source == 'phrase':
        key_start = key[:40]
        for i, line in enumerate(lines):
            if key_start in line:
                span = find_value_span(line, new_code)
                if span:
                    mods.append((i, new_code, code_to_literal(old_code)))
                    break

print(f"\nTotal modifications: {len(mods)} (expected {len(swaps) * 2})")

# Apply modifications grouped by line
mods_by_line = defaultdict(list)
for line_num, old_code, new_literal in mods:
    mods_by_line[line_num].append((old_code, new_literal))

changes = 0
errors = 0
for line_num, line_mods in mods_by_line.items():
    line = lines[line_num]
    for old_code, new_literal in line_mods:
        span = find_value_span(line, old_code)
        if span:
            line = line[:span[0]] + new_literal + line[span[1]:]
            changes += 1
        else:
            print(f"ERROR on line {line_num}: Could not find code {old_code!r}")
            errors += 1
    lines[line_num] = line

print(f"\nChanges applied: {changes}")
print(f"Errors: {errors}")

# Write
new_content = '\n'.join(lines)
config_path.write_text(new_content, encoding='utf-8')
print("Config.py written!")

# Verify
import importlib
importlib.reload(config)

phrase_vals = list(config.PHRASE_CODEBOOK.values())
phrase_dups = len(phrase_vals) - len(set(phrase_vals))
sym_vals = list(config.SYMBOL_MAP.values())
sym_dups = len(sym_vals) - len(set(sym_vals))

print(f"\nPHRASE_CODEBOOK duplicate values: {phrase_dups}")
print(f"SYMBOL_MAP duplicate values: {sym_dups}")

verify_errors = 0
for phrase, old_code, new_code, source, key in swaps:
    actual = config.PHRASE_CODEBOOK.get(phrase)
    if actual != new_code:
        print(f"MISMATCH: '{phrase[:40]}...' got {actual!r}, expected {new_code!r}")
        verify_errors += 1
    if source == 'symbol':
        actual_sh = config.SYMBOL_MAP.get(key)
        if actual_sh != old_code:
            print(f"MISMATCH: symbol '{key}' got {actual_sh!r}, expected {old_code!r}")
            verify_errors += 1
    elif source == 'phrase':
        actual_sh = config.PHRASE_CODEBOOK.get(key)
        if actual_sh != old_code:
            print(f"MISMATCH: phrase '{key[:40]}' got {actual_sh!r}, expected {old_code!r}")
            verify_errors += 1

print(f"\nVerification errors: {verify_errors}")
if verify_errors == 0 and phrase_dups == 0 and sym_dups == 0 and errors == 0:
    print("=== ALL VERIFICATIONS PASSED! ===")
else:
    print("=== SOME VERIFICATIONS FAILED ===")

total_savings = sum(byte_size(old) - byte_size(new) for _, old, new, _, _ in swaps)
print(f"\nTotal byte savings: {total_savings}")
