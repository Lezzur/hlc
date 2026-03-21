"""
HLC Compression Pipeline
=========================
The core engine. Takes raw English text and runs it through
six compression layers in sequence.

Layer 1: Phrase codebook substitution (highest impact)
Layer 2: Word codebook substitution (high impact)
Layer 3: Symbol substitution for function words (medium impact)
Layer 4: Vowel stripping on remaining words (medium impact)
Layer 5: Recursive pattern compression (lower impact, optional)
Layer 6: Semantic metadata enrichment (enhancement, optional)
"""

import json
import re
from pathlib import Path

CODEBOOK_DIR = Path(__file__).parent / "codebooks"

# ── Vowel Stripping Config ──
VOWELS = set("aeiouAEIOU")
MIN_WORD_LENGTH_FOR_VOWEL_STRIP = 4  # don't strip words shorter than this

# Protected shorthand — never modify these
PROTECTED_SHORTHAND = {
    "btw", "tldr", "rsvp", "fyi", "imo", "imho", "gtg", "brb", "afk",
    "asap", "diy", "eta", "faq", "fomo", "ftw", "gg", "idk", "irl",
    "jk", "lmk", "lol", "nvm", "omg", "omw", "rofl", "smh", "tbh",
    "tmi", "ttyl", "ty", "thx", "pls", "np", "wip", "wtf", "yolo",
    "msg", "info", "pic", "app", "dev", "doc", "docs", "admin", "auth",
    "api", "url", "html", "css", "js", "sql", "db", "ui", "ux",
}


