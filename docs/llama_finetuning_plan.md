# HLC Phase 5: Llama 3.1 Fine-Tuning Plan

## Goal

Prove that HLC compression translates to real token savings when the model's tokenizer includes HLC symbols in its vocabulary. This closes the token expansion gap discovered in the negative result.

## Architecture

```
Current (broken):
  English text → HLC compress → BPE tokenize → [MORE tokens] → LLM
                                 ↑ BPE doesn't know HLC symbols

Target (fixed):
  English text → HLC compress → HLC-aware BPE tokenize → [FEWER tokens] → Fine-tuned LLM
                                 ↑ Each HLC symbol = 1 token
```

## Two-phase approach

### Phase A: Proof of concept with Qwen3-0.6B ($0, 1-2 hours)

Validate the approach works before spending money.

**Hardware:** Any machine with 8GB+ RAM. Free Google Colab T4 works.

**Steps:**

1. Train custom tokenizer
```python
from tokenizers import Tokenizer, models, trainers, pre_tokenizers
from transformers import AutoTokenizer

# Start from Qwen3's tokenizer
base_tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")

# Add HLC symbols as special tokens
hlc_symbols = list(SYMBOL_MAP.values()) + list(PHRASE_CODEBOOK.values())
base_tokenizer.add_tokens(hlc_symbols)

# Verify each symbol is now 1 token
for sym in hlc_symbols[:10]:
    tokens = base_tokenizer.encode(sym)
    print(f"'{sym}' → {len(tokens)} token(s)")  # Should all be 1
```

2. Generate training data
```python
# Take a large English corpus (e.g., OpenWebText, Wikipedia)
# Compress each passage with HLC
# Create instruction-following pairs:

training_data = []
for passage in english_corpus:
    compressed = hlc_compress(passage)
    training_data.append({
        "instruction": compressed,  # HLC-compressed input
        "output": "understood"      # Or generate a response/summary
    })

# Also include comprehension tasks:
for passage in english_corpus:
    compressed = hlc_compress(passage)
    question = generate_question(passage)  # About the content
    answer = generate_answer(passage, question)
    training_data.append({
        "instruction": f"{compressed}\n\nQuestion: {question}",
        "output": answer
    })
```

3. Fine-tune with LoRA
```python
from transformers import AutoModelForCausalLM
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B")
model.resize_token_embeddings(len(base_tokenizer))  # Expand for new tokens

lora_config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"])
model = get_peft_model(model, lora_config)

trainer = SFTTrainer(
    model=model,
    tokenizer=base_tokenizer,
    train_dataset=training_data,
    max_seq_length=2048,
)
trainer.train()
```

4. Measure token compression
```python
# Compare token counts: original vs HLC-compressed
for text in test_corpus:
    compressed = hlc_compress(text)
    orig_tokens = len(base_tokenizer.encode(text))
    comp_tokens = len(base_tokenizer.encode(compressed))
    ratio = (orig_tokens - comp_tokens) / orig_tokens * 100
    print(f"Token compression: {ratio:.1f}%")
    # Should now be POSITIVE (30-48% savings)
```

5. Test comprehension
```python
# Does the model understand HLC-compressed input?
compressed_prompt = hlc_compress("What is the capital of France?")
response = model.generate(base_tokenizer.encode(compressed_prompt))
# Should answer correctly despite compressed input
```

**Success criteria for Phase A:**
- Each HLC symbol tokenizes to exactly 1 token ✓
- Token compression is positive (target: 30%+) ✓
- Model can answer simple questions from compressed input ✓
- If any of these fail, stop and diagnose before spending money

### Phase B: Publishable result with Llama 3.1 8B ($50-200)

**Model:** meta-llama/Llama-3.1-8B-Instruct

**Why Llama 3.1:**
- Industry-standard benchmarking model (reviewers know it)
- 8B parameters — large enough to be credible, small enough to fine-tune cheaply
- Llama 3.1 community license allows research use
- Well-supported by all fine-tuning platforms

**Platform options (pick one):**

| Platform | Est. cost | Setup time | Notes |
|----------|-----------|------------|-------|
| Together AI | $50-100 | 30 min | Managed, easiest. Upload data → configure → train. |
| Hugging Face Jobs | $50-150 | 30 min | Via Claude Code with hf-llm-trainer skill. |
| Lambda Labs | $100-200 | 1-2 hours | Rent A100 GPU ($1.10/hr), run locally. Full control. |
| RunPod | $80-150 | 1-2 hours | Rent A100 ($0.79/hr community cloud). |
| Google Colab Pro | $50 | 1 hour | A100 available on Pro+ ($50/mo). |

**Recommended: Together AI** for simplicity, or **Lambda Labs** for full control.

**Steps:**

