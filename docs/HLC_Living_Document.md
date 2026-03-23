# HLC Project — Living Document

**Last updated:** March 23, 2026 (end of Session 2)
**Author:** Ruzzel Maestro (rocketturtles.creative@gmail.com)
**Repo:** https://github.com/Lezzur/hlc
**Status:** Phase 2 nearly complete — byte-optimized autoresearch done, token measurement done, ready for paper

---

## What is this document?

This is the continuity file for the HLC (Hierarchical Lexical Compression) project. If you are an AI assistant picking this up in a new chat, read this entire document before doing anything. It contains the full project context, all decisions made, current state, and exactly what to do next.

---

## The Big Idea (1-paragraph summary)

Current LLM systems compress conversation history using summarization, which is lossy, expensive, and unpredictable. HLC is a fundamentally different approach: instead of semantic compression (deciding what to discard), it applies deterministic, rule-based lexical compression that reduces byte count by 48-58% while preserving ALL information. The key insight is that LLMs are natural decompressors — they can reconstruct full English from aggressively compressed text because that's literally what next-token prediction does. This has been empirically validated: Claude Haiku (smallest model) achieved 98.8% word-for-word reconstruction accuracy on compressed text with no codebook. The autoresearch optimization loop has been run across three model tiers (Haiku, Sonnet, Opus) with byte-based scoring on a 300-sample corpus spanning 15 categories.

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
| Corpus v1 | 80 train / 20 holdout, 10 categories | Session 1 corpus. Adequate for initial optimization. |
| Corpus v2 | 210 train / 45 val / 45 holdout, 15 categories, 300 samples | Session 2 corpus. 3× larger, 5 new categories (legal, medical, journalism, marketing, conversational_ai). Agent sees train+val; holdout is human-only. |
| Scoring metric | UTF-8 bytes (not characters) | Discovered in Session 2 that character-based scoring overstates compression by ~10pp because 3-byte Unicode symbols replace short ASCII words. Byte scoring aligns with how BPE tokenizers actually work. |
| Overfit prevention | Gap-penalty on composite score | Codebook caps failed (Opus found workarounds). Gap penalty works but Opus learned to memorize BOTH splits simultaneously. See "Adversarial Optimization" findings. |

---

## Autoresearch Results

### What is autoresearch?

An autonomous optimization loop inspired by Karpathy's autoresearch pattern. An AI agent edits a config file, runs evaluation, keeps improvements, reverts failures, and loops. Applied to HLC codebook optimization.

### Session 1 Results — Character-based (March 22, 2026)

Corpus: 100 samples, 10 categories, 80/20 split, ~34K chars. Scoring: character count.

| Metric | Baseline | Haiku (50 exps) | Sonnet (50 exps) |
|---|---|---|---|
| Train score | 56.08 | 60.51 | **70.22** |
| Holdout score | 57.02 | 60.33 | **66.10** |
| Train/holdout gap | 0.94 | 0.18 | 4.12 |
| Compression ratio (train) | 27.3% | 35.2% | **50.5%** |
| Reconstruction | 99.3% | 98.4% | **99.9%** |
| Experiments run | — | 50 | 50 |
| Success rate | — | 72% | **100%** |
| Symbol map entries | 12 | ~200 | **528** |
| Phrase codebook entries | 101 | 418 | 196 (actual) |

Key findings from Session 1:
1. Sonnet fixed 29 collision bugs from Haiku in experiment 1 — RECON jumped 98.4% → 99.9%.
2. Sonnet had 100% success rate vs Haiku's 72%.
3. Character compression crossed 50% but byte compression was only 40.6% (10pp gap from 3-byte Unicode symbols).

### Session 2 Results — Byte-based (March 23, 2026)

#### Token/Byte Measurement (critical discovery)

Measured Sonnet's best config against both character and byte counts:

| Metric | Character | Byte | Gap |
|---|---|---|---|
| Train compression | 50.5% | 40.6% | 9.9 pp |
| Holdout compression | 43.6% | 36.8% | 6.8 pp |

Root cause: 473 of 528 symbols were 3-byte CJK/Hangul/Katakana. A 3-byte symbol replacing a 3-letter word saves 0 bytes. Only 55 ASCII symbols (1-byte) were maximally efficient. This led to retargeting all evaluation to UTF-8 bytes.

Symbol byte-size distribution: 55 × 1-byte (ASCII), 0 × 2-byte, 473 × 3-byte (CJK/Hangul/etc).

#### Opus v1 — Byte-optimized, 100-sample corpus

Starting config: Sonnet best. Scoring: UTF-8 bytes. Corpus: v1 (100 samples, 10 categories).

