"""
HLC Frequency Analyzer
======================
Track 1: Build word and phrase frequency rankings from available corpora.
Uses the wordfreq library for word-level frequencies (derived from Wikipedia,
subtitles, Twitter, web text — ~400k English words).

Phrase frequency is bootstrapped from common English n-grams.
"""

import json
import re
from pathlib import Path
from collections import Counter

from wordfreq import top_n_list, word_frequency, available_languages

# ── Constants ──
CODEBOOK_DIR = Path(__file__).parent / "codebooks"
CODEBOOK_DIR.mkdir(exist_ok=True)

# Existing shorthand that must NEVER be reassigned
PROTECTED_SHORTHAND = {
    "btw", "tldr", "rsvp", "fyi", "imo", "imho", "gtg", "brb", "afk",
    "asap", "diy", "eta", "faq", "fomo", "ftw", "gg", "idk", "irl",
    "jk", "lmk", "lol", "nvm", "omg", "omw", "rofl", "smh", "tbh",
    "tmi", "ttyl", "wip", "wtf", "yolo", "np", "ty", "thx", "pls",
    "msg", "info", "pic", "app", "dev", "doc", "docs", "admin", "auth",
    "api", "url", "html", "css", "js", "sql", "db", "ui", "ux",
}

# High-frequency short words that get single-symbol replacement
SYMBOL_MAP = {
    "and": "+",
    "the": "^",
    "is": "$",
    "be": "$",
    "that": "~",
    "for": "@",
    "at": "@",
    "what": "#",
    "with": "&",
    "this": "!",
    "from": "%",
    "not": "*",
}

# Common phrases in English (bootstrapped — will be expanded with corpus analysis)
COMMON_PHRASES = [
    # Conversational
    "how are you", "thank you", "you're welcome", "nice to meet you",
    "good morning", "good night", "good evening", "good afternoon",
    "i don't know", "i don't think", "i don't understand",
    "let me know", "as soon as possible", "by the way",
    "in my opinion", "to be honest", "for what it's worth",
    "on the other hand", "at the same time", "for example",
    "in order to", "as well as", "such as", "due to",
    "in terms of", "with respect to", "in addition to",
    "as a result", "in fact", "of course", "at least",
    "so far", "right now", "a lot of", "kind of", "sort of",
    "a little bit", "more or less", "up to", "out of",
    # Technical / LLM context
    "it is important to note that", "it should be noted that",
    "in this case", "on the other hand", "for instance",
    "as mentioned above", "as discussed", "based on",
    "in the context of", "with regard to", "according to",
    "it is worth noting", "take into account", "keep in mind",
    "make sure", "in particular", "as a whole",
    "at this point", "in general", "for the most part",
    "in other words", "that being said", "having said that",
    "the fact that", "in addition", "as well",
    "there is", "there are", "it is", "it was",
    "would be", "could be", "should be", "might be",
    "has been", "have been", "had been", "will be",
    "going to", "able to", "need to", "want to",
    "have to", "used to", "try to", "seem to",
    # Agent / AI specific
    "context window", "token cost", "language model",
    "large language model", "machine learning", "artificial intelligence",
    "neural network", "deep learning", "natural language",
    "natural language processing",
]


def get_word_frequencies(top_n=50000):
    """Get top N English words ranked by frequency from wordfreq."""
    words = top_n_list("en", top_n, wordlist="best")
    result = []
    for rank, word in enumerate(words, 1):
        freq = word_frequency(word, "en", wordlist="best")
        result.append({
            "word": word,
            "rank": rank,
            "frequency": freq,
            "length": len(word),
        })
    return result


def compute_code_savings(word_len, code_len):
    """Calculate character savings of replacing a word with a code."""
    return word_len - code_len


def filter_codeable_words(word_list, min_word_length=4):
    """
    Filter words that benefit from codebook encoding.
    A word is codeable if the code assigned to it is shorter than the word.
    
    Code length depends on rank:
    - Ranks 1-9: 1 char (if using single Unicode symbols)
    - For Unicode-first: top ~3000 get single Unicode chars (1 char)
    - Ranks 3001-99999: numeric codes (2-5 chars)
    
    We only encode words where code_length < word_length.
    """
    codeable = []
    unicode_pool_size = 3000  # approximate single-char Unicode slots available
    
    for item in word_list:
        word = item["word"]
        rank = item["rank"]
        word_len = len(word)
        
        # Skip very short words (handled by symbol map)
        if word_len < min_word_length:
            continue
        
        # Skip protected shorthand
        if word.lower() in PROTECTED_SHORTHAND:
            continue
        
        # Determine code length based on rank
        if rank <= unicode_pool_size:
            code_len = 1  # single Unicode character
        elif rank <= 9:
            code_len = 1
        elif rank <= 99:
            code_len = 2
        elif rank <= 999:
            code_len = 3
        elif rank <= 9999:
            code_len = 4
        else:
            code_len = 5
        
        savings = compute_code_savings(word_len, code_len)
        
        if savings > 0:
            codeable.append({
                "word": word,
                "rank": rank,
                "word_length": word_len,
                "code_length": code_len,
                "savings_per_occurrence": savings,
                "frequency": item["frequency"],
            })
    
    return codeable


