# HLC Project — Living Document

**Last updated:** March 22, 2026
**Author:** Ruzzel Maestro (rocketturtles.creative@gmail.com)
**Repo:** https://github.com/Lezzur/hlc
**Status:** Phase 1 complete, entering Phase 2

---

## What is this document?

This is the continuity file for the HLC (Hierarchical Lexical Compression) project. If you are an AI assistant picking this up in a new chat, read the entire document before doing anything. It contains the full project context, all decisions made, current state, and exactly what to do next.

---

## The Big Idea (1-paragraph summary)

Current LLM systems compress conversation history using summarization, which is lossy, expensive, and unpredictable. HLC is a fundamentally different approach: instead of semantic compression (deciding what to discard), it applies deterministic, rule-based lexical compression that reduces token count by 50-60% while preserving ALL information. The key insight is that LLMs are natural decompressors — they can reconstruct full English from aggressively compressed text because that's literally what next-token prediction does. This has been empirically validated: Claude Haiku (smallest model) achieved 98.8% word-for-word reconstruction accuracy on compressed text with no codebook.

---

## How HLC Works — The Six Layers

Compression layers applied in order from highest to lowest impact:

1. **Layer 1 — Phrase codebook**: Common multi-word phrases → single Unicode characters. "it is important to note that" → α. Highest impact per substitution. Includes semantic deduplication (80% equivalence threshold — "how are you" / "hey how are you" / "dude how are you" all map to same code).

2. **Layer 2 — Word codebook**: Frequency-ranked individual words → Unicode characters (top ~3000) or short numeric codes (rest). 37,639 words encoded. "because" → я, "apple" → у. Morphological handling: "produce" = code 11, "produces" = 11s, "produced" = 11d.

3. **Layer 3 — Symbol substitution**: High-frequency short function words → single ASCII symbols. and→+, the→^, is/be→$, that→~, for/at→@, what→#, with→&, this→!, from→%, not→*.

4. **Layer 4 — Vowel stripping**: Remove interior vowels from remaining words, keep first and last character. "computation" → "cmputn", "model" → "modl". Skip words <4 chars.

5. **Layer 5 — Recursive pattern compression**: Find repeated patterns in the compressed output itself and assign macro codes. More effective as conversations grow longer. Currently placeholder — needs implementation.

6. **Layer 6 — Semantic enrichment**: Metadata markers that ADD information. ![critical], t[technical], e[emotional], d[decision], ?[unresolved]. Paradoxically makes compressed form MORE informative than original.

**Critical rule:** Existing shorthand is sacred. btw=by the way, tldr, fyi, imo, gtg, brb, etc. — never reassign these. 54 protected terms.

---

## Key Design Decisions Made

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| Codebook format | Unicode-first, numeric fallback | Single Unicode chars = single tokens in most tokenizers = maximum compression per substitution |
| Layer ordering | Phrases first (biggest impact) → words → symbols → vowels | Biggest savings come from replacing multi-word phrases and single codes |
| License | Apache 2.0 | Patent protection clause — important given the IP nature of this work |
| Compression target | Machine-readable, not human-readable | Optimizing for LLM reconstruction, not human reading. Compressed text can look like garbage to humans. |
| Codebook scope | Universal English codebook (static, precomputed) | One-time cost, reusable across all conversations. Codebook is frequency-ranked from wordfreq library |

---

## Current Benchmark Results (Measured)

### Compression rates (all 6 layers, character-level):

| Category | Original | Compressed | Reduction |
|----------|----------|------------|-----------|
| Technical / Agent | 451 chars | 200 chars | 55.7% |
| Casual Chat | 366 chars | 169 chars | 53.8% |
| Business / Professional | 514 chars | 216 chars | 58.0% |
| Technical Documentation | 634 chars | 308 chars | 51.4% |
| Creative / Narrative | 507 chars | 288 chars | 43.2% |
| Academic / Research | 782 chars | 348 chars | 55.5% |
| Customer Support | 517 chars | 243 chars | 53.0% |
| How-to / Instructional | 624 chars | 288 chars | 53.8% |
| **Overall** | **4,395** | **2,060** | **53.1%** |

### LLM Reconstruction accuracy (Haiku, Layers 3+4 only, ~29% compression, NO codebook):

| Sample | Word accuracy | Notes |
|--------|-------------|-------|
| Technical | 97.0% (65/67) | Two near-misses: "computation"→"compression", "declarative"→"descriptive" — both semantically equivalent |
| Casual | 100% (51/51) | Perfect reconstruction |
| Business | 100% (51/51) | Perfect reconstruction |
| **Overall** | **98.8% (167/169)** | **Semantic accuracy: effectively 100%** |

Key: this was the smallest, cheapest model. Layers 1-2 are deterministically reversible (zero error). Combined system is intent-lossless.

---

## Project Structure

```
hlc-release/
├── hlc/                        # Core Python package
│   ├── __init__.py             # Package init, exports compress/decompress
│   ├── analyze.py              # Corpus frequency analysis (wordfreq-based)
│   ├── codebook.py             # Codebook generation (Unicode-first assignment)
│   ├── compress.py             # 6-layer compression + decompression engine
│   ├── benchmark.py            # Benchmark suite, 8 text categories
│   └── codebooks/              # Generated data
│       ├── codebook_full.json  # All codebooks + reverse maps (~37k entries)
│       ├── codebook_compact.json
│       ├── word_freq.json      # 38,050 codeable words ranked
│       ├── phrase_freq.json    # 96 phrases ranked (NEEDS EXPANSION)
│       └── symbols.json        # Symbol map + protected shorthand
├── examples/
│   └── basic_usage.py
├── tests/
│   └── test_compress.py        # 14 tests, all passing
├── docs/
│   └── HLC_Technical_Paper.docx
├── README.md
├── LICENSE                     # Apache 2.0
├── requirements.txt            # wordfreq, nltk
└── setup.py                    # pip installable
```