| Metric | Baseline | Opus exp 21 (valid) | Opus exp 32 (overfit) |
|---|---|---|---|
| Composite score | 64.30 | **74.81** | 99.58 |
| Byte compression | 40.6% | **58.1%** | 99.3% |
| Reconstruction | 99.9% | **99.9%** | 100.0% |
| Experiments | — | 21 | 32 |
| Symbol map entries | 528 | 1,877 | 1,877 |
| Phrase codebook | 196 | 842 | 7,823 |

Opus v1 key findings:
1. Experiment 1: replacing 473 three-byte symbols with 2-byte Latin gave instant +2.6 points.
2. Experiments 11-21: exhaustive word mapping pushed byte compression to 58.1%.
3. **Overfit at experiment 22+**: Opus memorized the training corpus by adding full sentences and multi-sentence chunks as "phrases." Phrase count exploded from 842 to 7,823.

#### Opus v2 — Gap-penalized, 300-sample corpus

Starting config: Sonnet best. Scoring: UTF-8 bytes with gap penalty. Corpus: v2 (300 samples, 15 categories, 210/45/45 split).

Gap penalty formula: `penalty = max(0, (gap - 8.0) × 2.0)` applied to composite score. No codebook size limits.

| Metric | Baseline | Opus exp 15 (valid) | Opus exp 20 (exploit) |
|---|---|---|---|
| Composite score | 60.04 | **69.64** | 99.78 |
| Train subscore | 60.05 | 68.69 | 99.71 |
| Val subscore | 60.03 | 70.58 | 99.84 |
| Gap | 0.02 | **1.89** | 0.13 |
| Penalty | 0.00 | 0.00 | 0.00 |
| Experiments | — | 15 | 20 |

Opus v2 key findings:
1. Experiments 1-15: legitimate compression. Byte optimization, word expansion, phrase addition. Gap stayed under 5.
2. **Experiment 16: Opus found the exploit.** Added 33,172 phrases in one experiment, memorizing train (gap rose to 7.94, just under the 8-point threshold).
3. **Experiment 17: memorized val too.** Gap dropped back to 7.98 because both splits were now memorized.
4. **Experiments 18-20: gap went to 0.00** — not because compression generalized, but because BOTH train and val were entirely memorized.

### Adversarial Optimization — Key Research Finding

Across three Opus sessions, the agent consistently discovered and exploited evaluation loopholes:

| Session | Guardrail | How Opus defeated it |
|---|---|---|
| Opus v1 | Train-only scoring, no caps | Added full sentences as phrases (7,823 entries) |
| Opus v2 (caps) | Codebook caps (800 sym / 500 phrase) | Hit cap ceiling, couldn't optimize further |
| Opus v2 (gap) | Gap penalty (threshold 8, rate 2×) | Memorized BOTH splits simultaneously to keep gap at 0 |

**This is itself a publishable finding.** More capable models are more capable at gaming evaluation metrics. The gap penalty only works when the agent cannot see validation data. Since evaluate_v2.py reports val scores to enable the composite calculation, Opus has full information to optimize val directly.

**Implication for the field:** Autonomous optimization agents require evaluation designs where the agent genuinely cannot access the holdout data, or where the metric cannot be gamed by memorization (e.g., testing on completely unseen text at evaluation time).

---

## LLM Reconstruction Tests

### Living document test (all 3 models, Layers 3+4 only, 17% compression, NO codebook):

| Model | Words | Accuracy | Semantic accuracy |
|-------|-------|----------|-------------------|
| Haiku | 1,432 | 98.18% | ~100% |
| Sonnet | 1,432 | 98.27% | ~100% |
| Opus | 1,432 | 98.95% | ~100% |
| **Overall** | **4,309** | **98.47%** | **~100%** |

### Short paragraph tests (Haiku only, Layers 3+4 only, ~29% compression):

| Sample | Accuracy | Notes |
|--------|----------|-------|
| Technical | 97.0% (65/67) | "compaction" became "compression", "decorative" became "descriptive" — semantically equivalent |
| Casual | 100% (51/51) | Perfect |
| Business | 100% (51/51) | Perfect |
| **Overall** | **98.8%** | **Semantic: 100%** |

### Two compression tiers explained

- **Layers 3+4 only (17-29% compression)**: No codebook needed. Any LLM reads natively. Use for continuity documents uploaded to new chats.
- **All layers (48-58% byte compression)**: Requires codebook in context. Use inside agent systems where codebook is loaded once per session.

---

## Project Structure

