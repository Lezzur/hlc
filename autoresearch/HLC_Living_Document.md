# HLC Project — Living Document

**Last updated:** March 22, 2026 (end of Session 1)
**Author:** Ruzzel Maestro (rocketturtles.creative@gmail.com)
**Repo:** https://github.com/Lezzur/hlc
**Status:** Phase 2 in progress — autoresearch optimization complete for Haiku + Sonnet

---

## What is this document?

This is the continuity file for the HLC (Hierarchical Lexical Compression) project. If you are an AI assistant picking this up in a new chat, read this entire document before doing anything. It contains the full project context, all decisions made, current state, and exactly what to do next.

---

## The Big Idea (1-paragraph summary)

Current LLM systems compress conversation history using summarization, which is lossy, expensive, and unpredictable. HLC is a fundamentally different approach: instead of semantic compression (deciding what to discard), it applies deterministic, rule-based lexical compression that reduces token count by 50-60% while preserving ALL information. The key insight is that LLMs are natural decompressors — they can reconstruct full English from aggressively compressed text because that's literally what next-token prediction does. This has been empirically validated: Claude Haiku (smallest model) achieved 98.8% word-for-word reconstruction accuracy on compressed text with no codebook. The autoresearch optimization loop has pushed compression from 27.3% to 50.5% while maintaining 99.9% reconstruction accuracy.

---

## How HLC Works — The Six Layers

Compression layers applied in order from highest to lowest impact:

1. **Layer 1 — Phrase codebook**: Common multi-word phrases to single Unicode characters. "it is important to note that" becomes alpha. Highest impact per substitution. Includes semantic deduplication (80% equivalence threshold — "how are you" / "hey how are you" / "dude how are you" all map to same code).

2. **Layer 2 — Word codebook**: Frequency-ranked individual words to Unicode characters (top ~3000) or short numeric codes (rest). 37,639 words encoded. Morphological handling: "produce" = code 11, "produces" = 11s, "produced" = 11d.

3. **Layer 3 — Symbol substitution**: High-frequency short function words to single ASCII symbols. and=+, the=^, is/be=$, that=~, for/at=@, what=#, with=&, this=!, from=%, not=*.

4. **Layer 4 — Vowel stripping**: Remove interior vowels from remaining words, keep first and last char. "compaction" becomes "cmpctn", "model" becomes "modl". Skip words under 4 chars.

5. **Layer 5 — Recursive pattern compression**: Find repeated patterns in the compressed output itself and assign macro codes. More effective as conversations grow longer. Currently placeholder — needs implementation.

6. **Layer 6 — Semantic enrichment**: Metadata markers that ADD information. ![critical], t[technical], e[emotional], d[decision], ?[unresolved]. Paradoxically makes compressed form MORE informative than original.

**Critical rule:** Existing shorthand is sacred. btw=by the way, tldr, fyi, imo, gtg, brb, etc. — never reassign these. 54 protected terms.

---

## Key Design Decisions Made

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| Codebook format | Unicode-first, numeric fallback | Single Unicode chars = single tokens in most tokenizers = maximum compression per substitution |
| Layer ordering | Phrases first (biggest impact), then words, symbols, vowels | Biggest savings come from replacing multi-word phrases with single codes |
| License | Apache 2.0 | Patent protection clause — important given the IP nature of this work |
| Compression target | Machine-readable, not human-readable | Optimizing for LLM reconstruction, not human reading |
| Codebook scope | Universal English codebook (static, precomputed) | One-time cost, reusable across all conversations |
| Autoresearch design | Sequential model chain (Haiku then Sonnet then Opus) | Each model builds on the previous best. More capable models find optimizations less capable ones miss. |
| Corpus split | 80 train / 20 holdout, stratified across 10 categories | Prevents overfitting. Agent optimizes on train, human validates on holdout. |

---

## Autoresearch Results (March 22, 2026)

### What is autoresearch?

An autonomous optimization loop inspired by Karpathy's autoresearch pattern. An AI agent edits a config file, runs evaluation, keeps improvements, reverts failures, and loops. Applied to HLC codebook optimization.

### Architecture

