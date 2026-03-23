I'm updating the HLC autoresearch evaluator. Replace these 3 files in hlc/autoresearch/ with the new versions I downloaded:

- evaluate_v2.py (new: gap-penalty instead of codebook caps)
- validate_v2.py (updated: no cap check import)
- program_v2.md (new: explains gap penalty, no hard limits)

After replacing:

1. Run `cd hlc/autoresearch && python evaluate_v2.py --verbose` — show me the output
2. Run `python validate_v2.py --verbose` — show me the output
3. `git add -A && git commit -m "v2 evaluator: gap-penalty replaces codebook caps (threshold 8, rate 2x)" && git push`

The key change: no more codebook size limits. Instead, the train/val gap is penalized. Gap under 8 points = no penalty. Above 8, each extra point costs 2 points from the composite. This lets Opus use unlimited symbols and phrases while making memorization self-defeating.
