"""
HLC Autoresearch — Validate (v2)
==================================
Runs evaluation against the HOLDOUT set to check for overfitting.
The agent NEVER sees or uses this file. Only the human runs it.

Usage:
    python validate.py           # Quick check
    python validate.py --verbose  # Detailed breakdown
"""

import sys
from pathlib import Path
from evaluate_v2 import load_corpus, compress_text, decompress_text, score_reconstruction, load_config, score_split, check_codebook_caps


def validate(verbose=False):
    config = load_config()

    caps_ok, caps_msg = check_codebook_caps(config)
    if not caps_ok:
        print(f"CODEBOOK CAP VIOLATION: {caps_msg}")
        return 0.0

    holdout = load_corpus("holdout")
    ratio, recon, results = score_split(holdout, config)
    composite = (ratio * 0.6 + recon * 0.4) * 100

    if verbose:
        print("=" * 60)
        print("HLC HOLDOUT VALIDATION (agent never sees this data)")
        print("=" * 60)
        print(f"\n  {'Sample':<28} {'Orig':>6} {'Comp':>6} {'Ratio':>7} {'Recon':>7}")
        print(f"  {'-'*28} {'-'*6} {'-'*6} {'-'*7} {'-'*7}")
        for r in results:
            print(f"  {r['name']:<28} {r['original']:>6} {r['compressed']:>6} "
                  f"{r['ratio']:>6.1f}% {r['reconstruction']*100:>6.1f}%")

        print(f"\n── Holdout Aggregate ──")
        print(f"  Samples:            {len(holdout)}")
        print(f"  Byte compression:   {ratio*100:.1f}%")
        print(f"  Reconstruction:     {recon*100:.1f}%")
        print(f"  {caps_msg}")
        print(f"\n  ═══════════════════════════════")
        print(f"  HOLDOUT COMPOSITE SCORE: {composite:.2f}")
        print(f"  ═══════════════════════════════")
    else:
        print(f"HOLDOUT_SCORE:{composite:.4f} RATIO:{ratio*100:.1f} "
              f"RECON:{recon*100:.1f} SAMPLES:{len(holdout)}")

    return composite


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv
    validate(verbose)
