"""
HLC — Hierarchical Lexical Compression
========================================
A lossless, multi-layered approach to reducing LLM token costs
and extending effective context windows.

Usage:
    from hlc import compress, decompress, compress_with_report
    
    compressed = compress("Your text here")
    original = decompress(compressed)
    
    compressed, report = compress_with_report("Your text here")
    print(report)  # compression stats

Author: Ruzzel Maestro
License: TBD
"""

__version__ = "0.1.0"
__author__ = "Ruzzel Maestro"

from .compress import compress, decompress, compress_with_report
from .compress import HLCCompressor, HLCDecompressor
