# HLC Autoresearch — Agent Instructions

You are an autonomous research agent optimizing the HLC (Hierarchical Lexical Compression) system. Your goal is to **maximize the composite score** by improving both compression ratio and reconstruction accuracy.

## Setup (one-time)

1. Create a new git branch: `git checkout -b autoresearch/<tag>` where tag is today's date (e.g. `mar22`)
2. Read `config.py` — this is the ONLY file you modify
3. Read `evaluate.py` — this is read-only, do NOT touch it
4. Run the baseline: `python evaluate.py --verbose`
5. Record the baseline score in `results.tsv` (create it with header: `experiment\tdescription\tscore\tratio\trecon\tphrases\tstatus`)
6. Begin experimentation

## The metric

Run `python evaluate.py` after every change. It scores against **80 train samples** across 10 categories (technical, casual, business, documentation, creative, academic, support, instructional, email, AI conversation). A separate **20-sample holdout set** exists in `corpus/holdout.json` that you NEVER optimize against — the human uses `validate.py` to check for overfitting.

It prints:

```
SCORE:XX.XXXX RATIO:XX.X RECON:XX.X PHRASES:XX CODEBOOK:XXX
```

- **SCORE** is the composite (0-100). This is what you maximize.
- **RATIO** is compression percentage. Higher = better compression.
- **RECON** is deterministic reconstruction accuracy. Higher = more reversible.
- **PHRASES** is how many phrase codebook entries actually hit in the test corpus.
- **CODEBOOK** is the total number of phrase entries.

The composite formula is: `SCORE = RATIO * 0.6 + RECON * 0.4`

## What you can modify

You ONLY edit `config.py`. Specifically:

### PHRASE_CODEBOOK (highest impact — focus here)
- **Add phrases** that appear in the test corpus. Read the test samples in evaluate.py to find common phrases.
- **Remove phrases** that never hit (PHRASES count tells you).
- **Try longer phrases** — they save more characters per hit.
- **Try common English phrases** — "I would like", "as well as", "in order to", "there are", "would be", etc.
- **Try domain phrases** — "context window", "language model", "token cost", etc.
- Codes must be shorter than the phrase. Single Unicode chars are ideal.
- NEVER reuse a code for two different phrases.

### SYMBOL_MAP (medium impact)
- Consider adding more high-frequency short words
- Words like "are", "was", "were", "had", "has", "but", "can", "our", "its" are candidates
- Each symbol must be unique. Don't collide with existing symbols.
- Available ASCII symbols you could use: `;`, `<`, `>`, `{`, `}`, `\`, `|`, etc.
- Be careful: some symbols break markdown or have special meaning in regex.

### VOWEL_STRIP_EXCEPTIONS (low-medium impact)
- Add words where vowel stripping causes ambiguity
- If reconstruction accuracy drops after adding a phrase, check if vowel stripping is mangling a nearby word

### MORPHOLOGICAL_PATTERNS (medium impact)
- Improve suffix detection so more word variants match their base forms
- Add patterns for common suffixes you see failing
- Order matters — put more specific patterns before generic ones

### MIN_VOWEL_STRIP_LENGTH (low impact)
- Currently 4. Try 3 (more aggressive) or 5 (more conservative)
- Check reconstruction score — if it drops, revert

## Experiment loop

LOOP FOREVER:

1. **Hypothesize**: Pick ONE thing to change. Write a 1-line description.
2. **Edit**: Modify config.py with the change.
3. **Evaluate**: Run `python evaluate.py`
4. **Compare**: Is SCORE higher than the previous best?
   - YES → `git add config.py && git commit -m "exp N: <description> (score: X.XX)"` and log to results.tsv
   - NO → `git checkout config.py` (revert) and log the failure to results.tsv
5. **Analyze**: Look at the breakdown. Where is the score being lost? Focus there next.
6. Go to step 1.

## Strategy guidance

### Phase A: Low-hanging fruit (do this first)
- Read the test corpus text carefully. Find phrases that appear multiple times.
- Add those exact phrases to PHRASE_CODEBOOK.
- Each phrase hit converts 10-30 chars into 1 char. This is the biggest win.

### Phase B: Symbol expansion
- After phrases are maxed out, try adding more symbols.
- Focus on words that appear 5+ times across the corpus.

### Phase C: Vowel tuning
- Experiment with MIN_VOWEL_STRIP_LENGTH.
- Add words to VOWEL_STRIP_EXCEPTIONS if they reconstruct badly.

### Phase D: Morphological improvement
- Look for words in the test corpus that have common suffixes.
- Add patterns that help the decompressor match them to base forms.

### Phase E: Creative exploration
- Try anything you think might work. The score is the judge.
- Combine multiple small changes if they're independent.
- If you get stuck, try reverting to the best config and exploring a different direction.

## Rules

1. NEVER modify evaluate.py, validate.py, or build_corpus.py
2. NEVER modify files in the corpus/ directory
3. You ONLY edit config.py
4. NEVER stop to ask permission — keep looping
5. Commit only improvements. Revert everything else.
6. Log EVERY experiment to results.tsv, including failures.
7. Keep descriptions concise but specific in commit messages.
8. If config.py has a syntax error, fix it immediately and don't count it as an experiment.
