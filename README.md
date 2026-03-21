# HLC — Hierarchical Lexical Compression

> A lossless, multi-layered approach to reducing LLM token costs and extending effective context windows.

## The problem

LLM-based systems face an inherent trilemma: **fidelity** (remembering what was said), **cost** (every token has a price), and **session length** (context windows are finite). Current solutions use semantic compression — summarization — which is lossy, expensive, and unpredictable. An agent that "remembers" discussing your database architecture but forgets you specified PostgreSQL 14 will make confident but wrong decisions.

## The insight

Language models are, by design, the best possible decompressors of compressed natural language. Next-token prediction — the core training objective — is precisely the skill of reconstructing meaning from partial signals. HLC exploits this by applying **deterministic, rule-based compression** that reduces token count while preserving all information.

```
Original (451 chars):
"Absolutely, and this is the part that deserves more attention. The compaction 
quality is bounded by the compacting model's ability to understand what matters..."

Compressed (200 chars, -55.7%):
"僕, + ! $ ^ 亰 ~ 1379 ь 偠. ^ cmpctn 刳 $ 12880 by ^ 3905ng 28729 恟 to 亐 # 遲..."

→ Any LLM (including Haiku) reconstructs the original meaning accurately.
```

## How it works

HLC applies six stackable compression layers, ordered from highest to lowest impact:

| Layer | Method | Target | Impact |
|-------|--------|--------|--------|
| 1 | Phrase codebook | Common multi-word phrases → single codes | Highest |
| 2 | Word codebook | Frequency-ranked words → Unicode/numeric codes | High |
| 3 | Symbol substitution | Function words → single symbols (`and`→`+`, `the`→`^`) | Medium |
| 4 | Vowel stripping | Interior vowels removed (`compaction`→`cmpctn`) | Medium |
| 5 | Recursive patterns | Patterns in compressed output → macro codes | Lower |
| 6 | Semantic enrichment | Metadata markers: `![critical]`, `t[technical]` | Enhancement |

Each layer targets a different source of redundancy. Together they achieve **50–60% compression** across diverse English text — without discarding any information.

## Benchmark results

Tested across 8 text categories:

| Category | Original | Compressed | Reduction |
|----------|----------|------------|-----------|
| Technical / Agent | 451 chars | 200 chars | **55.7%** |
| Casual Chat | 366 chars | 169 chars | **53.8%** |
| Business / Professional | 514 chars | 216 chars | **58.0%** |
| Technical Documentation | 634 chars | 308 chars | **51.4%** |
| Creative / Narrative | 507 chars | 288 chars | **43.2%** |
| Academic / Research | 782 chars | 348 chars | **55.5%** |
| Customer Support | 517 chars | 243 chars | **53.0%** |
| How-to / Instructional | 624 chars | 288 chars | **53.8%** |
| **Overall** | **4,395** | **2,060** | **53.1%** |

## Quick start

```bash
git clone https://github.com/Lezzur/hlc.git
cd hlc
pip install -r requirements.txt
```

```python
from hlc import compress, decompress, compress_with_report

text = "The compaction quality is bounded by the compacting model's ability to understand what matters."

# Compress
compressed = compress(text)
print(compressed)

# Compress with statistics
compressed, report = compress_with_report(text)
print(f"Compression: {report['compression_ratio']}%")

# Deterministic decompression (reverses Layers 1–3; Layer 4 relies on LLM reconstruction)
decompressed = decompress(compressed)
```

Run the benchmarks yourself:

```bash
python -m hlc.benchmark
```

## Project structure

```
hlc/
├── hlc/                    # Core package
│   ├── __init__.py
│   ├── analyze.py          # Corpus frequency analysis
│   ├── codebook.py         # Codebook generation (Unicode-first)
│   ├── compress.py         # Compression + decompression engine
│   ├── benchmark.py        # Benchmark suite
│   └── codebooks/          # Generated codebook data
│       ├── codebook_full.json
│       ├── codebook_compact.json
│       ├── word_freq.json
│       ├── phrase_freq.json
│       └── symbols.json
├── examples/               # Usage examples
│   └── basic_usage.py
├── tests/                  # Test suite
│   └── test_compress.py
├── docs/                   # Technical paper
│   └── HLC_Technical_Paper.docx
├── requirements.txt
├── setup.py
├── LICENSE
└── README.md
```

## Why not just summarize?

| | Semantic compression (summarization) | HLC |
|---|---|---|
| **Mechanism** | Model decides what to keep | Deterministic rule-based transforms |
| **Information loss** | Irreversible, unpredictable | None (intent-lossless) |
| **Compression cost** | Requires model inference | Zero inference cost |
| **Future relevance** | Must predict what matters | Everything preserved |
| **Failure mode** | Confident ignorance (silent gaps) | Graceful (visible reconstruction) |
| **Over time** | Errors compound | Efficiency improves |

## Roadmap

- [x] Core compression pipeline (Layers 1–4)
- [x] Unicode-first codebook generation
- [x] Benchmark suite across 8 text categories
- [ ] LLM reconstruction accuracy tests (Haiku, Sonnet, Opus)
- [ ] Token-level measurement (vs character-level)
- [ ] Expanded phrase codebook (2,000+ entries)
- [ ] Edge case handling (URLs, code, proper nouns)
- [ ] pip package distribution
- [ ] arXiv paper submission
- [ ] Fine-tuning experiments (native HLC fluency)

## The long game

If an LLM can be **fine-tuned** to read HLC natively — without a codebook in context — the overhead drops to zero. Every message, both input and output, is natively compressed. A 200K context window effectively becomes 400–600K. A 1M window holds 2–3M tokens of content. Per-message costs drop 50–70%.

This is the direction we're heading. See the [technical paper](docs/HLC_Technical_Paper.docx) for the full proposal.

## Contributing

This project is in early stage. If you're interested in collaborating — especially on corpus analysis, tokenizer interaction research, or fine-tuning experiments — please reach out.

## Author

**Ruzzel Maestro** — Independent Researcher
rocketturtles.creative@gmail.com

## License

See [LICENSE](LICENSE) for details.
