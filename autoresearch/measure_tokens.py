"""
HLC Token Measurement
======================
Measures ACTUAL token savings using tiktoken.

Usage:
    pip install tiktoken
    cd hlc/autoresearch
    python measure_tokens.py                              # Uses config.py, v2 corpus
    python measure_tokens.py --config config_sonnet_best.py
    python measure_tokens.py --config config_opus_v2_best.py

Tokenizers tested:
    - cl100k_base (GPT-4, GPT-3.5)
    - o200k_base  (GPT-4o)

Note: Anthropic's tokenizer is not publicly available via tiktoken.
cl100k results are a reasonable proxy — most BPE tokenizers handle
Unicode similarly. For the paper, we note this limitation.
"""

import re
import sys
import json
import importlib.util
from pathlib import Path
from collections import Counter

import tiktoken

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def load_config(config_path=None):
    if config_path is None:
        config_path = Path(__file__).parent / "config.py"
    spec = importlib.util.spec_from_file_location("config", str(config_path))
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)
    return cfg


VOWELS = set("aeiouAEIOU")

def compress_text(text, config):
    result = text
    phrases_sorted = sorted(config.PHRASE_CODEBOOK.keys(), key=len, reverse=True)
    for phrase in phrases_sorted:
        code = config.PHRASE_CODEBOOK[phrase]
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        result = pattern.sub(code, result)

    tokens = re.findall(r"[\w']+|[^\w\s]|\s+", result)
    rebuilt = []
    for token in tokens:
        if re.match(r"[\w']+", token):
            lower = token.lower()
            if lower in config.SYMBOL_MAP:
                rebuilt.append(config.SYMBOL_MAP[lower])
            else:
                rebuilt.append(token)
        else:
            rebuilt.append(token)
    result = "".join(rebuilt)

    tokens = re.findall(r"[\w']+|[^\w\s]|\s+", result)
    rebuilt = []
    for token in tokens:
        if re.match(r"[a-zA-Z]+$", token):
            lower = token.lower()
            if lower in config.PROTECTED_SHORTHAND:
                rebuilt.append(token); continue
            if lower in config.VOWEL_STRIP_EXCEPTIONS:
                rebuilt.append(token); continue
            if len(token) < config.MIN_VOWEL_STRIP_LENGTH:
                rebuilt.append(token); continue
            if len(token) == 1:
                rebuilt.append(token); continue
            first, last, middle = token[0], token[-1], token[1:-1]
            stripped = "".join(c for c in middle if c not in VOWELS)
            rebuilt.append(first + stripped + last if stripped else token)
        else:
            rebuilt.append(token)
    return "".join(rebuilt)


def analyze_symbol_tokenization(config, encoder):
    results = []
    for word, symbol in config.SYMBOL_MAP.items():
        word_tokens = len(encoder.encode(word))
        sym_tokens = len(encoder.encode(symbol))
        results.append({
            "word": word, "symbol": symbol,
            "word_tokens": word_tokens, "symbol_tokens": sym_tokens,
            "savings": word_tokens - sym_tokens,
            "efficient": (word_tokens - sym_tokens) > 0,
        })
    return results


def measure_corpus(config, encoder, samples):
    results = []
    total_oc, total_cc = 0, 0
    total_ob, total_cb = 0, 0
    total_ot, total_ct = 0, 0

    for sample in samples:
        text = sample["text"]
        compressed = compress_text(text, config)

        oc, cc = len(text), len(compressed)
        ob, cb = len(text.encode("utf-8")), len(compressed.encode("utf-8"))
        ot, ct = len(encoder.encode(text)), len(encoder.encode(compressed))

        total_oc += oc; total_cc += cc
        total_ob += ob; total_cb += cb
        total_ot += ot; total_ct += ct

        results.append({
            "category": sample["category"],
            "orig_chars": oc, "comp_chars": cc,
            "orig_bytes": ob, "comp_bytes": cb,
            "orig_tokens": ot, "comp_tokens": ct,
            "char_ratio": (oc - cc) / oc * 100,
            "byte_ratio": (ob - cb) / ob * 100,
            "token_ratio": (ot - ct) / ot * 100,
        })

    return results, {
        "total_orig_chars": total_oc, "total_comp_chars": total_cc,
        "total_orig_bytes": total_ob, "total_comp_bytes": total_cb,
        "total_orig_tokens": total_ot, "total_comp_tokens": total_ct,
        "char_ratio": (total_oc - total_cc) / total_oc * 100,
        "byte_ratio": (total_ob - total_cb) / total_ob * 100,
        "token_ratio": (total_ot - total_ct) / total_ot * 100,
    }


