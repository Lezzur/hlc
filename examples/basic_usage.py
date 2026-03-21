"""
Basic HLC usage example.
Run: python examples/basic_usage.py
"""

from hlc import compress, decompress, compress_with_report


def main():
    # ── Example 1: Simple compression ──
    text = (
        "The system architecture consists of three primary components: "
        "the ingestion pipeline, the processing engine, and the storage layer. "
        "The ingestion pipeline handles incoming data from multiple sources "
        "including REST APIs, message queues, and batch file uploads."
    )

    compressed = compress(text)
    print("Example 1: Simple compression")
    print(f"  Original:   {text[:80]}...")
    print(f"  Compressed: {compressed[:80]}...")
    print(f"  Original length:   {len(text)} chars")
    print(f"  Compressed length: {len(compressed)} chars")
    print()

    # ── Example 2: Compression with statistics ──
    text2 = (
        "I understand your frustration with the billing issue. Let me look "
        "into this for you right away. It appears that the charge was applied "
        "twice due to a processing error on our end. I have initiated a refund "
        "for the duplicate charge, which should appear in your account within "
        "three to five business days."
    )

    compressed2, report = compress_with_report(text2)
    print("Example 2: Compression with stats")
    print(f"  Compression ratio: {report['compression_ratio']}%")
    print(f"  Characters saved:  {report['chars_saved']}")
    print(f"  Word replacements: {report['layer2_word_replacements']}")
    print(f"  Symbol subs:       {report['layer3_symbol_replacements']}")
    print()

    # ── Example 3: Layer-by-layer ──
    text3 = (
        "Absolutely, and this is the part that deserves more attention. "
        "The compaction quality is bounded by the compacting model's ability "
        "to understand what matters."
    )

    print("Example 3: Layer-by-layer compression")
    print(f"  Original: {text3}")
    for n in range(1, 5):
        layers = tuple(range(1, n + 1))
        result = compress(text3, layers=layers)
        ratio = round((1 - len(result) / len(text3)) * 100, 1)
        print(f"  Layers 1-{n}: {result}  ({ratio}%)")
    print()

    # ── Example 4: Deterministic decompression ──
    compressed4 = compress(text3)
    decompressed = decompress(compressed4)
    print("Example 4: Decompression")
    print(f"  Compressed:   {compressed4}")
    print(f"  Decompressed: {decompressed}")
    print(f"  (Vowel-stripped words remain compressed — LLM handles full reconstruction)")


if __name__ == "__main__":
    main()
