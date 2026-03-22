"""
HLC Autoresearch — Evaluate (v2)
==================================
DO NOT MODIFY THIS FILE. This is the fixed evaluation harness.
The agent only modifies config.py.

Runs the HLC compression pipeline using settings from config.py,
scores the result against BOTH train and validation splits,
and prints a composite score.

KEY CHANGES FROM V1:
- Measures compression in UTF-8 BYTES (not characters)
- Scores against both train AND validation (prevents overfitting)
- Codebook size caps: SYMBOL_MAP ≤ 800, PHRASE_CODEBOOK ≤ 500
- Composite = 0.5 * train_score + 0.5 * val_score

Usage:
    python evaluate.py          # Run evaluation, print score
    python evaluate.py --verbose  # Print detailed breakdown
"""

import re
import sys
import json
import importlib
from pathlib import Path
from difflib import SequenceMatcher

# ═══════════════════════════════════════════════════════════
# CODEBOOK SIZE LIMITS — hard caps to prevent memorization
# ═══════════════════════════════════════════════════════════
MAX_SYMBOL_MAP = 900
MAX_PHRASE_CODEBOOK = 600

# ── Corpus Loading ──

def load_corpus(split="train"):
    """Load corpus from JSON."""
    corpus_path = Path(__file__).parent / "corpus" / f"{split}.json"
    if not corpus_path.exists():
        print(f"ERROR: {corpus_path} not found. Run build_corpus_v2.py first.")
        sys.exit(1)
    with open(corpus_path) as f:
        samples = json.load(f)
    return {f"{s['category']}_{i}": s["text"] for i, s in enumerate(samples)}


TRAIN_SAMPLES = load_corpus("train")
VAL_SAMPLES = load_corpus("val")

# ── Compression Engine (uses config.py settings) ──

VOWELS = set("aeiouAEIOU")


def load_config():
    """Reload config.py to pick up agent's changes."""
    import config
    importlib.reload(config)
    return config


def compress_text(text, config):
    """Compress text using all layers with settings from config."""
    result = text

    # Layer 1: Phrase substitution (longest phrases first)
    phrases_sorted = sorted(config.PHRASE_CODEBOOK.keys(), key=len, reverse=True)
    for phrase in phrases_sorted:
        code = config.PHRASE_CODEBOOK[phrase]
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        result = pattern.sub(code, result)

    # Layer 2: Symbol substitution
    tokens = re.findall(r"[\w']+|[^\w\s]|\s+", result)
    rebuilt = []
    for token in tokens:
        if re.match(r"[\w']+", token):
            lower = token.lower()
            if lower in config.SYMBOL_MAP:
                rebuilt.append(config.SYMBOL_MAP[lower])
            else:
                rebuilt.append(token)
        else:
            rebuilt.append(token)
    result = "".join(rebuilt)

    # Layer 3: Vowel stripping
    tokens = re.findall(r"[\w']+|[^\w\s]|\s+", result)
    rebuilt = []
    for token in tokens:
        if re.match(r"[a-zA-Z]+$", token):
            lower = token.lower()
            if lower in config.PROTECTED_SHORTHAND:
                rebuilt.append(token)
                continue
            if lower in config.VOWEL_STRIP_EXCEPTIONS:
                rebuilt.append(token)
                continue
            if len(token) < config.MIN_VOWEL_STRIP_LENGTH:
                rebuilt.append(token)
                continue
            if len(token) == 1:
                rebuilt.append(token)
                continue
            first = token[0]
            last = token[-1]
            middle = token[1:-1]
            stripped = "".join(c for c in middle if c not in VOWELS)
            if stripped:
                rebuilt.append(first + stripped + last)
            else:
                rebuilt.append(token)
        else:
            rebuilt.append(token)
    result = "".join(rebuilt)

    return result


