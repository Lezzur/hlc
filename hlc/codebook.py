"""
HLC Codebook Generator
======================
Builds Unicode-first codebooks from frequency-ranked word and phrase data.
Assigns single Unicode characters to the highest-value items,
falls back to short numeric codes for the rest.
"""

import json
from pathlib import Path

CODEBOOK_DIR = Path(__file__).parent / "codebooks"

# ── Unicode Character Pools ──
# Each pool is a range of Unicode codepoints that are:
# 1. Visually distinct from each other and from ASCII
# 2. Typically single tokens in LLM tokenizers
# 3. Not commonly used in English text

def _build_unicode_pool():
    """
    Build a pool of Unicode characters for codebook assignment.
    Ordered by preference: most visually distinct and tokenizer-friendly first.
    """
    pool = []
    
    # Greek lowercase (24 chars) — familiar, visually clear
    for cp in range(0x03B1, 0x03CA):  # α to ω
        if chr(cp).isalpha():
            pool.append(chr(cp))
    
    # Greek uppercase (24 chars)
    for cp in range(0x0391, 0x03AA):
        if chr(cp).isalpha():
            pool.append(chr(cp))
    
    # Cyrillic common (66 chars) — visually distinct from Latin
    for cp in range(0x0410, 0x0450):
        pool.append(chr(cp))
    
    # CJK Unified Ideographs subset (common, single-token)
    # Using a curated range of common characters
    cjk_ranges = [
        (0x4E00, 0x4E60),   # very common CJK (~96 chars)
        (0x4E8C, 0x4EFF),   # more common CJK
        (0x5000, 0x5100),   # extended common
        (0x5200, 0x5300),   # extended common
        (0x6000, 0x6100),   # extended
        (0x7000, 0x7100),   # extended
        (0x8000, 0x8100),   # extended
        (0x9000, 0x9100),   # extended
    ]
    for start, end in cjk_ranges:
        for cp in range(start, end):
            pool.append(chr(cp))
    
    # Armenian (38 chars)
    for cp in range(0x0531, 0x0557):
        pool.append(chr(cp))
    
    # Georgian (38 chars)
    for cp in range(0x10A0, 0x10C6):
        pool.append(chr(cp))
    
    # Thai consonants (44 chars)
    for cp in range(0x0E01, 0x0E2F):
        pool.append(chr(cp))
    
    # Devanagari (48 chars)
    for cp in range(0x0905, 0x0940):
        pool.append(chr(cp))
    
    # Mathematical symbols (common, recognizable)
    math_symbols = [
        '∀', '∃', '∅', '∇', '∈', '∉', '∋', '∏', '∑', '∗',
        '√', '∝', '∞', '∧', '∨', '∩', '∪', '∫', '≈', '≠',
        '≡', '≤', '≥', '⊂', '⊃', '⊆', '⊇', '⊕', '⊗', '⊥',
        '⋅', '⌈', '⌉', '⌊', '⌋', '⟨', '⟩',
    ]
    pool.extend(math_symbols)
    
    # Currency and misc symbols
    misc_symbols = [
        '₿', '₹', '₩', '₫', '₭', '₮', '₯', '₰', '₱', '₲',
        '₳', '₴', '₵', '₶', '₷', '₸', '₺', '₻', '₼', '₽',
        '℃', '℉', '℗', '℘', '℞', '℧', '℩', '℮',
        '⌀', '⌁', '⌂', '⌃', '⌄', '⌅', '⌆', '⌇',
    ]
    pool.extend(misc_symbols)
    
    # Remove any duplicates while preserving order
    seen = set()
    deduped = []
    for ch in pool:
        if ch not in seen:
            seen.add(ch)
            deduped.append(ch)
    
    return deduped


# ── Symbol Map for High-Frequency Short Words ──
SYMBOL_MAP = {
    "and": "+",
    "the": "^",
    "is": "$",
    "be": "$",
    "that": "~",
    "for": "@",
    "at": "@",
    "what": "#",
    "with": "&",
    "this": "!",
    "from": "%",
    "not": "*",
}

# Reverse map for decompression
SYMBOL_REVERSE = {}
for word, sym in SYMBOL_MAP.items():
    if sym not in SYMBOL_REVERSE:
        SYMBOL_REVERSE[sym] = word  # first mapping wins for reverse


# ── Codebook Builder ──