def main():
    config_path = None
    if "--config" in sys.argv:
        idx = sys.argv.index("--config")
        config_path = Path(sys.argv[idx + 1])

    config = load_config(config_path)
    config_name = config_path.name if config_path else "config.py"

    encoders = {}
    for name in ["cl100k_base", "o200k_base"]:
        try:
            encoders[name] = tiktoken.get_encoding(name)
        except Exception as e:
            print(f"WARNING: Could not load {name}: {e}")

    if not encoders:
        print("ERROR: No tokenizers loaded. Run: pip install tiktoken")
        sys.exit(1)

    corpus_dir = Path(__file__).parent / "corpus"
    splits = {}
    for name in ["train", "val", "holdout"]:
        path = corpus_dir / f"{name}.json"
        if path.exists():
            with open(path) as f:
                splits[name] = json.load(f)

    print("=" * 70)
    print(f"HLC TOKEN MEASUREMENT REPORT")
    print(f"Config: {config_name}")
    print(f"SYMBOL_MAP: {len(config.SYMBOL_MAP)} | PHRASE_CODEBOOK: {len(config.PHRASE_CODEBOOK)}")
    print(f"Corpus: {', '.join(f'{k}({len(v)})' for k, v in splits.items())}")
    print("=" * 70)

    # Part 1: Symbol audit
    print("\n-- SYMBOL TOKENIZATION AUDIT --")
    for enc_name, encoder in encoders.items():
        sym_results = analyze_symbol_tokenization(config, encoder)
        efficient = sum(1 for r in sym_results if r["efficient"])
        neutral = sum(1 for r in sym_results if r["savings"] == 0)
        wasteful = sum(1 for r in sym_results if r["savings"] < 0)

        print(f"\n  {enc_name}:")
        print(f"    Efficient: {efficient}/{len(sym_results)} ({efficient/len(sym_results)*100:.0f}%)")
        print(f"    Neutral:   {neutral}  |  Wasteful: {wasteful}")

        wl = sorted([r for r in sym_results if r["savings"] < 0], key=lambda x: x["savings"])
        if wl:
            print(f"    Wasteful (top 10):")
            for r in wl[:10]:
                print(f"      '{r['word']}' ({r['word_tokens']}t) -> '{r['symbol']}' ({r['symbol_tokens']}t) = {r['savings']:+d}")

        dist = Counter(r["symbol_tokens"] for r in sym_results)
        print(f"    Token cost distribution: {dict(sorted(dist.items()))}")

    # Part 2: Corpus measurement
    print("\n-- CORPUS: CHARS vs BYTES vs TOKENS --")
    for enc_name, encoder in encoders.items():
        print(f"\n  {enc_name}:")
        for split_name, samples in splits.items():
            results, agg = measure_corpus(config, encoder, samples)
            print(f"\n    [{split_name.upper()}] ({len(samples)} samples)")
            print(f"      Char compression:  {agg['char_ratio']:.1f}%")
            print(f"      Byte compression:  {agg['byte_ratio']:.1f}%")
            print(f"      TOKEN compression: {agg['token_ratio']:.1f}%")
            print(f"      Tokens: {agg['total_orig_tokens']:,} -> {agg['total_comp_tokens']:,} (saved {agg['total_orig_tokens']-agg['total_comp_tokens']:,})")
            print(f"      Gaps: char->byte {agg['char_ratio']-agg['byte_ratio']:.1f}pp | byte->token {agg['byte_ratio']-agg['token_ratio']:.1f}pp")

            cats = {}
            for s in results:
                cat = s["category"]
                if cat not in cats:
                    cats[cat] = {"cr": [], "br": [], "tr": []}
                cats[cat]["cr"].append(s["char_ratio"])
                cats[cat]["br"].append(s["byte_ratio"])
                cats[cat]["tr"].append(s["token_ratio"])

            print(f"\n      {'Category':<18} {'Char%':>6} {'Byte%':>6} {'Token%':>7} {'B->T':>5}")
            print(f"      {'─'*18} {'─'*6} {'─'*6} {'─'*7} {'─'*5}")
            for cat in sorted(cats):
                c = sum(cats[cat]["cr"]) / len(cats[cat]["cr"])
                b = sum(cats[cat]["br"]) / len(cats[cat]["br"])
                t = sum(cats[cat]["tr"]) / len(cats[cat]["tr"])
                print(f"      {cat:<18} {c:>5.1f}% {b:>5.1f}% {t:>6.1f}% {b-t:>4.1f}")

    # Part 3: Summary
    print("\n-- SUMMARY FOR PAPER --")
    enc_name = list(encoders.keys())[0]
    encoder = encoders[enc_name]
    print(f"\n  Tokenizer: {enc_name}")
    print(f"  Config: {config_name}\n")
    print(f"  {'Split':<10} {'Char%':>7} {'Byte%':>7} {'Token%':>8} {'C->B':>5} {'B->T':>5}")
    print(f"  {'─'*10} {'─'*7} {'─'*7} {'─'*8} {'─'*5} {'─'*5}")
    for split_name in ["train", "val", "holdout"]:
        if split_name not in splits:
            continue
        _, agg = measure_corpus(config, encoder, splits[split_name])
        cb = agg["char_ratio"] - agg["byte_ratio"]
        bt = agg["byte_ratio"] - agg["token_ratio"]
        print(f"  {split_name:<10} {agg['char_ratio']:>6.1f}% {agg['byte_ratio']:>6.1f}% {agg['token_ratio']:>7.1f}% {cb:>4.1f} {bt:>4.1f}")

    print()


if __name__ == "__main__":
    main()