```
autoresearch/
├── config.py          # THE MUTABLE FILE — agent edits this
├── evaluate.py        # Fixed scorer — 80 train samples, 10 categories
├── validate.py        # Holdout checker — 20 samples, human-only
├── build_corpus.py    # Corpus generator
├── program.md         # Agent instructions (Karpathy-style)
├── corpus/
│   ├── train.json     # 80 samples across 10 categories (34K chars)
│   └── holdout.json   # 20 samples for overfitting detection (9K chars)
├── reports/
│   ├── autoresearch_session_haiku_mar22.md
│   └── autoresearch_session_sonnet_mar22.md
├── config_haiku_best.py
├── config_sonnet_best.py
├── results_haiku.tsv
└── results_sonnet.tsv
```

### Session Results — The Core Data

| Metric | Baseline | Haiku (50 exps) | Sonnet (50 exps) |
|---|---|---|---|
| Train score | 56.08 | 60.51 | **70.22** |
| Holdout score | 57.02 | 60.33 | **66.10** |
| Train/holdout gap | 0.94 | 0.18 | 4.12 |
| Compression ratio (train) | 27.3% | 35.2% | **50.5%** |
| Compression ratio (holdout) | 28.7% | 35.5% | **43.6%** |
| Reconstruction | 99.3% | 98.4% | **99.9%** |
| Experiments run | — | 50 | 50 |
| Successful improvements | — | 36 (72%) | **50 (100%)** |
| Failures/reversions | — | 13 | **0** |
| Phrase codebook entries | 101 | 418 | 582 |
| Symbol map entries | 12 | ~200 | **528** |
| Collision bugs introduced | — | 29 | **0** |

### Key Findings

1. **Sonnet found and fixed 29 collision bugs from Haiku's session.** Two words mapped to the same symbol character causing silent reconstruction failures. Haiku couldn't detect its own errors; Sonnet fixed them all in experiment 1. RECON jumped from 98.4% to 99.9%. This mirrors the HLC thesis: compression quality is bounded by model capability.

2. **Sonnet had 100% success rate vs Haiku's 72%.** More capable model searched more efficiently — systematic word-length sweeps instead of trial-and-error. Never proposed a change that made things worse.

3. **Compression crossed 50% on train set.** From 27.3% baseline to 50.5% through symbol expansion (528 entries) and phrase mining (582 entries). Holdout reached 43.6%.

4. **The 4.12-point holdout gap is from vocabulary specificity, not text mangling.** Reconstruction accuracy is 99.9% on both splits. The gap is because Sonnet mined train-specific words that don't all appear in holdout.

5. **Diminishing returns are smooth.** Phrase discovery: +0.5-0.8 per batch early. Symbol expansion: +0.08-0.3 per batch. No cliff. Natural ceiling estimated at ~72-75 on current corpus.

6. **Morphological patterns had zero impact.** Tested by Haiku, confirmed by Sonnet.

7. **Contractions are valid symbol keys.** Python tokenizer handles "it's", "don't", "i've" as single tokens.

8. **Unicode symbol space is not a bottleneck.** 528 symbols used across ASCII, Hangul, Katakana, Hiragana, CJK. Thousands more available.

---

## LLM Reconstruction Tests

### Living document test (all 3 models, Layers 3+4 only, 17% compression, NO codebook):

| Model | Words | Accuracy | Semantic accuracy |
|-------|-------|----------|-------------------|
| Haiku | 1,432 | 98.18% | ~100% |
| Sonnet | 1,432 | 98.27% | ~100% |
| Opus | 1,432 | 98.95% | ~100% |
| **Overall** | **4,309** | **98.47%** | **~100%** |

Tested on the full living document (complex technical content with tables, code blocks, markdown, URLs). Zero meaning-altering errors. Opus commented: "this document is itself a pretty compelling proof of concept."

### Short paragraph tests (Haiku only, Layers 3+4 only, ~29% compression):

| Sample | Accuracy | Notes |
|--------|----------|-------|
| Technical | 97.0% (65/67) | "compaction" became "compression", "decorative" became "descriptive" — semantically equivalent |
| Casual | 100% (51/51) | Perfect |
| Business | 100% (51/51) | Perfect |
| **Overall** | **98.8%** | **Semantic: 100%** |

### Two compression tiers explained

- **Layers 3+4 only (17-29% compression)**: No codebook needed. Any LLM reads natively. Use for continuity documents uploaded to new chats.
- **All layers (50-53% compression)**: Requires codebook in context. Use inside agent systems where codebook is loaded once per session.

