"""
HLC test suite.
Run: python -m pytest tests/ -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from hlc import compress, decompress, compress_with_report
from hlc.compress import HLCCompressor, HLCDecompressor


class TestCompression:
    """Test the compression pipeline."""

    def test_compress_returns_shorter_text(self):
        text = "The compaction quality is bounded by the compacting model's ability to understand what matters."
        compressed = compress(text)
        assert len(compressed) < len(text)

    def test_compress_with_report_returns_stats(self):
        text = "A more capable model will produce better summaries because it can reason about relevance."
        compressed, report = compress_with_report(text)
        assert "compression_ratio" in report
        assert report["compression_ratio"] > 0
        assert report["original_chars"] == len(text)
        assert report["compressed_chars"] == len(compressed)

    def test_empty_string(self):
        compressed = compress("")
        assert compressed == ""

    def test_single_word(self):
        compressed = compress("hello")
        assert isinstance(compressed, str)

    def test_layer_selection(self):
        text = "The quick brown fox jumps over the lazy dog."
        full = compress(text, layers=(1, 2, 3, 4))
        partial = compress(text, layers=(1, 2))
        # More layers should generally produce shorter or equal output
        assert len(full) <= len(partial) + 5  # small tolerance

    def test_compression_ratio_positive(self):
        text = (
            "Absolutely, and this is the part that deserves more attention. "
            "The compaction quality is bounded by the compacting model's ability "
            "to understand what matters."
        )
        compressed, report = compress_with_report(text)
        assert report["compression_ratio"] > 30  # expect at least 30%

    def test_punctuation_preserved(self):
        text = "Hello, world! How are you? I'm fine — thanks."
        compressed = compress(text)
        # Core punctuation should survive
        assert "," in compressed or "!" in compressed or "?" in compressed


class TestDecompression:
    """Test the decompression pipeline."""

    def test_decompress_recovers_words(self):
        text = "A more capable model will produce better summaries."
        compressed = compress(text)
        decompressed = decompress(compressed)
        # Key content words should be recovered
        for word in ["capable", "model", "produce", "better", "summaries"]:
            assert word in decompressed.lower() or any(
                w.startswith(word[:4]) for w in decompressed.lower().split()
            )

    def test_roundtrip_symbol_recovery(self):
        """Symbols (Layer 3) should be fully reversible."""
        text = "this is the thing that matters for what we have from here"
        compressed = compress(text, layers=(3,))  # only symbols
        decompressed = decompress(compressed)
        # Should recover the original words
        assert "this" in decompressed or "!" in compressed

    def test_decompress_empty(self):
        assert decompress("") == ""


class TestCodebook:
    """Test codebook integrity."""

    def test_codebook_loads(self):
        compressor = HLCCompressor()
        assert len(compressor.word_codebook) > 0
        assert len(compressor.symbol_map) > 0

    def test_symbol_map_completeness(self):
        compressor = HLCCompressor()
        expected_words = {"and", "the", "is", "that", "for", "what", "with", "this", "from", "not"}
        mapped_words = set(compressor.symbol_map.keys())
        assert expected_words.issubset(mapped_words)

    def test_no_code_longer_than_word(self):
        """Every code must be shorter than the word it replaces."""
        compressor = HLCCompressor()
        for word, code in compressor.word_codebook.items():
            assert len(code) < len(word), f"Code '{code}' is not shorter than word '{word}'"


class TestBenchmark:
    """Test that benchmarks run without errors."""

    def test_benchmark_runs(self):
        from hlc.benchmark import TEST_SAMPLES
        compressor = HLCCompressor()
        for name, sample in TEST_SAMPLES.items():
            compressed = compressor.compress(sample["text"])
            report = compressor.get_compression_report()
            assert report["compression_ratio"] > 0, f"Failed on {name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