def decompress_text(compressed, config):
    """Deterministic decompression — reverse Layers 1-2."""
    result = compressed

    # Reverse symbols
    symbol_reverse = {}
    for word, sym in config.SYMBOL_MAP.items():
        if sym not in symbol_reverse:
            symbol_reverse[sym] = word

    tokens = re.findall(r"[\w']+|[^\w\s]|\s+", result)
    rebuilt = []
    for token in tokens:
        if token in symbol_reverse:
            rebuilt.append(symbol_reverse[token])
        else:
            rebuilt.append(token)
    result = "".join(rebuilt)

    # Reverse phrases
    phrase_reverse = {v: k for k, v in config.PHRASE_CODEBOOK.items()}
    for code, phrase in phrase_reverse.items():
        result = result.replace(code, phrase)

    return result


def strip_vowels_from_word(word):
    """Strip interior vowels from a word for comparison."""
    if len(word) < 3:
        return word
    first = word[0]
    last = word[-1]
    middle = word[1:-1]
    stripped = "".join(c for c in middle if c.lower() not in "aeiou")
    return first + stripped + last if stripped else word


def words_match(orig, decomp):
    """Check if two words match, accounting for vowel stripping."""
    if orig == decomp:
        return True
    if strip_vowels_from_word(orig) == strip_vowels_from_word(decomp):
        return True
    if strip_vowels_from_word(orig) == decomp:
        return True
    if orig == strip_vowels_from_word(decomp):
        return True
    return False


def score_reconstruction(original, decompressed):
    """Score how well decompressed text matches original (0-1)."""
    orig_words = re.findall(r"[a-zA-Z']+", original.lower())
    decomp_words = re.findall(r"[a-zA-Z']+", decompressed.lower())

    if not orig_words:
        return 1.0

    matcher = SequenceMatcher(None, orig_words, decomp_words)
    matches = 0
    total = max(len(orig_words), len(decomp_words))

    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            matches += (i2 - i1)
        elif op == "replace":
            for o, d in zip(orig_words[i1:i2], decomp_words[j1:j2]):
                if words_match(o, d):
                    matches += 1

    return matches / total if total > 0 else 1.0


def score_split(samples, config):
    """Score compression on a corpus split. Returns (ratio, recon, details)."""
    total_original = 0
    total_compressed = 0
    total_recon = 0
    n = len(samples)
    results = []

    for name, text in samples.items():
        orig_len = len(text.encode("utf-8"))
        compressed = compress_text(text, config)
        comp_len = len(compressed.encode("utf-8"))
        decompressed = decompress_text(compressed, config)
        recon = score_reconstruction(text, decompressed)

        total_original += orig_len
        total_compressed += comp_len
        total_recon += recon

        results.append({
            "name": name,
            "original": orig_len,
            "compressed": comp_len,
            "ratio": (orig_len - comp_len) / orig_len * 100,
            "reconstruction": recon,
        })

    compression_ratio = (total_original - total_compressed) / total_original
    avg_recon = total_recon / n

    return compression_ratio, avg_recon, results


def check_codebook_caps(config):
    """Check codebook sizes against caps. Returns (ok, message)."""
    sym_count = len(config.SYMBOL_MAP)
    phrase_count = len(config.PHRASE_CODEBOOK)

    violations = []
    if sym_count > MAX_SYMBOL_MAP:
        violations.append(f"SYMBOL_MAP has {sym_count} entries (max {MAX_SYMBOL_MAP})")
    if phrase_count > MAX_PHRASE_CODEBOOK:
        violations.append(f"PHRASE_CODEBOOK has {phrase_count} entries (max {MAX_PHRASE_CODEBOOK})")

    if violations:
        return False, "; ".join(violations)
    return True, f"SYMBOL_MAP: {sym_count}/{MAX_SYMBOL_MAP}, PHRASES: {phrase_count}/{MAX_PHRASE_CODEBOOK}"