---

## Project Structure

```
hlc-release/
├── hlc/                        # Core Python package
│   ├── __init__.py
│   ├── analyze.py
│   ├── codebook.py
│   ├── compress.py
│   ├── benchmark.py
│   └── codebooks/
├── autoresearch/               # Autonomous optimization loop
│   ├── config.py               # Current best (Sonnet optimized)
│   ├── evaluate.py
│   ├── validate.py
│   ├── build_corpus.py
│   ├── program.md
│   ├── corpus/
│   ├── reports/
│   ├── config_haiku_best.py
│   └── config_sonnet_best.py
├── examples/
├── tests/
├── docs/
│   ├── HLC_Technical_Paper.docx
│   ├── HLC_Living_Document.md
│   └── HLC_Living_Document_Compressed.md
├── README.md
├── LICENSE
├── requirements.txt
└── setup.py
```

---

## Roadmap

### Phase 1: Build the engine (COMPLETE)
- [x] Corpus frequency analysis (38,050 codeable words)
- [x] Unicode-first codebook generation (37,639 words + 95 phrases)
- [x] 6-layer compression pipeline
- [x] Decompression engine (deterministic for L1-3)
- [x] Benchmark suite (8 categories)
- [x] Test suite (14 tests passing)
- [x] GitHub repo live: https://github.com/Lezzur/hlc

### Phase 2: Benchmark and validate (IN PROGRESS)
- [x] LLM reconstruction test — Haiku (98.18% on living doc, 98.8% on paragraphs)
- [x] LLM reconstruction test — Sonnet (98.27% on living doc)
- [x] LLM reconstruction test — Opus (98.95% on living doc)
- [x] Autoresearch: Haiku session (56.08 to 60.51, 50 experiments)
- [x] Autoresearch: Sonnet session (60.51 to 70.22, 50 experiments)
- [x] Holdout validation (Haiku: 60.33, Sonnet: 66.10)
- [ ] Autoresearch: Opus session (optional — build on Sonnet's 70.22)
- [ ] Measure actual TOKEN counts (not just characters)
- [ ] Edge case handling: URLs, emails, code, numbers, proper nouns
- [ ] Integrate autoresearch config back into main hlc/ package

### Phase 3: Package and publish (NOT STARTED)
- [ ] Rewrite technical paper with all measured data
- [ ] Format paper for arXiv (LaTeX, proper citations)
- [ ] Build live web demo
- [ ] pip package (pypi)
- [ ] Submit to arXiv

### Phase 4: Outreach (NOT STARTED)
- [ ] Hacker News, Reddit r/MachineLearning, X/Twitter
- [ ] Target researchers in context management and tokenizer design
- [ ] Contact LLM providers (Anthropic, OpenAI, Google DeepMind)
- [ ] Blog post with interactive demo

### Phase 5: Training frontier (NEEDS PARTNERS)
- [ ] Generate HLC-encoded training corpus
- [ ] Fine-tune model on compressed text
- [ ] Zero-codebook deployment

---

## Known Issues and Technical Debt

1. **Token vs character gap** — biggest unknown. All benchmarks measure character savings. Unicode chars may tokenize into multiple tokens. MUST measure before publishing.

2. **Two architectures diverging** — main hlc/ package uses 37k word codebook. Autoresearch config.py uses 528 symbol map + 582 phrases. Need reconciliation.

3. **Holdout gap (4.12 points)** — from train-specific vocabulary. Not reconstruction failure. Mitigate by expanding corpus or filtering low-frequency words.

4. **No edge case protection** — URLs, emails, code get compressed. Need preserve layer.

5. **Layer 5 placeholder** — recursive pattern compression not implemented.

6. **Collision risk** — Haiku introduced 29 collisions. Need automated collision checking in evaluate.py.

---

## How to Continue in a New Chat

Upload this document and say:

> "I'm Ruzzel. This is my HLC project living document. Read it and let's continue where I left off. [Then state what you want to work on next]"

### Suggested next actions (priority order):
1. Run Opus autoresearch session to push past Sonnet's 70.22
2. Measure actual token counts with a real tokenizer
3. Integrate best autoresearch config into main hlc/ package
4. Rewrite technical paper with all measured data
5. Build live web demo
6. Format for arXiv and submit

---

*End of living document. Update after every significant work session.*