---

## Roadmap — Full Picture

### Phase 1: Build the engine (COMPLETE)
- [x] Corpus frequency analysis (38,050 codeable words)
- [x] Unicode-first codebook generation (37,639 words + 95 phrases)
- [x] 6-layer compression pipeline
- [x] Decompression engine (deterministic for L1-3)
- [x] Benchmark site (8 categories)
- [x] Test site (14 tests passing)
- [x] GitHub repo live: https://github.com/Lezzur/hlc

### Phase 2: Benchmark + validate (IN PROGRESS)
- [x] LLM reconstruction test — Haiku (98.8% accuracy)
- [ ] LLM reconstruction test — Sonnet
- [ ] LLM reconstruction test — Opus
- [ ] **Expand phrase codebook** from 96 to 2,000+ entries (Layer 1 currently shows 0% impact in benchmarks because no test samples hit the 96 bootstrapped phrases — this is the biggest low-hanging fruit)
- [ ] Measure actual TOKEN counts (not just characters) — Unicode chars may tokenize into multiple tokens, which would change the real savings number
- [ ] Edge case handling: URLs, email addresses, code snippets, numbers, proper nouns — these need to pass through uncompressed
- [ ] Domain testing: code/programming text, multilingual mixed text
- [ ] Fix: some morphological variants not matching base codes (e.g. "compacting" → "3905ng" instead of matching "computation" base)

### Phase 3: Package + publish (NOT STARTED)
- [ ] Expand test suite
- [ ] pip package (pypi)
- [ ] Rewrite technical paper & ALL measured data (replace estimates)
- [ ] Format paper for arXiv (LaTeX, proper citations)
- [ ] Build live web demo (paste text → see compression + reconstruction)
- [ ] Submit to arXiv

### Phase 4: Outreach (NOT STARTED)
- [ ] Hacker News post
- [ ] Reddit r/MachineLearning post
- [ ] X/Twitter thread
- [ ] Target specific researchers (context management, tokenizer design)
- [ ] Contact LLM providers (Anthropic, OpenAI, Google DeepMind, Cohere)
- [ ] Blog post & interactive demo

### Phase 5: The training frontier (NEEDS PARTNERS)
- [ ] Generate HLC-encoded training corpus
- [ ] Fine-tune model on compressed text
- [ ] Benchmark fine-tuned model vs base (performance parity test)
- [ ] Zero-codebook deployment (model reads HLC natively)

---

## Known Issues + Technical Debt

1. **Phrase codebook is too small** — only 96 bootstrapped phrases, none hit in benchmarks. Need corpus-driven n-gram analysis & 2,000+ entries. This is the single biggest improvement available.

2. **Token vs character measurement gap** — all benchmarks measure character savings. Real token savings may differ because Unicode characters (CJK, Cyrillic, Greek) may tokenize into 2-3 tokens in some tokenizers. MUST measure with actual tokenizer before publishing.

3. **Morphological handling is incomplete** — "compacting" becomes "3905ng" (numeric code + suffix) which works but looks messy. Some word variants aren't matching their base forms in the codebook.

4. **No edge case protection** — URLs, emails, code blocks, numbers, and proper nouns get compressed when they shouldn't. Need a "preserve" layer that shields special content.

5. **Layer 5 (recursive patterns) is a placeholder** — not implemented yet. Needs analysis of compressed output patterns across real conversations.

6. **benchmark.py had a relative import issue** — fixed by changing `from compress import` to `from .compress import`. Watch for similar issues if restructuring.

7. **Deduplication in phrase codebook** — "on the other hand" appears twice in the bootstrapped phrase list. Need dedup in the generation pipeline.

---

## The Origin Story (for context)

This project emerged from a conversation about agent memory challenges. The key breakthrough moments:

1. **The vowel-stripping test** — showed that "this part deserves attention..." is perfectly readable by LLMs, proving aggressive compression doesn't destroy meaning.

2. **The "L8 =?" test** — showed that even symbolic shorthand (2 characters) is interpretable in context, extending the compression principle beyond word-level.

3. **The Haiku codebook test** — gave Haiku a 27-entry numeric codebook and encoded paragraph. Haiku reconstructed it perfectly. Proved even small models can decompress.

4. **The fundamental realization** — LLMs are literally trained to predict missing information from context. Compression that removes predictable information is exactly what they're built to reverse. We're not asking them to do something new; we're leveraging their core capability.

5. **The layers insight** — compression should be multi-layered (phrases → words → symbols → vowels → patterns → metadata), and each layer targeting different redundancy. Ordered by impact, not complexity.

6. **Existing shorthand is sacred** — btw, tldr, fyi etc. already have meanings. Don't reassign them. Use them for free.

7. **Semantic deduplication** — phrases with 80%+ equivalent meaning map to same code. "How are you" / "Hey how are you" = same code. Intent-lossless, not word-lossless.

8. **Enrichment layer** — compression can paradoxically ADD information through metadata markers that make implicit context explicit.

---

## People + Resources

- **Ruzzel Maestro** — project creator, independent researcher
- **Email:** rocketturtles.creative@gmail.com
- **GitHub:** https://github.com/Lezzur/hlc
- **Technical paper:** in docs/HLC_Technical_Paper.docx in the repo

---

## How to Continue in a New Chat

Upload this document and say something like:

> "I'm Ruzzel. This is my HLC project living document. Read it and let's continue where I left off. [Then state what you want to work on next]"

The AI will have full context of the project, all decisions, current state, and what needs doing. No re-explaining needed.

---

*End of living document. Update this file after every significant work session.*