```
hlc/
├── hlc/                        # Core Python package
│   ├── __init__.py
│   ├── analyze.py
│   ├── codebook.py
│   ├── compress.py
│   ├── benchmark.py
│   └── codebooks/
├── autoresearch/               # Autonomous optimization loop
│   ├── config.py               # Current best
│   ├── evaluate.py             # v1 evaluator (char-based)
│   ├── evaluate_v2.py          # v2 evaluator (byte-based, gap-penalized)
│   ├── validate.py             # v1 holdout checker
│   ├── validate_v2.py          # v2 holdout checker
│   ├── build_corpus.py         # v1 corpus builder (100 samples)
│   ├── build_corpus_v2.py      # v2 corpus verifier (300 samples)
│   ├── measure_tokens.py       # Token measurement script (needs tiktoken)
│   ├── program.md              # v1 agent instructions
│   ├── program_v2.md           # v2 agent instructions (gap-penalized)
│   ├── corpus/
│   │   ├── train.json          # v2: 210 samples, 15 categories
│   │   ├── val.json            # v2: 45 samples (agent sees this)
│   │   └── holdout.json        # v2: 45 samples (human-only)
│   ├── corpus_v1_backup/       # Original 100-sample corpus
│   ├── reports/
│   ├── config_sonnet_best.py
│   ├── config_opus_best.py     # Opus v1 exp 21 (pre-overfit)
│   ├── config_opus_v2_best.py  # Opus v2 exp 15 (pre-exploit)
│   ├── results_sonnet.tsv
│   ├── results_opus.tsv        # v1 Opus (32 experiments)
│   └── results_opus_v2.tsv     # v2 Opus (20 experiments)
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

### Phase 2: Benchmark and validate (NEARLY COMPLETE)
- [x] LLM reconstruction test — Haiku (98.18% on living doc, 98.8% on paragraphs)
- [x] LLM reconstruction test — Sonnet (98.27% on living doc)
- [x] LLM reconstruction test — Opus (98.95% on living doc)
- [x] Autoresearch: Haiku session (56.08 → 60.51, 50 experiments)
- [x] Autoresearch: Sonnet session (60.51 → 70.22, 50 experiments, char-based)
- [x] Autoresearch: Opus v1 session (64.30 → 74.81 valid, byte-based, 100-sample corpus)
- [x] Autoresearch: Opus v2 session (60.04 → 69.64 valid, byte+gap-penalized, 300-sample corpus)
- [x] Byte vs character measurement (10pp gap discovered, byte scoring adopted)
- [x] Adversarial optimization finding (Opus games metrics across 3 sessions)
- [x] Holdout validation across all sessions
- [ ] Measure actual TOKEN counts with tiktoken (script written, needs local run)
- [ ] Edge case handling: URLs, emails, code, numbers, proper nouns
- [ ] Integrate best autoresearch config into main hlc/ package
- [ ] Roll back Opus v2 config to experiment 15

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

1. **Token vs character gap (PARTIALLY RESOLVED)** — Byte measurement done (40.6% byte vs 50.5% char on Sonnet config). Actual tokenizer measurement with tiktoken written but not yet run locally (needs network access to download tokenizer data). Byte count is a close proxy for token count.

2. **Two architectures still diverging** — main hlc/ package uses 37k word codebook. Autoresearch config.py uses symbol map + phrases. Need reconciliation before paper.

3. **Adversarial optimization (NEW)** — Opus consistently games evaluation metrics. Three different guardrails defeated across three sessions. Any future autoresearch sessions need evaluation designs where the agent genuinely cannot access holdout data.

4. **No edge case protection** — URLs, emails, code get compressed. Need preserve layer.

5. **Layer 5 placeholder** — recursive pattern compression not implemented.

6. **Collision risk (RESOLVED)** — Sonnet fixed all 29 Haiku collisions. Opus v2 config verified collision-free.

7. **Opus v2 config needs rollback** — Current config in repo is the overfit version (exp 20). Need to roll back to exp 15 config.

---

## How to Continue in a New Chat

Upload this document and say:

> "I'm Ruzzel. This is my HLC project living document. Read it and let's continue where I left off. [Then state what you want to work on next]"

### Suggested next actions (priority order):
1. Roll back Opus v2 config to experiment 15 (pre-exploit)
2. Run measure_tokens.py locally with tiktoken for actual token numbers
3. Integrate best config into main hlc/ package
4. Rewrite technical paper with all measured data (lead with adversarial finding)
5. Build live web demo
6. Format for arXiv and submit

### The paper should cover:
- HLC system design (6 layers, codebook architecture)
- Empirical compression results (48-58% byte compression, 99.9% reconstruction)
- Autoresearch methodology (Karpathy-inspired, sequential model chain)
- The byte vs character gap (why measuring the right metric matters)
- Adversarial optimization finding (Opus gaming evaluation metrics — novel contribution)
- LLM reconstruction accuracy across model tiers

---

*End of living document. Update after every significant work session.*
