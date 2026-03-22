"""
HLC Autoresearch — Evaluate
==============================
DO NOT MODIFY THIS FILE. This is the fixed evaluation harness.
The agent only modifies config.py.

Runs the HLC compression pipeline using settings from config.py,
scores the result, and prints a single composite score.

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

# ── Test Corpus (loaded from corpus/train.json — DO NOT modify the corpus files) ──

def load_corpus(split="train"):
    """Load corpus from JSON. Agent optimizes against train. Human validates on holdout."""
    corpus_path = Path(__file__).parent / "corpus" / f"{split}.json"
    if not corpus_path.exists():
        print(f"ERROR: {corpus_path} not found. Run build_corpus.py first.")
        sys.exit(1)
    with open(corpus_path) as f:
        samples = json.load(f)
    return {f"{s['category']}_{i}": s["text"] for i, s in enumerate(samples)}


TEST_SAMPLES = load_corpus("train")

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
            # Already a single char (from symbol sub) — skip
            if len(token) == 1:
                rebuilt.append(token)
                continue
            # Strip interior vowels
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
    """
    Check if two words match, accounting for vowel stripping.
    'prompt' and 'prmpt' should match because they have the same consonant skeleton.
    """
    if orig == decomp:
        return True
    # Check if one is the vowel-stripped form of the other
    if strip_vowels_from_word(orig) == strip_vowels_from_word(decomp):
        return True
    if strip_vowels_from_word(orig) == decomp:
        return True
    if orig == strip_vowels_from_word(decomp):
        return True
    return False


def score_reconstruction(original, decompressed):
    """
    Score how well decompressed text matches original.
    Returns a 0-1 score where 1.0 = perfect match.
    Accounts for vowel stripping — 'prmpt' matches 'prompt'.
    """
    orig_words = re.findall(r"[a-zA-Z']+", original.lower())
    decomp_words = re.findall(r"[a-zA-Z']+", decompressed.lower())

    if not orig_words:
        return 1.0

    # Use SequenceMatcher for alignment, then score with vowel-aware matching
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


def evaluate(verbose=False):
    """
    Run full evaluation. Returns composite score.
    
    Composite score = compression_ratio * 0.6 + reconstruction_accuracy * 0.4
    
    This weights compression slightly higher because reconstruction is already
    very high (~98%) and the main room for improvement is compression ratio.
    """
    config = load_config()

    total_original = 0
    total_compressed = 0
    total_reconstruction_score = 0
    n_samples = len(TEST_SAMPLES)
    phrase_hits = 0
    symbol_hits = 0

    sample_results = []

    for name, text in TEST_SAMPLES.items():
        orig_len = len(text)
        compressed = compress_text(text, config)
        comp_len = len(compressed)
        decompressed = decompress_text(compressed, config)
        recon_score = score_reconstruction(text, decompressed)

        total_original += orig_len
        total_compressed += comp_len
        total_reconstruction_score += recon_score

        # Count phrase hits
        for phrase in config.PHRASE_CODEBOOK:
            if phrase.lower() in text.lower():
                phrase_hits += 1

        # Count symbol hits
        words = re.findall(r"[\w']+", text.lower())
        for w in words:
            if w in config.SYMBOL_MAP:
                symbol_hits += 1

        ratio = (orig_len - comp_len) / orig_len * 100

        sample_results.append({
            "name": name,
            "original": orig_len,
            "compressed": comp_len,
            "ratio": ratio,
            "reconstruction": recon_score,
        })

    # Aggregate metrics
    compression_ratio = (total_original - total_compressed) / total_original
    avg_reconstruction = total_reconstruction_score / n_samples

    # Composite score (0-100 scale)
    composite = (compression_ratio * 0.6 + avg_reconstruction * 0.4) * 100

    if verbose:
        print("=" * 60)
        print("HLC AUTORESEARCH EVALUATION")
        print("=" * 60)
        print(f"\n{'Sample':<28} {'Orig':>6} {'Comp':>6} {'Ratio':>7} {'Recon':>7}")
        print(f"{'-'*28} {'-'*6} {'-'*6} {'-'*7} {'-'*7}")
        for r in sample_results:
            print(f"{r['name']:<28} {r['original']:>6} {r['compressed']:>6} "
                  f"{r['ratio']:>6.1f}% {r['reconstruction']:>6.1f}%")

        print(f"\n── Aggregate ──")
        print(f"  Total original:     {total_original} chars")
        print(f"  Total compressed:   {total_compressed} chars")
        print(f"  Compression ratio:  {compression_ratio*100:.1f}%")
        print(f"  Avg reconstruction: {avg_reconstruction*100:.1f}%")
        print(f"  Phrase hits:        {phrase_hits}")
        print(f"  Symbol hits:        {symbol_hits}")
        print(f"  Phrase codebook:    {len(config.PHRASE_CODEBOOK)} entries")
        print(f"\n  ═══════════════════════════")
        print(f"  COMPOSITE SCORE: {composite:.2f}")
        print(f"  ═══════════════════════════")
    else:
        # Machine-readable single-line output for the agent
        print(f"SCORE:{composite:.4f} RATIO:{compression_ratio*100:.1f} "
              f"RECON:{avg_reconstruction*100:.1f} PHRASES:{phrase_hits} "
              f"CODEBOOK:{len(config.PHRASE_CODEBOOK)}")

    return composite


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv
    score = evaluate(verbose=verbose)
