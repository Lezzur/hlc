"""
HLC Autoresearch — Validate
==============================
Runs evaluation against the HOLDOUT set to check for overfitting.
The agent NEVER sees or uses this file. Only the human runs it.

Usage:
    python validate.py           # Quick check
    python validate.py --verbose  # Detailed breakdown
"""

import sys
from pathlib import Path
from evaluate import load_corpus, compress_text, decompress_text, score_reconstruction, load_config


def validate(verbose=False):
    config = load_config()
    holdout = load_corpus("holdout")

    total_original = 0
    total_compressed = 0
    total_recon = 0
    n = len(holdout)
    results = []

    for name, text in holdout.items():
        orig_len = len(text)
        compressed = compress_text(text, config)
        comp_len = len(compressed)
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
            "reconstruction": recon * 100,
        })

    compression_ratio = (total_original - total_compressed) / total_original
    avg_recon = total_recon / n
    composite = (compression_ratio * 0.6 + avg_recon * 0.4) * 100

    if verbose:
        print("=" * 60)
        print("HLC HOLDOUT VALIDATION (agent never sees this data)")
        print("=" * 60)
        print(f"\n{'Sample':<28} {'Orig':>6} {'Comp':>6} {'Ratio':>7} {'Recon':>7}")
        print(f"{'-'*28} {'-'*6} {'-'*6} {'-'*7} {'-'*7}")
        for r in results:
            print(f"{r['name']:<28} {r['original']:>6} {r['compressed']:>6} "
                  f"{r['ratio']:>6.1f}% {r['reconstruction']:>6.1f}%")

        print(f"\n── Holdout Aggregate ──")
        print(f"  Samples:            {n}")
        print(f"  Total original:     {total_original} chars")
        print(f"  Total compressed:   {total_compressed} chars")
        print(f"  Compression ratio:  {compression_ratio*100:.1f}%")
        print(f"  Avg reconstruction: {avg_recon*100:.1f}%")
        print(f"\n  ═══════════════════════════════")
        print(f"  HOLDOUT COMPOSITE SCORE: {composite:.2f}")
        print(f"  ═══════════════════════════════")
    else:
        print(f"HOLDOUT_SCORE:{composite:.4f} RATIO:{compression_ratio*100:.1f} "
              f"RECON:{avg_recon*100:.1f} SAMPLES:{n}")

    return composite


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv
    validate(verbose)