class HLCCompressor:
    """Hierarchical Lexical Compression engine."""
    
    def __init__(self, codebook_path=None):
        if codebook_path is None:
            codebook_path = CODEBOOK_DIR / "codebook_full.json"
        
        with open(codebook_path) as f:
            data = json.load(f)
        
        self.phrase_codebook = data.get("phrase_codebook", {})
        self.phrase_reverse = data.get("phrase_reverse", {})
        self.word_codebook = data.get("word_codebook", {})
        self.word_reverse = data.get("word_reverse", {})
        self.symbol_map = data.get("symbol_map", {})
        self.symbol_reverse = data.get("symbol_reverse", {})
        
        # Build case-insensitive phrase lookup
        self.phrase_lookup = {}
        for phrase, code in self.phrase_codebook.items():
            self.phrase_lookup[phrase.lower()] = (phrase, code)
        
        # Sort phrases by length (longest first) for greedy matching
        self.sorted_phrases = sorted(
            self.phrase_lookup.keys(),
            key=len,
            reverse=True
        )
        
        # Build case-insensitive word lookup
        self.word_lookup = {}
        for word, code in self.word_codebook.items():
            self.word_lookup[word.lower()] = (word, code)
        
        # Stats tracking
        self.stats = {
            "layer1_replacements": 0,
            "layer2_replacements": 0,
            "layer3_replacements": 0,
            "layer4_replacements": 0,
            "original_chars": 0,
            "compressed_chars": 0,
        }
    
    def reset_stats(self):
        for key in self.stats:
            self.stats[key] = 0
    
    # ── Layer 1: Phrase Substitution ──
    
    def _layer1_phrases(self, text):
        """Replace known phrases with codebook codes."""
        result = text
        for phrase in self.sorted_phrases:
            # Case-insensitive search
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            matches = pattern.findall(result)
            if matches:
                _, code = self.phrase_lookup[phrase]
                result = pattern.sub(code, result)
                self.stats["layer1_replacements"] += len(matches)
        return result
    
    # ── Layer 2: Word Substitution ──
    
    def _layer2_words(self, text):
        """Replace individual words with codebook codes."""
        # Tokenize preserving punctuation and whitespace
        tokens = re.findall(r"[\w']+|[^\w\s]|\s+", text)
        result = []
        
        for token in tokens:
            # Check if it's a word (not punctuation or whitespace)
            if re.match(r"[\w']+", token):
                lower = token.lower()
                
                # Skip if already a code (single Unicode char or number from L1)
                if len(token) == 1 and not token.isascii():
                    result.append(token)
                    continue
                
                # Skip words handled by symbol map (Layer 3)
                if lower in self.symbol_map:
                    result.append(token)
                    continue
                
                # Handle morphological variants
                base_word, suffix = self._extract_morphology(lower)
                
                if lower in self.word_lookup:
                    _, code = self.word_lookup[lower]
                    result.append(code)
                    self.stats["layer2_replacements"] += 1
                elif base_word and base_word in self.word_lookup:
                    _, code = self.word_lookup[base_word]
                    result.append(code + suffix)
                    self.stats["layer2_replacements"] += 1
                else:
                    result.append(token)
            else:
                result.append(token)
        
        return "".join(result)
    
    def _extract_morphology(self, word):
        """
        Extract base word and morphological suffix.
        Returns (base_word, suffix) or (None, None) if no pattern matches.
        """
        # Common English suffixes -> compact suffix codes
        patterns = [
            (r"^(.+?)tion$", "tn"),      # production -> produc + tn
            (r"^(.+?)sion$", "sn"),       # decision -> deci + sn
            (r"^(.+?)ment$", "mt"),       # movement -> move + mt  
            (r"^(.+?)ness$", "ns"),       # happiness -> happi + ns
            (r"^(.+?)able$", "bl"),       # comfortable -> comfort + bl
            (r"^(.+?)ible$", "bl"),       # possible -> poss + bl
            (r"^(.+?)ing$", "ng"),        # running -> runn + ng
            (r"^(.+?)ily$", "ly"),        # happily -> happ + ly
            (r"^(.+?)ly$", "ly"),         # quickly -> quick + ly
            (r"^(.+?)ed$", "d"),          # walked -> walk + d
            (r"^(.+?)er$", "r"),          # bigger -> bigg + r
            (r"^(.+?)est$", "st"),        # biggest -> bigg + st
            (r"^(.+?)es$", "s"),          # watches -> watch + s
            (r"^(.+?)s$", "s"),           # dogs -> dog + s
        ]
        
        for pattern, suffix in patterns:
            match = re.match(pattern, word)
            if match:
                base = match.group(1)
                if len(base) >= 3:  # base must be meaningful
                    return base, suffix
        
        return None, None
    
    # ── Layer 3: Symbol Substitution ──
    
    def _layer3_symbols(self, text):
        """Replace high-frequency short words with symbols."""
        tokens = re.findall(r"[\w']+|[^\w\s]|\s+", text)
        result = []
        
        for token in tokens:
            if re.match(r"[\w']+", token):
                lower = token.lower()
                if lower in self.symbol_map:
                    result.append(self.symbol_map[lower])
                    self.stats["layer3_replacements"] += 1
                else:
                    result.append(token)
            else:
                result.append(token)
        
        return "".join(result)
    
    # ── Layer 4: Vowel Stripping ──
    
    def _layer4_vowels(self, text):
        """Strip interior vowels from remaining words."""
        tokens = re.findall(r"[\w']+|[^\w\s]|\s+", text)
        result = []
        
        for token in tokens:
            if re.match(r"[a-zA-Z]+", token):
                lower = token.lower()
                
                # Skip if already encoded (Unicode, number, symbol)
                if len(token) == 1:
                    result.append(token)
                    continue
                
                # Skip protected shorthand
                if lower in PROTECTED_SHORTHAND:
                    result.append(token)
                    continue
                
                # Skip short words
                if len(token) < MIN_WORD_LENGTH_FOR_VOWEL_STRIP:
                    result.append(token)
                    continue
                
                # Strip interior vowels (keep first and last char)
                stripped = self._strip_vowels(token)
                if stripped != token:
                    self.stats["layer4_replacements"] += 1
                result.append(stripped)
            else:
                result.append(token)
        
        return "".join(result)
    
    def _strip_vowels(self, word):
        """Remove interior vowels, keeping first and last character."""
        if len(word) <= 3:
            return word
        
        first = word[0]
        last = word[-1]
        middle = word[1:-1]
        
        stripped_middle = "".join(c for c in middle if c not in VOWELS)
        
        # If stripping removed everything, keep one consonant
        if not stripped_middle:
            return word
        
        return first + stripped_middle + last
    
    # ── Layer 5: Recursive Pattern Compression (Optional) ──
    
    def _layer5_patterns(self, text):
        """
        Find repeated patterns in the compressed output and replace
        with macro codes. Most effective on longer texts.
        """
        # For now, this is a placeholder for the pattern detection algorithm
        # Full implementation requires analyzing the compressed corpus
        # to find statistically significant repeated sequences
        return text
    
    # ── Layer 6: Semantic Enrichment (Optional) ──
    
    def _layer6_enrich(self, text, metadata=None):
        """
        Add semantic metadata markers to compressed content.
        metadata dict can specify sections to mark as important,
        technical, emotional, etc.
        """
        if metadata is None:
            return text
        
        # Apply metadata markers
        for marker_type, sections in metadata.items():
            prefix_map = {
                "important": "!",
                "technical": "t",
                "emotional": "e",
                "decision": "d",
                "question": "?",
            }
            prefix = prefix_map.get(marker_type, marker_type[0])
            for section in sections:
                if section in text:
                    text = text.replace(section, f"{prefix}[{section}]")
        
        return text
    
    # ── Main Pipeline ──
    
    def compress(self, text, layers=(1, 2, 3, 4), metadata=None):
        """
        Run the full compression pipeline.
        
        Args:
            text: Raw English text to compress
            layers: Tuple of layer numbers to apply (1-6)
            metadata: Optional dict for Layer 6 enrichment
        
        Returns:
            Compressed text string
        """
        self.reset_stats()
        self.stats["original_chars"] = len(text)
        
        result = text
        
        if 1 in layers:
            result = self._layer1_phrases(result)
        if 2 in layers:
            result = self._layer2_words(result)
        if 3 in layers:
            result = self._layer3_symbols(result)
        if 4 in layers:
            result = self._layer4_vowels(result)
        if 5 in layers:
            result = self._layer5_patterns(result)
        if 6 in layers:
            result = self._layer6_enrich(result, metadata)
        
        self.stats["compressed_chars"] = len(result)
        
        return result
    
    def get_compression_report(self):
        """Return compression statistics from the last compress() call."""
        orig = self.stats["original_chars"]
        comp = self.stats["compressed_chars"]
        saved = orig - comp
        ratio = (saved / orig * 100) if orig > 0 else 0
        
        return {
            "original_chars": orig,
            "compressed_chars": comp,
            "chars_saved": saved,
            "compression_ratio": round(ratio, 1),
            "layer1_phrase_replacements": self.stats["layer1_replacements"],
            "layer2_word_replacements": self.stats["layer2_replacements"],
            "layer3_symbol_replacements": self.stats["layer3_replacements"],
            "layer4_vowel_strips": self.stats["layer4_replacements"],
        }


