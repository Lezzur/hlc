"""
HLC Autoresearch — Corpus Builder v2
======================================
300 samples across 15 categories, split 70/15/15 (train/val/holdout).

The corpus JSON files are pre-built. This script verifies them.

Usage:
    python build_corpus_v2.py           # Verify corpus
    python build_corpus_v2.py --stats   # Show detailed statistics
"""

import json
import sys
from pathlib import Path
from collections import Counter


def verify_corpus():
    corpus_dir = Path(__file__).parent / "corpus"

    splits = {}
    for name in ["train", "val", "holdout"]:
        path = corpus_dir / f"{name}.json"
        if not path.exists():
            print(f"ERROR: {path} not found")
            sys.exit(1)
        with open(path) as f:
            splits[name] = json.load(f)

    total = sum(len(v) for v in splits.values())
    all_samples = [s for v in splits.values() for s in v]
    cats = Counter(s["category"] for s in all_samples)
    chars = sum(len(s["text"]) for s in all_samples)
    unique = len(set(s["text"] for s in all_samples))

    print(f"Corpus v2: {total} samples, {chars:,} chars, {len(cats)} categories")
    print(f"Unique texts: {unique}/{total}")
    print(f"\nSplit:")
    for name, data in splits.items():
        print(f"  {name:>8}: {len(data)} samples, {sum(len(s['text']) for s in data):,} chars")

    if "--stats" in sys.argv:
        print(f"\nCategory distribution:")
        for cat in sorted(cats):
            t = sum(1 for s in splits["train"] if s["category"] == cat)
            v = sum(1 for s in splits["val"] if s["category"] == cat)
            h = sum(1 for s in splits["holdout"] if s["category"] == cat)
            print(f"  {cat:<20} train:{t:>3}  val:{v:>2}  holdout:{h:>2}  total:{t+v+h:>3}")

    # Sanity checks
    assert unique == total, f"Duplicate texts found: {total - unique}"
    assert total >= 280, f"Too few samples: {total}"
    assert len(cats) >= 12, f"Too few categories: {len(cats)}"
    for name, data in splits.items():
        for s in data:
            assert 100 < len(s["text"]) < 800, f"Bad length in {name}: {len(s['text'])}"

    print(f"\n✅ Corpus verified")


if __name__ == "__main__":
    verify_corpus()
