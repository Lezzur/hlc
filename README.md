# HLC — Hierarchical Lexical Compression

**A lossless compression system for reducing LLM token costs and extending context windows.**

HLC applies deterministic, rule-based compression to natural language text, achieving **34-48% byte compression** with **99.9% reconstruction accuracy**. By replacing common words and phrases with compact Unicode symbols, it reduces the physical size of text while preserving all information for LLM reconstruction.

## Current Status (Session 2 Complete)

### ✓ What Works
- **Byte Compression**: 34-48% reduction across 15 text categories (300-sample v2 corpus)
- **Reconstruction Quality**: 99.9% accuracy (validated across Haiku, Sonnet, and Opus)
- **Adversarial Robustness**: Tested via automated optimization (32 experiments w/ Opus v1, 20 w/ Opus v2)

### ⚠ Critical Finding: Token Expansion
Using tiktoken to measure actual token counts with cl100k_base (GPT-4) and o200k_base (GPT-4o):

| Config | Byte Compression | Token "Compression" | Byte→Token Gap |
|--------|------------------|---------------------|----------------|
| Sonnet Best (724 entries) | 33.5% | **-81.3%** (expansion) | 114.8pp |
| Opus v2 Best (1737 entries) | 47.9% | **-70.5%** (expansion) | 118.4pp |

**Root cause:** BPE tokenizers (used by GPT, Claude, Llama) encode unfamiliar Unicode symbols as 2-3 tokens each. HLC compresses bytes but **expands tokens** by 70-81%.

### Why This Matters
Token expansion makes HLC **cost-prohibitive** with standard tokenizers:
- A 10K token conversation → 18K tokens after compression (81% more expensive)
- Byte savings are invisible to the LLM's billing and context window
- No production viability without token-aware design

For full context, see [docs/hlc_negative_result.md](docs/hlc_negative_result.md).

## Path Forward: Phase 5 (Custom Tokenizer)

The solution is to **control the tokenizer**:

1. **Train a custom BPE tokenizer** that natively recognizes HLC's Unicode symbols as single tokens
2. **Fine-tune Llama 3.1 8B** on the custom tokenizer to maintain language understanding
3. **Redeploy HLC on top** of the fine-tuned model

Expected outcome:
- Byte compression: 40-50% (unchanged)
- Token compression: 35-45% (matched to byte compression)
- Cost reduction: 40-50% per message
- Context extension: 2x effective window size

See [docs/llama_finetuning_plan.md](docs/llama_finetuning_plan.md) for the detailed implementation plan.

## Quick Start

```bash
git clone https://github.com/Lezzur/hlc.git
cd hlc
pip install -r requirements.txt
```

```python
from hlc import compress, decompress

text = "The compaction quality is bounded by the compacting model's ability."
compressed = compress(text)
print(compressed)  # "^ cmpctn 刳 $ 12880 by ^ 3905ng 28729..."

# Deterministic decompression
decompressed = decompress(compressed)
```

Run benchmarks:
```bash
python -m hlc.benchmark
```

## Project Structure

```
hlc/
├── hlc/                    # Core compression engine
│   ├── compress.py         # Compression + decompression
│   ├── codebook.py         # Unicode symbol mapping
│   ├── benchmark.py        # Evaluation suite
│   └── codebooks/          # Codebook data
├── autoresearch/           # Automated optimization sessions
│   ├── config_sonnet_best.py   # Best config from Sonnet (21 exps)
│   ├── config_opus_best.py     # Best config from Opus v1 (32 exps)
│   ├── config_opus_v2_best.py  # Best config from Opus v2 (20 exps)
│   ├── corpus/             # v2 corpus (210 train, 45 val, 45 holdout)
│   └── measure_tokens.py   # Tiktoken measurement tool
├── docs/
│   ├── HLC_Living_Document.md      # Full project context
│   ├── hlc_negative_result.md      # Token expansion finding
│   └── llama_finetuning_plan.md    # Phase 5 implementation
├── reports/
│   └── token_measurement.md    # Tiktoken results (Sonnet vs Opus v2)
└── examples/               # Usage examples
```

## Session History

- **Session 1 (Mar 21)**: Initial implementation, character-level compression (50-60%)
- **Session 2 (Mar 22-23)**: Byte measurement, tiktoken analysis, adversarial optimization, negative result discovery

## Documentation

- **Living Document**: [docs/HLC_Living_Document.md](docs/HLC_Living_Document.md) — Complete project history, findings, and roadmap
- **Negative Result**: [docs/hlc_negative_result.md](docs/hlc_negative_result.md) — Token expansion analysis
- **Phase 5 Plan**: [docs/llama_finetuning_plan.md](docs/llama_finetuning_plan.md) — Custom tokenizer + Llama fine-tuning

## Contributing

This project is in the research/negative-result phase. If you're interested in:
- Custom tokenizer training (BPE/SentencePiece)
- Llama/Mistral fine-tuning infrastructure
- Token-aware compression design
- Corpus expansion for training data

Please reach out: rocketturtles.creative@gmail.com

## Author

**Ruzzel Maestro** — Independent Researcher

## License

See [LICENSE](LICENSE) for details.