class HLCDecompressor:
    """Deterministic decompression — reverses all codebook lookups."""
    
    def __init__(self, codebook_path=None):
        if codebook_path is None:
            codebook_path = CODEBOOK_DIR / "codebook_full.json"
        
        with open(codebook_path) as f:
            data = json.load(f)
        
        self.phrase_reverse = data.get("phrase_reverse", {})
        self.word_reverse = data.get("word_reverse", {})
        self.symbol_reverse = data.get("symbol_reverse", {})
    
    def decompress(self, text):
        """
        Reverse the compression pipeline.
        Note: Layer 4 (vowel stripping) is NOT fully reversible
        deterministically — the LLM reader handles that.
        This reverses Layers 1-3 deterministically.
        """
        result = text
        
        # Reverse Layer 3: symbols back to words
        for symbol, word in self.symbol_reverse.items():
            # Only replace standalone symbols (not inside other tokens)
            result = re.sub(
                r'(?<!\w)' + re.escape(symbol) + r'(?!\w)',
                word,
                result
            )
        
        # Reverse Layer 2: word codes back to words
        tokens = re.findall(r"[\w']+|[^\w\s]|\s+", result)
        rebuilt = []
        for token in tokens:
            if token in self.word_reverse:
                rebuilt.append(self.word_reverse[token])
            else:
                rebuilt.append(token)
        result = "".join(rebuilt)
        
        # Reverse Layer 1: phrase codes back to phrases
        for code, phrase in self.phrase_reverse.items():
            result = result.replace(code, phrase)
        
        return result


# ── Convenience Functions ──

_compressor = None
_decompressor = None

def _get_compressor():
    global _compressor
    if _compressor is None:
        _compressor = HLCCompressor()
    return _compressor

def _get_decompressor():
    global _decompressor
    if _decompressor is None:
        _decompressor = HLCDecompressor()
    return _decompressor

def compress(text, layers=(1, 2, 3, 4), metadata=None):
    """Compress text using HLC pipeline."""
    return _get_compressor().compress(text, layers=layers, metadata=metadata)

def decompress(text):
    """Decompress text (deterministic, reverses Layers 1-3)."""
    return _get_decompressor().decompress(text)

def compress_with_report(text, layers=(1, 2, 3, 4)):
    """Compress and return both compressed text and statistics."""
    c = _get_compressor()
    compressed = c.compress(text, layers=layers)
    report = c.get_compression_report()
    return compressed, report


if __name__ == "__main__":
    # Demo with our running example
    test_text = (
        "Absolutely, and this is the part that deserves more attention. "
        "The compaction quality is bounded by the compacting model's ability "
        "to understand what matters. A more capable model will produce better "
        "summaries because it can reason about relevance, identify dependencies "
        "between statements, and recognize which details are structural versus "
        "decorative. But even the best model is guessing about future relevance "
        "— it doesn't know what you'll ask next."
    )
    
    print("=" * 70)
    print("HLC COMPRESSION DEMO")
    print("=" * 70)
    
    print(f"\n── Original ({len(test_text)} chars) ──")
    print(test_text)
    
    c = HLCCompressor()
    
    # Show each layer independently
    for layer_num in range(1, 5):
        layers = tuple(range(1, layer_num + 1))
        compressed = c.compress(test_text, layers=layers)
        report = c.get_compression_report()
        print(f"\n── After Layers 1-{layer_num} ({report['compressed_chars']} chars, "
              f"-{report['compression_ratio']}%) ──")
        print(compressed)
    
    # Full pipeline
    compressed, report = compress_with_report(test_text)
    
    print(f"\n── Compression Report ──")
    for key, value in report.items():
        print(f"  {key}: {value}")
    
    # Deterministic decompression
    decompressed = decompress(compressed)
    print(f"\n── Deterministic Decompression ──")
    print(decompressed)
    print(f"\n  (Note: vowel-stripped words remain compressed —")
    print(f"   LLM reader handles full reconstruction)")
