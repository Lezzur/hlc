# HLC Autoresearch — Agent Instructions (Opus Session, Byte-Optimized)

You are an autonomous research agent optimizing the HLC (Hierarchical Lexical Compression) system. Your goal is to **maximize the composite score** by improving both compression ratio and reconstruction accuracy.

## CRITICAL CONTEXT: This is a byte-optimized session

Previous sessions (Haiku, Sonnet) optimized for **character count**. This session optimizes for **UTF-8 byte count**. The evaluator now measures `len(text.encode("utf-8"))` instead of `len(text)`.

**Why this matters:** BPE tokenizers (GPT-4, Claude) operate on bytes. A 3-byte CJK symbol (e.g. `海`) replacing a 3-letter word (e.g. "the") saves 0 bytes despite saving 2 characters. The previous Sonnet session achieved 50.5% character compression but only 40.6% byte compression because 473 of 528 symbols were 3-byte Unicode.

**Your primary lever:** Replace 3-byte Unicode symbols with 1-byte ASCII or 2-byte Latin-1 alternatives. Every 3-byte→1-byte swap on a high-frequency word recovers 2 bytes per occurrence across the entire corpus.

## Setup (one-time)

1. Create a new git branch: `git checkout -b autoresearch/opus-bytes-<date>`
2. Read `config.py` — this is the ONLY file you modify
3. Read `evaluate.py` — this is read-only, do NOT touch it
4. Run the baseline: `python evaluate.py --verbose`
5. Record the baseline score in `results.tsv` (create it with header: `experiment\tdescription\tscore\tratio\trecon\tphrases\tstatus`)
6. Begin experimentation

## The metric

Run `python evaluate.py` after every change. It scores against **80 train samples** across 10 categories. A separate **20-sample holdout set** exists in `corpus/holdout.json` that you NEVER optimize against.
