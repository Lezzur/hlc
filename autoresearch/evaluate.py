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

# ── Test Corpus (FIXED — do not modify) ──

TEST_SAMPLES = {
    "technical_discussion": (
        "Absolutely, and this is the part that deserves more attention. "
        "The compaction quality is bounded by the compacting model's ability "
        "to understand what matters. A more capable model will produce better "
        "summaries because it can reason about relevance, identify dependencies "
        "between statements, and recognize which details are structural versus "
        "decorative. But even the best model is guessing about future relevance "
        "— it doesn't know what you'll ask next."
    ),
    "casual_conversation": (
        "Hey, how are you doing today? I was thinking about what you said "
        "yesterday about the project. I don't think we should rush it because "
        "there are still a lot of things we need to figure out. Let me know "
        "what you think and we can talk about it more later. By the way, did "
        "you see the new update? It's pretty cool but I'm not sure if it "
        "fixes the problem we were having."
    ),
    "business_email": (
        "Thank you for your prompt response regarding the quarterly report. "
        "I have reviewed the financial projections and would like to schedule "
        "a meeting to discuss the budget allocation for the upcoming fiscal year. "
        "In addition to the revenue forecasts, we should also consider the "
        "operational expenses and potential cost reduction strategies. Please "
        "let me know your availability for next week. I would appreciate it "
        "if you could also prepare a brief summary of the key performance "
        "indicators for the board presentation."
    ),
    "technical_documentation": (
        "The system architecture consists of three primary components: the "
        "ingestion pipeline, the processing engine, and the storage layer. "
        "The ingestion pipeline handles incoming data from multiple sources "
        "including REST APIs, message queues, and batch file uploads. Data "
        "is validated, transformed, and normalized before being passed to "
        "the processing engine. The processing engine applies business logic, "
        "performs aggregations, and generates derived metrics. Results are "
        "persisted to the storage layer which supports both real-time queries "
        "and historical analysis through a combination of time-series databases "
        "and columnar data warehouses."
    ),
    "creative_writing": (
        "The old lighthouse keeper stood at the edge of the cliff, watching "
        "the storm clouds gather on the horizon. He had seen countless storms "
        "in his forty years at this post, but something about this one felt "
        "different. The air was heavy with electricity, and the seabirds had "
        "fallen silent hours ago. He checked the lamp one more time, making "
        "sure the mechanism was properly oiled and the lens was spotless. "
        "Tonight would be a long night, and the ships out there would need "
        "every bit of light he could give them."
    ),
    "ai_research": (
        "We present a novel approach to context window optimization in large "
        "language models through hierarchical lexical compression. Our method "
        "achieves significant token reduction without information loss by "
        "applying deterministic rule-based transformations at multiple levels "
        "of linguistic granularity. Unlike semantic compression approaches "
        "which require model inference and produce irreversible information "
        "loss, our system operates through precomputed codebook substitutions "
        "that preserve all original content."
    ),
    "customer_support": (
        "I understand your frustration with the billing issue. Let me look "
        "into this for you right away. It appears that the charge was applied "
        "twice due to a processing error on our end. I have initiated a refund "
        "for the duplicate charge, which should appear in your account within "
        "three to five business days. Is there anything else I can help you "
        "with today? If you experience any further issues, please don't "
        "hesitate to contact us again. We value your business and want to "
        "make sure this is resolved to your satisfaction."
    ),
    "instructional": (
        "To set up the development environment, first install the required "
        "dependencies using the package manager. Make sure you have the latest "
        "version of the runtime installed on your system. Next, clone the "
        "repository and navigate to the project directory. Create a virtual "
        "environment to isolate your project dependencies from the system "
        "packages. Activate the virtual environment and run the installation "
        "script. The configuration file should be updated with your specific "
        "settings before running the application for the first time."
    ),
}

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
