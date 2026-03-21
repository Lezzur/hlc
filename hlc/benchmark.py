"""
HLC Benchmark Suite
====================
Tests compression ratio, reconstruction accuracy, and token savings
across diverse text types.
"""

import json
import sys
from pathlib import Path

# Handle Unicode output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from .compress import HLCCompressor, HLCDecompressor, compress_with_report

# -- Test Corpus --
# Diverse English text samples representing different use cases

TEST_SAMPLES = {
    "technical_discussion": {
        "category": "Technical / Agent",
        "text": (
            "Absolutely, and this is the part that deserves more attention. "
            "The compaction quality is bounded by the compacting model's ability "
            "to understand what matters. A more capable model will produce better "
            "summaries because it can reason about relevance, identify dependencies "
            "between statements, and recognize which details are structural versus "
            "decorative. But even the best model is guessing about future relevance "
            "— it doesn't know what you'll ask next."
        ),
    },
    
    "casual_conversation": {
        "category": "Casual Chat",
        "text": (
            "Hey, how are you doing today? I was thinking about what you said "
            "yesterday about the project. I don't think we should rush it because "
            "there are still a lot of things we need to figure out. Let me know "
            "what you think and we can talk about it more later. By the way, did "
            "you see the new update? It's pretty cool but I'm not sure if it "
            "fixes the problem we were having."
        ),
    },
    
    "business_email": {
        "category": "Business / Professional",
        "text": (
            "Thank you for your prompt response regarding the quarterly report. "
            "I have reviewed the financial projections and would like to schedule "
            "a meeting to discuss the budget allocation for the upcoming fiscal year. "
            "In addition to the revenue forecasts, we should also consider the "
            "operational expenses and potential cost reduction strategies. Please "
            "let me know your availability for next week. I would appreciate it "
            "if you could also prepare a brief summary of the key performance "
            "indicators for the board presentation."
        ),
    },
    
    "technical_documentation": {
        "category": "Technical Documentation",
        "text": (
            "The system architecture consists of three primary components: the "
            "ingestion pipeline, the processing engine, and the storage layer. "
            "The ingestion pipeline handles incoming data from multiple sources "
            "including REST APIs, message queues, and batch file uploads. Data "
            "is validated, transformed, and normalized before being passed to "
            "the processing engine. The processing engine applies business logic, "
            "performs aggregations, and generates derived metrics. Results are "
            "persisted to the storage layer which supports both real-time queries "
            "and historical analysis through a combination of time-series databases "
            "and columnar data warehouses."
        ),
    },
    
    "creative_writing": {
        "category": "Creative / Narrative",
        "text": (
            "The old lighthouse keeper stood at the edge of the cliff, watching "
            "the storm clouds gather on the horizon. He had seen countless storms "
            "in his forty years at this post, but something about this one felt "
            "different. The air was heavy with electricity, and the seabirds had "
            "fallen silent hours ago. He checked the lamp one more time, making "
            "sure the mechanism was properly oiled and the lens was spotless. "
            "Tonight would be a long night, and the ships out there would need "
            "every bit of light he could give them."
        ),
    },
    
    "ai_research_abstract": {
        "category": "Academic / Research",
        "text": (
            "We present a novel approach to context window optimization in large "
            "language models through hierarchical lexical compression. Our method "
            "achieves significant token reduction without information loss by "
            "applying deterministic rule-based transformations at multiple levels "
            "of linguistic granularity. Unlike semantic compression approaches "
            "which require model inference and produce irreversible information "
            "loss, our system operates through precomputed codebook substitutions "
            "that preserve all original content. Empirical evaluation across "
            "multiple model sizes demonstrates that compressed text is accurately "
            "reconstructable by language models at all capability tiers, validating "
            "the core hypothesis that language models function as effective "
            "decompressors of lexically degraded input."
        ),
    },
    
    "customer_support": {
        "category": "Customer Support",
        "text": (
            "I understand your frustration with the billing issue. Let me look "
            "into this for you right away. It appears that the charge was applied "
            "twice due to a processing error on our end. I have initiated a refund "
            "for the duplicate charge, which should appear in your account within "
            "three to five business days. Is there anything else I can help you "
            "with today? If you experience any further issues, please don't "
            "hesitate to contact us again. We value your business and want to "
            "make sure this is resolved to your satisfaction."
        ),
    },
    
    "instructional": {
        "category": "How-to / Instructional",
        "text": (
            "To set up the development environment, first install the required "
            "dependencies using the package manager. Make sure you have the latest "
            "version of the runtime installed on your system. Next, clone the "
            "repository and navigate to the project directory. Create a virtual "
            "environment to isolate your project dependencies from the system "
            "packages. Activate the virtual environment and run the installation "
            "script. The configuration file should be updated with your specific "
            "settings before running the application for the first time. If you "
            "encounter any errors during setup, check the troubleshooting guide "
            "in the documentation."
        ),
    },
}


