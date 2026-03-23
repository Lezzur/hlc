I'm wrapping up Session 2 of the HLC project. I need to commit all results, documentation, and plans to the repo at https://github.com/Lezzur/hlc. Do everything in order:

## Step 1: Update the living document

Replace docs/HLC_Living_Document.md with the new version I downloaded (HLC_Living_Document.md). This version covers all Session 2 work: byte measurement, Opus v1 and v2 sessions, adversarial optimization findings, tiktoken results, and updated roadmap.

## Step 2: Add the negative result writeup

Place hlc_negative_result.md into docs/. This documents the token expansion finding — HLC compresses characters/bytes but EXPANDS tokens by 70-81% due to BPE tokenizer incompatibility.

## Step 3: Add the Llama fine-tuning plan

Place llama_finetuning_plan.md into docs/. This is the Phase 5 plan: custom tokenizer + Llama 3.1 fine-tuning to close the token gap.

## Step 4: Ensure all autoresearch artifacts are committed

Check that these files exist in autoresearch/ and are tracked by git:
- config_sonnet_best.py
- config_opus_best.py (Opus v1 exp 21)
- config_opus_v2_best.py (Opus v2 exp 15)
- results_sonnet.tsv
- results_opus.tsv (v1, 32 experiments)
- results_opus_v2.tsv (v2, 20 experiments)
- evaluate_v2.py
- validate_v2.py
- program_v2.md
- build_corpus_v2.py
- measure_tokens.py
- corpus/train.json (v2, 210 samples)
- corpus/val.json (v2, 45 samples)
- corpus/holdout.json (v2, 45 samples)
- reports/token_measurement.md

If any are missing, note which ones so I can add them manually.

## Step 5: Roll back Opus v2 config to experiment 15

Make sure config.py in autoresearch/ is the exp 15 version (not the overfit exp 20). If config_opus_v2_best.py exists, copy it to config.py. Verify by checking that SYMBOL_MAP has ~1120 entries and PHRASE_CODEBOOK has ~617 entries (NOT 33,172).

## Step 6: Update README.md

Update the project README to reflect current status. It should mention:
- What HLC is (1-paragraph summary)
- Current results: 34-48% byte compression, 99.9% reconstruction, but token expansion with standard tokenizers
- The negative result and why it matters
- Next steps: custom tokenizer + Llama fine-tuning
- Link to the living document for full context
- Keep it concise — under 100 lines

## Step 7: Commit and push

```
git add -A
git commit -m "Session 2 complete: byte measurement, tiktoken negative result, Opus v1+v2 sessions, Llama plan

Key findings:
- HLC achieves 34-48% byte compression with 99.9% reconstruction
- Token compression is -70 to -81% (expansion) due to BPE incompatibility
- Opus adversarially exploited 3 different evaluation guardrails
- Path forward: custom tokenizer + Llama 3.1 fine-tuning (Phase 5)"

git push origin main
```

## Step 8: Show me the final state

Run:
```
git log --oneline -5
find docs/ -name "*.md" | sort
find autoresearch/ -name "*.py" -o -name "*.tsv" -o -name "*.md" | sort
```

Show me the output so I can confirm everything is in place.
