# HLC Autoresearch — Agent Instructions (v2: Byte-Optimized, Gap-Penalized)

You are an autonomous research agent optimizing the HLC (Hierarchical Lexical Compression) system. Your goal is to **maximize the composite score** by improving compression ratio and reconstruction accuracy on BOTH train and validation data.

## CRITICAL: How overfitting is penalized

This evaluator scores on BOTH train AND validation splits. The composite score is:

    raw_score = 0.5 × train_subscore + 0.5 × val_subscore
    gap = |train_subscore - val_subscore|
    penalty = max(0, (gap - 8.0) × 2.0)
    SCORE = raw_score - penalty

**What this means:**
- A gap under 8 points is free — normal variance between splits.
- A gap of 10 costs 4 points. A gap of 15 costs 14 points. A gap of 20 costs 24 points.
- The penalty grows faster than any train-only gain from memorization.
- **The only way to maximize SCORE is to improve BOTH train and val equally.**
- There are no codebook size limits. Use as many symbols and phrases as you want. But if they only help train and not val, the gap penalty will eat your gains.

### Guidelines to keep the gap low:
- **Add general English patterns**, not corpus-specific phrases. "in order to" helps both splits. "The patient presents with a four-day history" only helps train.
- **Watch the GAP number after every experiment.** If it jumps, the change is overfitting.
- **Word symbols are safe.** Common English words appear in both splits. Symbol expansion rarely increases the gap.
- **Phrases are riskier.** Long or specific phrases may only match train text. Test in small batches and check GAP.

## Context: Byte-based scoring

The evaluator measures `len(text.encode("utf-8"))`, not `len(text)`. A 3-byte CJK symbol replacing a 3-letter word saves 0 bytes. **Prefer 1-byte ASCII or 2-byte Latin-1 symbols over 3-byte Unicode.**

## Setup (one-time)

1. Create a new git branch: `git checkout -b autoresearch/v2-<date>`
2. Read `config.py` — this is the ONLY file you modify
3. Read `evaluate_v2.py` — this is read-only, do NOT touch it
4. Run the baseline: `python evaluate_v2.py --verbose`
5. Record the baseline score in `results.tsv` (header: `experiment\tdescription\tscore\ttrain\tval\tgap\tpenalty\tstatus`)
6. Begin experimentation

## The metric

Run `python evaluate_v2.py` after every change. Output format:

```
SCORE:XX.XXXX TRAIN:XX.XX VAL:XX.XX TRATIO:XX.X VRATIO:XX.X TRECON:XX.X VRECON:XX.X GAP:X.XX PENALTY:X.XX PHRASES:XX SYMS:XXX PBOOK:XXX
```

- **SCORE** is the composite after penalty (0-100). This is what you maximize.
- **TRAIN/VAL** are the subscores for each split.
- **GAP** is |train - val|. Under 8 = free. Above 8 = penalty kicks in.
- **PENALTY** is the points deducted. Zero when gap < 8.
- **SYMS/PBOOK** are codebook sizes (no hard limits, but overfitting shows up in GAP).

## What you can modify

You ONLY edit `config.py`.

### PRIORITY 1: SYMBOL_MAP — byte-efficient word symbols
- Replace 3-byte symbols with 1-byte ASCII or 2-byte Latin-1
- Add high-frequency general English words
- Word symbols are the safest way to improve score — common words appear in both splits
- Focus on words that appear frequently in ALL types of English text

### PRIORITY 2: PHRASE_CODEBOOK — general English phrases
- Add phrases that are common across ALL English writing
- Good: "in order to", "as well as", "I would like to", "there are", "has been", "would be"
- Risky: domain-specific phrases that may only appear in some categories
- Test phrase additions in small batches and check GAP after each
- Use 2-byte codes (Greek, Cyrillic, Latin Extended), not 3-byte

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
4. **Check**: Is SCORE higher than previous best? Is GAP reasonable?
   - SCORE improved AND GAP < 8 → great, commit and log
   - SCORE improved BUT GAP > 8 → risky, the penalty may worsen on further experiments. Consider reverting.
   - SCORE decreased → revert and log failure
5. Go to step 1.

## Strategy guidance

### Phase A: Byte-cost optimization (first)
- Audit current config for 3-byte symbols
- Replace highest-frequency 3-byte symbols with 1-byte or 2-byte alternatives
- This improves BOTH train and val equally (no gap risk)

### Phase B: General English symbol expansion
- Add common English words not yet in SYMBOL_MAP
- Focus on words that appear in ALL categories of text
- Words like prepositions, pronouns, common verbs, conjunctions
- This is the safest lever — word frequency is stable across splits

### Phase C: General English phrase expansion
- Add phrases that are universal English patterns
- Test each batch: if GAP increases significantly, revert
- Start with the most common phrases and work down

### Phase D: Vowel/morphological tuning
- Fine-tune vowel stripping for better reconstruction
- Add morphological patterns for common suffixes

### Phase E: Category-aware optimization
- The corpus spans 15 categories. Check which categories compress worst.
- Look for common patterns in low-performing categories and add those.
- Avoid category-specific jargon that only appears in train.

## Rules

1. NEVER modify evaluate_v2.py, validate_v2.py, or corpus files
2. You ONLY edit config.py
3. NEVER stop to ask permission — keep looping
4. Commit only improvements. Revert everything else.
5. Log EVERY experiment to results.tsv, including failures.
6. **Watch the GAP.** It's your overfitting radar.
7. Always prefer lower byte-cost symbols (1-byte > 2-byte > 3-byte).
