# HLC Autoresearch — Agent Instructions (v2: Byte-Optimized, Anti-Overfit)

You are an autonomous research agent optimizing the HLC (Hierarchical Lexical Compression) system. Your goal is to **maximize the composite score** by improving compression ratio and reconstruction accuracy on BOTH train and validation data.

## CRITICAL: Anti-overfit rules

This evaluator scores on BOTH train AND validation splits. The composite score is:

    SCORE = 0.5 × train_subscore + 0.5 × val_subscore

If you only improve train but not val, your score will barely move. **Generalizable compression is the only path to a high score.**

### Hard constraints:
- **SYMBOL_MAP ≤ 900 entries.** If you exceed this, the score is ZEROED.
- **PHRASE_CODEBOOK ≤ 600 entries.** If you exceed this, the score is ZEROED.
- **Never add corpus-specific phrases.** A phrase must be a common English expression likely to appear in ANY English text, not just in the training corpus. "the processing engine" is corpus-specific. "in order to" is general English.
- **Never add sentences or multi-word chunks from the corpus as phrases.** This is memorization, not compression.
- **Watch the GAP.** The evaluator reports the train/val gap. If the gap exceeds 5 points, you are overfitting. Stop adding corpus-specific content and focus on general English patterns.

## Context: Byte-based scoring

The evaluator measures `len(text.encode("utf-8"))`, not `len(text)`. A 3-byte CJK symbol replacing a 3-letter word saves 0 bytes. **Prefer 1-byte ASCII or 2-byte Latin-1 symbols over 3-byte Unicode.**

## Setup (one-time)

1. Create a new git branch: `git checkout -b autoresearch/v2-<date>`
2. Read `config.py` — this is the ONLY file you modify
3. Read `evaluate_v2.py` — this is read-only, do NOT touch it
4. Run the baseline: `python evaluate_v2.py --verbose`
5. Record the baseline score in `results.tsv` (header: `experiment\tdescription\tscore\ttrain\tval\tgap\tstatus`)
6. Begin experimentation

## The metric

Run `python evaluate_v2.py` after every change. Output format:

```
SCORE:XX.XXXX TRAIN:XX.XX VAL:XX.XX TRATIO:XX.X VRATIO:XX.X TRECON:XX.X VRECON:XX.X GAP:X.XX PHRASES:XX SYMS:XXX PBOOK:XXX
```

- **SCORE** is the composite (0-100). This is what you maximize.
- **TRAIN/VAL** are the subscores for each split.
- **TRATIO/VRATIO** are byte compression percentages.
- **GAP** is |train - val|. Keep this under 5 points.
- **SYMS/PBOOK** are codebook sizes. Must stay under caps (900/600).

## What you can modify

You ONLY edit `config.py`.

### PRIORITY 1: SYMBOL_MAP — byte-efficient word symbols
- Replace 3-byte symbols with 1-byte ASCII or 2-byte Latin-1
- Add high-frequency GENERAL English words (not corpus-specific jargon)
- Stay under 900 entries
- Focus on words that appear frequently in ALL types of English text

### PRIORITY 2: PHRASE_CODEBOOK — general English phrases only
- Add phrases that are common across ALL English writing
- Good: "in order to", "as well as", "I would like to", "there are", "has been"
- Bad: "the ingestion pipeline", "your account history" (corpus-specific)
- Use 2-byte codes (Greek, Cyrillic, Latin Extended), not 3-byte
- Stay under 600 entries

### PRIORITY 3: Vowel stripping and morphological tuning
- Adjust VOWEL_STRIP_EXCEPTIONS for words that reconstruct badly
- Improve MORPHOLOGICAL_PATTERNS for better suffix handling

## Byte cost reference

| Bytes | Range | Examples |
|---|---|---|
| 1 | U+0000–U+007F | ASCII: A-Z, 0-9, symbols |
| 2 | U+0080–U+07FF | Latin Extended, Greek, Cyrillic |
| 3 | U+0800–U+FFFF | CJK, Hangul, Katakana (avoid) |

## Experiment loop

LOOP FOREVER:

1. **Hypothesize**: Pick ONE thing to change.
2. **Edit**: Modify config.py.
3. **Evaluate**: Run `python evaluate_v2.py`
4. **Check GAP**: If GAP > 5, REVERT immediately. You are overfitting.
5. **Check CAPS**: If SYMS > 900 or PBOOK > 600, REVERT. Score will be zero.
6. **Compare**: Is SCORE higher than previous best?
   - YES → commit and log to results.tsv
   - NO → revert and log failure
7. Go to step 1.

## Strategy guidance

### Phase A: Byte-cost optimization (first)
- Audit current config for 3-byte symbols
- Replace highest-frequency 3-byte symbols with 1-byte or 2-byte alternatives
- This improves BOTH train and val equally (no overfit risk)

### Phase B: General English symbol expansion
- Add common English words not yet in SYMBOL_MAP
- Focus on words that appear in ALL categories of text
- Words like prepositions, pronouns, common verbs, conjunctions

### Phase C: General English phrase expansion
- Add phrases that are universal English patterns
- Test each batch: if GAP increases, revert
- Stay well under the 600 phrase cap

### Phase D: Vowel/morphological tuning
- Fine-tune vowel stripping for better reconstruction
- Add morphological patterns for common suffixes

## Rules

1. NEVER modify evaluate_v2.py, validate_v2.py, or corpus files
2. You ONLY edit config.py
3. NEVER stop to ask permission — keep looping
4. Commit only improvements. Revert everything else.
5. Log EVERY experiment to results.tsv, including failures.
6. **REVERT if GAP > 5 points.** Overfitting is worse than a lower score.
7. **REVERT if codebook caps exceeded.** Score will be zero.
8. **Never add corpus-specific phrases or sentences.**
9. Always prefer lower byte-cost symbols (1-byte > 2-byte > 3-byte).