def evaluate(verbose=False):
    """
    Run full evaluation. Returns composite score.

    IMPORTANT: Compression ratio is measured in UTF-8 BYTES, not characters.
    Score = 0.5 * train_subscore + 0.5 * val_subscore
    Each subscore = ratio * 0.6 + reconstruction * 0.4
    Codebook caps enforced: SYMBOL_MAP ≤ 800, PHRASE_CODEBOOK ≤ 500.
    """
    config = load_config()

    # ── Check codebook caps ──
    caps_ok, caps_msg = check_codebook_caps(config)
    if not caps_ok:
        if verbose:
            print("=" * 60)
            print("CODEBOOK CAP VIOLATION — SCORE ZEROED")
            print("=" * 60)
            print(f"\n  {caps_msg}")
            print(f"\n  Reduce codebook size and try again.")
            print(f"\n  ═══════════════════════════")
            print(f"  COMPOSITE SCORE: 0.00")
            print(f"  ═══════════════════════════")
        else:
            print(f"SCORE:0.0000 RATIO:0.0 RECON:0.0 CAP_VIOLATION:{caps_msg}")
        return 0.0

    # ── Score train split ──
    train_ratio, train_recon, train_results = score_split(TRAIN_SAMPLES, config)
    train_subscore = (train_ratio * 0.6 + train_recon * 0.4) * 100

    # ── Score validation split ──
    val_ratio, val_recon, val_results = score_split(VAL_SAMPLES, config)
    val_subscore = (val_ratio * 0.6 + val_recon * 0.4) * 100

    # ── Composite: average of train and val ──
    composite = 0.5 * train_subscore + 0.5 * val_subscore

    # ── Count hits ──
    phrase_hits = 0
    symbol_hits = 0
    for name, text in TRAIN_SAMPLES.items():
        for phrase in config.PHRASE_CODEBOOK:
            if phrase.lower() in text.lower():
                phrase_hits += 1
        words = re.findall(r"[\w']+", text.lower())
        for w in words:
            if w in config.SYMBOL_MAP:
                symbol_hits += 1

    if verbose:
        print("=" * 60)
        print("HLC AUTORESEARCH EVALUATION (v2 — byte-based, train+val)")
        print("=" * 60)

        print(f"\n── Train ({len(TRAIN_SAMPLES)} samples) ──")
        print(f"  {'Sample':<28} {'Orig':>6} {'Comp':>6} {'Ratio':>7} {'Recon':>7}")
        print(f"  {'-'*28} {'-'*6} {'-'*6} {'-'*7} {'-'*7}")
        for r in train_results:
            print(f"  {r['name']:<28} {r['original']:>6} {r['compressed']:>6} "
                  f"{r['ratio']:>6.1f}% {r['reconstruction']*100:>6.1f}%")
        print(f"\n  Byte compression: {train_ratio*100:.1f}%")
        print(f"  Reconstruction:   {train_recon*100:.1f}%")
        print(f"  Train subscore:   {train_subscore:.2f}")

        print(f"\n── Validation ({len(VAL_SAMPLES)} samples) ──")
        print(f"  {'Sample':<28} {'Orig':>6} {'Comp':>6} {'Ratio':>7} {'Recon':>7}")
        print(f"  {'-'*28} {'-'*6} {'-'*6} {'-'*7} {'-'*7}")
        for r in val_results:
            print(f"  {r['name']:<28} {r['original']:>6} {r['compressed']:>6} "
                  f"{r['ratio']:>6.1f}% {r['reconstruction']*100:>6.1f}%")
        print(f"\n  Byte compression: {val_ratio*100:.1f}%")
        print(f"  Reconstruction:   {val_recon*100:.1f}%")
        print(f"  Val subscore:     {val_subscore:.2f}")

        print(f"\n── Aggregate ──")
        print(f"  Train/val gap:    {abs(train_subscore - val_subscore):.2f} points")
        print(f"  Phrase hits:      {phrase_hits}")
        print(f"  Symbol hits:      {symbol_hits}")
        print(f"  {caps_msg}")

        print(f"\n  ═══════════════════════════")
        print(f"  COMPOSITE SCORE: {composite:.2f}")
        print(f"  ═══════════════════════════")
    else:
        print(f"SCORE:{composite:.4f} TRAIN:{train_subscore:.2f} VAL:{val_subscore:.2f} "
              f"TRATIO:{train_ratio*100:.1f} VRATIO:{val_ratio*100:.1f} "
              f"TRECON:{train_recon*100:.1f} VRECON:{val_recon*100:.1f} "
              f"GAP:{abs(train_subscore - val_subscore):.2f} "
              f"PHRASES:{phrase_hits} SYMS:{len(config.SYMBOL_MAP)} "
              f"PBOOK:{len(config.PHRASE_CODEBOOK)}")

    return composite


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv
    score = evaluate(verbose=verbose)