def rank_phrases(phrases=None):
    """
    Rank phrases by estimated frequency and compression value.
    Longer phrases that are common = higher value.
    """
    if phrases is None:
        phrases = COMMON_PHRASES
    
    ranked = []
    for phrase in phrases:
        word_count = len(phrase.split())
        char_count = len(phrase)
        # Estimate frequency from component word frequencies
        words = phrase.split()
        avg_freq = sum(
            word_frequency(w, "en", wordlist="best") for w in words
        ) / len(words)
        
        # Score: longer phrases with higher frequency = more valuable
        # Weight character count heavily since that's what we're saving
        score = char_count * (avg_freq ** 0.3)  # dampen frequency influence
        
        ranked.append({
            "phrase": phrase,
            "word_count": word_count,
            "char_count": char_count,
            "avg_word_freq": avg_freq,
            "compression_score": score,
        })
    
    ranked.sort(key=lambda x: x["compression_score"], reverse=True)
    
    # Assign ranks
    for i, item in enumerate(ranked):
        item["rank"] = i + 1
    
    return ranked


def generate_analysis_report():
    """Generate a full analysis report with statistics."""
    print("=" * 60)
    print("HLC FREQUENCY ANALYSIS REPORT")
    print("=" * 60)
    
    # Word analysis
    print("\n── Word Frequency Analysis ──")
    words = get_word_frequencies(50000)
    print(f"Total words analyzed: {len(words)}")
    
    codeable = filter_codeable_words(words)
    print(f"Codeable words (code < word length): {len(codeable)}")
    
    # Distribution of savings
    savings_dist = Counter()
    for item in codeable:
        savings_dist[item["savings_per_occurrence"]] += 1
    
    print("\nSavings distribution (chars saved per occurrence):")
    for savings in sorted(savings_dist.keys()):
        print(f"  {savings} chars saved: {savings_dist[savings]} words")
    
    # Top 20 highest-value words (frequency × savings)
    codeable.sort(key=lambda x: x["frequency"] * x["savings_per_occurrence"], reverse=True)
    print("\nTop 30 highest-value words for encoding:")
    print(f"  {'Word':<20} {'Length':>6} {'Code':>6} {'Saved':>6} {'Frequency':>12}")
    print(f"  {'-'*20} {'-'*6} {'-'*6} {'-'*6} {'-'*12}")
    for item in codeable[:30]:
        print(f"  {item['word']:<20} {item['word_length']:>6} {item['code_length']:>6} "
              f"{item['savings_per_occurrence']:>6} {item['frequency']:>12.8f}")
    
    # Phrase analysis
    print("\n── Phrase Frequency Analysis ──")
    phrases = rank_phrases()
    print(f"Total phrases analyzed: {len(phrases)}")
    
    print("\nTop 30 phrases by compression value:")
    print(f"  {'Phrase':<35} {'Chars':>5} {'Words':>5} {'Score':>10}")
    print(f"  {'-'*35} {'-'*5} {'-'*5} {'-'*10}")
    for item in phrases[:30]:
        print(f"  {item['phrase']:<35} {item['char_count']:>5} {item['word_count']:>5} "
              f"{item['compression_score']:>10.6f}")
    
    # Symbol map analysis
    print("\n── Symbol Map ──")
    print(f"Words with single-symbol replacement: {len(SYMBOL_MAP)}")
    for word, symbol in SYMBOL_MAP.items():
        freq = word_frequency(word, "en", wordlist="best")
        print(f"  '{word}' → '{symbol}'  (freq: {freq:.6f})")
    
    # Protected shorthand
    print(f"\n── Protected Shorthand ({len(PROTECTED_SHORTHAND)} entries) ──")
    print(f"  {', '.join(sorted(PROTECTED_SHORTHAND))}")
    
    # Summary statistics
    print("\n── Estimated Impact ──")
    # For a typical 1000-word English passage:
    # ~40% function words (handled by symbol map)
    # ~35% content words (handled by word codebook)
    # ~10% phrases (handled by phrase codebook)
    # ~15% remaining (vowel stripping)
    print("Estimated compression on typical English text:")
    print("  Layer 1 (Phrases):     ~10-15% of text, replaced with 1-2 char codes")
    print("  Layer 2 (Words):       ~35-40% of text, replaced with 1-4 char codes")
    print("  Layer 3 (Symbols):     ~30-35% of text, each word → 1 char")
    print("  Layer 4 (Vowels):      ~15-20% remaining, ~30% char reduction")
    print("  Combined estimate:     50-70% total character reduction")
    
    return {
        "words": codeable,
        "phrases": phrases,
        "symbol_map": SYMBOL_MAP,
        "protected": list(PROTECTED_SHORTHAND),
    }


def save_frequency_data():
    """Save frequency analysis to codebook directory."""
    words = get_word_frequencies(50000)
    codeable = filter_codeable_words(words)
    
    # Sort by frequency × savings for optimal code assignment
    codeable.sort(key=lambda x: x["frequency"] * x["savings_per_occurrence"], reverse=True)
    
    phrases = rank_phrases()
    
    # Save word frequencies
    with open(CODEBOOK_DIR / "word_freq.json", "w") as f:
        json.dump(codeable, f, indent=2)
    print(f"Saved {len(codeable)} codeable words to word_freq.json")
    
    # Save phrase frequencies
    with open(CODEBOOK_DIR / "phrase_freq.json", "w") as f:
        json.dump(phrases, f, indent=2)
    print(f"Saved {len(phrases)} ranked phrases to phrase_freq.json")
    
    # Save symbol map
    with open(CODEBOOK_DIR / "symbols.json", "w") as f:
        json.dump({
            "symbol_map": SYMBOL_MAP,
            "protected_shorthand": sorted(PROTECTED_SHORTHAND),
        }, f, indent=2)
    print(f"Saved symbol map ({len(SYMBOL_MAP)} entries) and protected list")
    
    return codeable, phrases


if __name__ == "__main__":
    report = generate_analysis_report()
    print("\n\nSaving frequency data...")
    save_frequency_data()
    print("Done!")