def build_phrase_codebook(phrase_freq_path=None):
    """
    Build phrase codebook: most frequent phrases get single Unicode chars.
    """
    if phrase_freq_path is None:
        phrase_freq_path = CODEBOOK_DIR / "phrase_freq.json"
    
    with open(phrase_freq_path) as f:
        phrases = json.load(f)
    
    unicode_pool = _build_unicode_pool()
    pool_idx = 0
    
    codebook = {}
    reverse = {}
    
    for item in phrases:
        phrase = item["phrase"]
        char_count = item["char_count"]
        
        # Assign Unicode char if available and saves space
        if pool_idx < len(unicode_pool):
            code = unicode_pool[pool_idx]
            code_len = 1
            pool_idx += 1
        else:
            # Numeric fallback
            code = f"P{len(codebook) + 1}"
            code_len = len(code)
        
        # Only add if code is shorter than phrase
        if code_len < char_count:
            codebook[phrase] = code
            reverse[code] = phrase
    
    # Return codebook, reverse map, and next available pool index
    return codebook, reverse, pool_idx


def build_word_codebook(word_freq_path=None, unicode_pool_start=0):
    """
    Build word codebook: most frequent long words get Unicode chars,
    rest get short numeric codes.
    """
    if word_freq_path is None:
        word_freq_path = CODEBOOK_DIR / "word_freq.json"
    
    with open(word_freq_path) as f:
        words = json.load(f)
    
    unicode_pool = _build_unicode_pool()
    pool_idx = unicode_pool_start  # continue from where phrase codebook left off
    
    # Words already handled by symbol map
    symbol_words = set(SYMBOL_MAP.keys())
    
    codebook = {}
    reverse = {}
    numeric_counter = 1
    
    for item in words:
        word = item["word"]
        word_len = item["word_length"]
        
        # Skip words handled by symbol map
        if word.lower() in symbol_words:
            continue
        
        # Try Unicode assignment first
        if pool_idx < len(unicode_pool):
            code = unicode_pool[pool_idx]
            code_len = 1
            
            if code_len < word_len:
                codebook[word] = code
                reverse[code] = word
                pool_idx += 1
                continue
        
        # Numeric fallback
        code = str(numeric_counter)
        code_len = len(code)
        
        if code_len < word_len:
            codebook[word] = code
            reverse[code] = word
            numeric_counter += 1
    
    return codebook, reverse


def build_all_codebooks():
    """Build all codebooks and save to disk."""
    print("Building phrase codebook...")
    phrase_cb, phrase_rev, pool_offset = build_phrase_codebook()
    print(f"  Phrases encoded: {len(phrase_cb)}")
    print(f"  Unicode chars used: {pool_offset}")
    
    print("Building word codebook...")
    word_cb, word_rev = build_word_codebook(unicode_pool_start=pool_offset)
    print(f"  Words encoded: {len(word_cb)}")
    
    # Count Unicode vs numeric codes in word codebook
    unicode_words = sum(1 for code in word_cb.values() if len(code) == 1 and not code.isdigit())
    numeric_words = len(word_cb) - unicode_words
    print(f"  Unicode codes: {unicode_words}")
    print(f"  Numeric codes: {numeric_words}")
    
    # Save codebooks
    all_codebooks = {
        "phrase_codebook": phrase_cb,
        "phrase_reverse": phrase_rev,
        "word_codebook": word_cb,
        "word_reverse": word_rev,
        "symbol_map": SYMBOL_MAP,
        "symbol_reverse": SYMBOL_REVERSE,
    }
    
    with open(CODEBOOK_DIR / "codebook_full.json", "w") as f:
        json.dump(all_codebooks, f, ensure_ascii=False, indent=2)
    print(f"\nSaved full codebook to codebook_full.json")
    
    # Save compact version (no reverse maps — those are computed at load time)
    compact = {
        "phrases": phrase_cb,
        "words": word_cb,
        "symbols": SYMBOL_MAP,
    }
    with open(CODEBOOK_DIR / "codebook_compact.json", "w") as f:
        json.dump(compact, f, ensure_ascii=False)
    print(f"Saved compact codebook to codebook_compact.json")
    
    # Stats
    total_entries = len(phrase_cb) + len(word_cb) + len(SYMBOL_MAP)
    print(f"\nTotal codebook entries: {total_entries}")
    print(f"  Phrases: {len(phrase_cb)}")
    print(f"  Words: {len(word_cb)}")
    print(f"  Symbols: {len(SYMBOL_MAP)}")
    
    # Sample entries
    print("\n── Sample Phrase Codes ──")
    for phrase, code in list(phrase_cb.items())[:10]:
        print(f"  '{phrase}' → '{code}'")
    
    print("\n── Sample Word Codes (top 20) ──")
    for word, code in list(word_cb.items())[:20]:
        print(f"  '{word}' → '{code}'")
    
    return all_codebooks


if __name__ == "__main__":
    codebooks = build_all_codebooks()