def run_benchmarks():
    """Run compression benchmarks across all test samples."""
    print("=" * 70)
    print("HLC BENCHMARK RESULTS")
    print("=" * 70)
    
    compressor = HLCCompressor()
    total_original = 0
    total_compressed = 0
    results = []
    
    for name, sample in TEST_SAMPLES.items():
        text = sample["text"]
        category = sample["category"]
        
        compressed = compressor.compress(text, layers=(1, 2, 3, 4))
        report = compressor.get_compression_report()
        
        total_original += report["original_chars"]
        total_compressed += report["compressed_chars"]
        
        result = {
            "name": name,
            "category": category,
            **report,
        }
        results.append(result)
        
        print(f"\n-- {category} ({name}) --")
        print(f"  Original:   {report['original_chars']} chars")
        print(f"  Compressed: {report['compressed_chars']} chars")
        print(f"  Saved:      {report['chars_saved']} chars ({report['compression_ratio']}%)")
        print(f"  L1 phrases: {report['layer1_phrase_replacements']}")
        print(f"  L2 words:   {report['layer2_word_replacements']}")
        print(f"  L3 symbols: {report['layer3_symbol_replacements']}")
        print(f"  L4 vowels:  {report['layer4_vowel_strips']}")
        print(f"  Compressed: {compressed[:100]}...")
    
    # Summary
    overall_ratio = round((total_original - total_compressed) / total_original * 100, 1)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n  Total original:   {total_original} chars")
    print(f"  Total compressed: {total_compressed} chars")
    print(f"  Total saved:      {total_original - total_compressed} chars")
    print(f"  Overall ratio:    {overall_ratio}%")
    
    print(f"\n  {'Category':<30} {'Original':>8} {'Compressed':>10} {'Ratio':>8}")
    print(f"  {'-'*30} {'-'*8} {'-'*10} {'-'*8}")
    for r in results:
        print(f"  {r['category']:<30} {r['original_chars']:>8} {r['compressed_chars']:>10} "
              f"{r['compression_ratio']:>7.1f}%")
    
    # Estimated token savings (rough: 1 token ≈ 4 chars for English)
    print(f"\n-- Estimated Token Impact --")
    est_orig_tokens = total_original / 4
    est_comp_tokens = total_compressed / 4
    print(f"  Est. original tokens:   ~{int(est_orig_tokens)}")
    print(f"  Est. compressed tokens: ~{int(est_comp_tokens)}")
    print(f"  Est. token savings:     ~{int(est_orig_tokens - est_comp_tokens)} tokens")
    
    # Cost projection
    print(f"\n-- Cost Projection (per 1M original tokens) --")
    # Anthropic Claude pricing approximate: $3/M input, $15/M output
    orig_cost = 3.0  # per 1M input tokens
    comp_ratio = overall_ratio / 100
    saved_cost = orig_cost * comp_ratio
    print(f"  Original cost (input):  ${orig_cost:.2f} / 1M tokens")
    print(f"  Compressed cost:        ${orig_cost - saved_cost:.2f} / 1M tokens")
    print(f"  Savings:                ${saved_cost:.2f} / 1M tokens ({overall_ratio}%)")
    print(f"  At 100M tokens/day:     ${saved_cost * 100:.0f}/day saved")
    
    return results


def show_layer_by_layer(text=None):
    """Show progressive compression of a text sample."""
    if text is None:
        text = TEST_SAMPLES["technical_discussion"]["text"]
    
    print("=" * 70)
    print("LAYER-BY-LAYER COMPRESSION")
    print("=" * 70)
    
    compressor = HLCCompressor()
    
    print(f"\n-- Original ({len(text)} chars) --")
    print(text)
    
    layer_names = {
        1: "Phrase Codebook",
        2: "Word Codebook",
        3: "Symbol Substitution",
        4: "Vowel Stripping",
    }
    
    for n in range(1, 5):
        layers = tuple(range(1, n + 1))
        compressed = compressor.compress(text, layers=layers)
        report = compressor.get_compression_report()
        print(f"\n-- +Layer {n}: {layer_names[n]} ({report['compressed_chars']} chars, "
              f"-{report['compression_ratio']}%) --")
        print(compressed)
    
    # Show deterministic decompression
    decompressor = HLCDecompressor()
    full_compressed = compressor.compress(text, layers=(1, 2, 3, 4))
    decompressed = decompressor.decompress(full_compressed)
    
    print(f"\n-- Deterministic Decompression --")
    print(decompressed)
    
    # Diff: what was perfectly recovered vs what needs LLM
    print(f"\n-- Recovery Analysis --")
    orig_words = set(text.lower().split())
    decomp_words = set(decompressed.lower().split())
    recovered = orig_words & decomp_words
    needs_llm = orig_words - decomp_words
    print(f"  Words perfectly recovered: {len(recovered)}/{len(orig_words)} "
          f"({len(recovered)/len(orig_words)*100:.0f}%)")
    if needs_llm:
        print(f"  Words needing LLM reconstruction: {needs_llm}")


if __name__ == "__main__":
    show_layer_by_layer()
    print("\n\n")
    run_benchmarks()