1. Train custom tokenizer (same as Phase A but starting from Llama 3.1's tokenizer)

2. Generate training corpus (larger — 50K-100K examples)
```
Sources:
- OpenWebText (general English)
- Wikipedia articles (knowledge-dense)
- Stack Exchange (technical Q&A)
- RedPajama (diverse web text)

For each source passage (200-500 words):
  a) Compress with HLC
  b) Create instruction pair:
     - Input: HLC-compressed passage + question about the content
     - Output: correct answer in normal English
  c) Also create "translate" pairs:
     - Input: "Decompress: {compressed text}"
     - Output: original English text
```

3. Fine-tune configuration
```yaml
# Together AI config (or equivalent)
model: meta-llama/Llama-3.1-8B-Instruct
method: lora
lora_rank: 32
lora_alpha: 64
learning_rate: 2e-5
batch_size: 4
gradient_accumulation_steps: 4
num_epochs: 3
max_seq_length: 4096
warmup_ratio: 0.1
```

4. Evaluation suite
```
Test 1: Token compression ratio
  - 300 test passages (same categories as autoresearch corpus)
  - Measure orig tokens vs compressed tokens with new tokenizer
  - Target: 30-45% token savings

Test 2: Comprehension accuracy
  - 100 questions about compressed passages
  - Compare accuracy: base model on English vs fine-tuned on HLC
  - Target: >90% accuracy on fine-tuned model

Test 3: Response quality
  - 50 open-ended prompts in HLC-compressed format
  - Human evaluation of response coherence and accuracy
  - Compare against base model on uncompressed prompts

Test 4: Reconstruction accuracy
  - 100 passages: compress → feed to model → ask to decompress
  - Word-for-word comparison with original
  - Target: >95% reconstruction accuracy
```

5. Paper results table (what we're aiming for)
```
| Metric                          | Base (English) | HLC + custom tokenizer |
|---------------------------------|----------------|------------------------|
| Avg tokens per passage          | ~120           | ~70 (42% fewer)        |
| Comprehension accuracy          | 94%            | 91%                    |
| Response coherence (human eval) | 4.2/5          | 3.9/5                  |
| Reconstruction accuracy         | N/A            | 96%                    |
| API cost per 1M passages        | $X             | $0.58X                 |
```

## Timeline

```
Week 1: Phase A (proof of concept)
  Day 1-2: Train custom tokenizer, generate small training set (5K examples)
  Day 3-4: Fine-tune Qwen3-0.6B on Colab, run basic tests
  Day 5:   Evaluate results, decide go/no-go for Phase B

Week 2-3: Phase B (Llama 3.1)
  Day 1-3: Generate full training corpus (50K-100K examples)
  Day 4-5: Set up cloud instance, configure training
  Day 6-7: Fine-tune (4-8 hours of GPU time)
  Day 8-10: Run full evaluation suite
  Day 11-14: Analyze results, write paper section

Week 4: Paper
  Integrate fine-tuning results with existing HLC data
  Write arXiv paper
  Submit
```

## Budget

| Item | Cost |
|------|------|
| Phase A: Qwen3-0.6B on Colab | $0 |
| Phase B: Llama 3.1 fine-tuning (8hrs A100) | $50-200 |
| Training data generation (Claude API for Q&A pairs) | $10-30 |
| Evaluation runs | $5-10 |
| **Total** | **$65-240** |

## Risk factors

1. **Model may not learn HLC symbols well with LoRA alone.** LoRA updates a small subset of weights — it might not be sufficient to teach the model a fundamentally new input encoding. Mitigation: try full fine-tuning on the small model first.

2. **Comprehension may degrade.** Even if tokens compress, the model might understand compressed input less well. Mitigation: measure accuracy, not just compression. A 40% token savings with 20% accuracy loss is not useful.

3. **Reconstruction quality may vary by category.** Technical and legal text may compress differently than casual text. Mitigation: evaluate per-category, report honestly.

4. **Training data quality matters enormously.** Garbage in, garbage out. Mitigation: use high-quality source corpora, validate a sample manually before full training.

## Success criteria

The experiment is a success if:
- Token compression is positive (>25%) with the custom tokenizer
- Comprehension accuracy stays above 85% on compressed input
- The result is reproducible (someone else can replicate with the published config)

The experiment provides valuable data even if it fails — it tells us how much tokenizer integration helps (or doesn't) and what the remaining barriers are.

## Files needed

- `train_tokenizer.py` — adds HLC symbols to Llama's tokenizer
- `generate_training_data.py` — creates compressed instruction pairs
- `finetune.py` (or `finetune.yaml` for Together AI) — training config
- `evaluate.py` — runs the 4-test evaluation suite
- `hlc/compress.py` — the compression pipeline (already exists)
- `autoresearch/config_opus_v2_best.py` — the codebook (already exists)

Want me to write these scripts?
