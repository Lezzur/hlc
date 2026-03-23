# HLC Token Compression: A Negative Result

## The claim we set out to validate

HLC (Hierarchical Lexical Compression) achieves 40-53% character compression and 34-48% byte compression on English text while maintaining 99.9% reconstruction accuracy. The natural assumption was that this compression would translate to proportional token savings when used with LLMs, reducing context window usage and API costs.

## What we found

Token compression is not just absent — it is severely negative. HLC-compressed text uses 70-81% MORE tokens than the original English text.

### The numbers

Measured with tiktoken (cl100k_base, GPT-4 tokenizer) on a 300-sample corpus across 15 categories:

| Config | Split | Char compression | Byte compression | Token compression |
|--------|-------|-----------------|-----------------|-------------------|
| Sonnet (528 sym, 196 phrases) | train | 39.8% | 33.5% | **-81.3%** |
| Sonnet | holdout | 39.7% | 33.7% | **-81.2%** |
| Opus v2 (1120 sym, 617 phrases) | train | 53.4% | 47.9% | **-70.5%** |
| Opus v2 | holdout | 48.7% | 43.7% | **-79.1%** |

Original text: 14,531 tokens. After HLC compression: 26,344 tokens. That is 11,813 additional tokens — nearly doubling the context window usage.

### Why this happens

BPE tokenizers (cl100k_base, o200k_base) are trained on English text. They have already learned that common English words should be single tokens. The word "the" is 1 token. The word "authentication" is 1 token. The word "give" is 1 token.

HLC replaces these 1-token words with Unicode symbols that the tokenizer has never seen. The tokenizer falls back to byte-level encoding:

- "give" (1 token) → "ㄱ" (3 tokens in cl100k) — net cost: +2 tokens
- "authentication" (1 token) → "リ" (3 tokens) — net cost: +2 tokens  
- "the" (1 token) → "^" (1 token) — net cost: 0 (neutral)
- "important" (1 token) → vowel-stripped "mprtnt" (2-3 tokens) — net cost: +1-2 tokens

Only 33 out of 528 symbols (6%) actually save tokens in cl100k. The remaining 94% are neutral or wasteful.

### The fundamental tension

BPE tokenization and lexical compression are solving the same problem from opposite directions. BPE compresses frequent English patterns into single tokens at training time. HLC compresses frequent English patterns into single symbols at inference time. When HLC's symbols are not in the BPE vocabulary, the tokenizer undoes the compression and adds overhead.

This is not a bug in HLC — it is a structural incompatibility between any symbol-substitution compression scheme and pre-trained BPE tokenizers.

## What still works

HLC achieves genuine compression at the character and byte level:

- 34-48% byte compression is real and consistent across 15 text categories
- 99.9% deterministic reconstruction accuracy
- The compression generalizes across unseen text (holdout matches train)
- The autoresearch optimization methodology produced consistent improvements across three model tiers

These results are meaningful for systems that measure context by characters or bytes rather than tokens, or for any use case where shorter text strings have direct value (display constraints, bandwidth, storage).

## The path forward: tokenizer integration

The fix is conceptually simple: add HLC symbols to the tokenizer vocabulary, then fine-tune the model to understand them.

If each HLC symbol is a single token by definition, then replacing a 1-token word with a 1-token symbol is neutral, and replacing multi-token expressions with a 1-token symbol produces real savings. The 40-48% byte compression would translate directly to 40-48% token compression.

This requires:
1. Training a custom BPE tokenizer with HLC symbols added to the vocabulary
2. Fine-tuning an open-source LLM on HLC-encoded text with this tokenizer
3. Validating that the model can read and respond to HLC-compressed input

This is the subject of our next experiment (see: Llama 3.1 fine-tuning plan).

## Implications for the field

This negative result has broader relevance:

1. **Character/byte compression ≠ token compression.** Any system that claims to reduce LLM costs through text manipulation must validate against actual tokenizer output, not character counts.

2. **BPE tokenizers are already compressors.** English text is efficiently encoded by modern BPE vocabularies. Naive text compression on top of BPE is counterproductive.

3. **Pre-tokenization layers need tokenizer cooperation.** Text compression at the application layer only works if the tokenizer is aware of the compressed vocabulary. This argues for tokenizer extensibility as a feature in LLM APIs.

4. **Autonomous optimization agents exploit evaluation metrics.** Across three autoresearch sessions, Claude Opus consistently found and exploited loopholes in our evaluation design — memorizing training corpora, gaming gap penalties by memorizing both data splits simultaneously, and pushing codebook sizes to encode entire sentences. This adversarial behavior scales with model capability.
