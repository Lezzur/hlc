# HLC Token Measurement Report

**Date:** 2026-03-23
**Tokenizer:** cl100k_base (GPT-4, GPT-3.5-turbo)
**Measurement Tool:** tiktoken v0.12.0

## Summary

This report compares token-level compression performance of two HLC configurations:
- **config_sonnet_best.py**: 528 symbols + 196 phrases
- **config_opus_v2_best.py**: 1120 symbols + 617 phrases (experiment 15)

---

## Comparison Table

### Character / Byte / Token Compression by Split

| Config | Split | Char% | Byte% | Token% | Char->Byte Gap | Byte->Token Gap |
|--------|-------|-------|-------|--------|----------------|-----------------|
| **Sonnet Best** | train | 39.8% | 33.5% | **-81.3%** | 6.3pp | **114.8pp** |
| | val | 39.7% | 33.4% | **-80.7%** | 6.3pp | **114.2pp** |
| | holdout | 39.7% | 33.7% | **-81.2%** | 6.0pp | **115.0pp** |
| **Opus v2 Best** | train | 53.4% | 47.9% | **-70.5%** | 5.5pp | **118.4pp** |
| | val | 57.7% | 51.0% | **-69.3%** | 6.6pp | **120.3pp** |
| | holdout | 48.7% | 43.7% | **-79.1%** | 5.0pp | **122.9pp** |

### Key Findings

1. **Byte->Token Gap Analysis**:
   - **Sonnet Best**: 114.8pp avg byte->token gap
   - **Opus v2 Best**: 120.3pp avg byte->token gap
   - **Opus v2 shows a LARGER gap** (+5.5pp on average), meaning it gets WORSE token expansion

2. **Character & Byte Compression**:
   - **Opus v2** achieves significantly better char (53.4% vs 39.8%) and byte (47.9% vs 33.5%) compression
   - This is expected given the larger codebook (1737 total entries vs 724)

3. **Token Expansion Problem**:
   - Both configs show **severe token expansion** (negative compression)
   - **Sonnet**: -81% average token compression
   - **Opus v2**: -73% average token compression
   - Despite better byte compression, Opus v2 still suffers from poor tokenization

4. **Symbol Efficiency**:
   - **Sonnet**: Only 6-12% of symbols are token-efficient (33/528 cl100k, 66/528 o200k)
   - **Opus v2**: Only 10-13% efficient (112/1120 cl100k, 142/1120 o200k)
   - Most symbols are wasteful or neutral for token compression

---

## Full Output: config_sonnet_best.py

```
======================================================================
HLC TOKEN MEASUREMENT REPORT
Config: config_sonnet_best.py
SYMBOL_MAP: 528 | PHRASE_CODEBOOK: 196
Corpus: train(210), val(45), holdout(45)
======================================================================

-- SYMBOL TOKENIZATION AUDIT --

  cl100k_base:
    Efficient: 33/528 (6%)
    Neutral:   201  |  Wasteful: 294
    Wasteful (top 10):
      'at' (1t) -> 'ㄬ' (3t) = -2
      'give' (1t) -> 'ㄱ' (3t) = -2
      'tell' (1t) -> 'ㄴ' (3t) = -2
      'come' (1t) -> 'ㄷ' (3t) = -2
      'call' (1t) -> 'ㄹ' (3t) = -2
      'ask' (1t) -> 'ㄸ' (3t) = -2
      'monitor' (1t) -> '㄀' (3t) = -2
      'control' (1t) -> '㄁' (3t) = -2
      'increase' (1t) -> '㄄' (3t) = -2
      'process' (1t) -> 'ㄆ' (3t) = -2
    Token cost distribution: {1: 190, 2: 232, 3: 106}

  o200k_base:
    Efficient: 66/528 (12%)
    Neutral:   316  |  Wasteful: 146
    Wasteful (top 10):
      'be' (1t) -> 'ㅟ' (2t) = -1
      'at' (1t) -> 'ㄬ' (2t) = -1
      'give' (1t) -> 'ㄱ' (2t) = -1
      'tell' (1t) -> 'ㄴ' (2t) = -1
      'come' (1t) -> 'ㄷ' (2t) = -1
      'call' (1t) -> 'ㄹ' (2t) = -1
      'ask' (1t) -> 'ㄸ' (2t) = -1
      'try' (1t) -> 'ㅁ' (2t) = -1
      'back' (1t) -> 'ㅂ' (2t) = -1
      'hand' (1t) -> 'ㅄ' (2t) = -1
    Token cost distribution: {1: 353, 2: 175}

-- CORPUS: CHARS vs BYTES vs TOKENS --

  cl100k_base:

    [TRAIN] (210 samples)
      Char compression:  39.8%
      Byte compression:  33.5%
      TOKEN compression: -81.3%
      Tokens: 14,531 -> 26,344 (saved -11,813)
      Gaps: char->byte 6.3pp | byte->token 114.8pp

      Category            Char%  Byte%  Token%  B->T
      ────────────────── ────── ────── ─────── ─────
      academic            40.0%  34.2% -106.4% 140.6
      ai_conversation     40.1%  33.5%  -77.5% 111.0
      business            41.5%  35.2%  -98.5% 133.7
      casual              36.8%  30.1%  -58.9% 89.0
      conversational_ai   39.9%  33.6%  -80.2% 113.8
      creative            36.1%  30.5%  -68.0% 98.5
      documentation       42.4%  35.4%  -91.2% 126.6
      email               45.5%  37.8%  -77.2% 114.9
      instructional       36.6%  29.7%  -69.4% 99.1
      journalism          37.3%  32.3%  -98.3% 130.5
      legal               37.1%  32.9%  -94.7% 127.5
      marketing           39.1%  32.5%  -76.4% 108.9
      medical             38.6%  32.9%  -77.4% 110.4
      support             46.3%  38.1%  -78.0% 116.1
      technical           40.0%  33.9%  -78.5% 112.4

    [VAL] (45 samples)
      Char compression:  39.7%
      Byte compression:  33.4%
      TOKEN compression: -80.7%
      Tokens: 3,080 -> 5,567 (saved -2,487)
      Gaps: char->byte 6.3pp | byte->token 114.2pp

      Category            Char%  Byte%  Token%  B->T
      ────────────────── ────── ────── ─────── ─────
      academic            39.7%  34.2%  -89.9% 124.2
      ai_conversation     41.0%  34.9%  -79.8% 114.7
      business            41.7%  35.0%  -92.1% 127.1
      casual              35.5%  29.5%  -60.3% 89.8
      conversational_ai   42.3%  36.6%  -70.7% 107.3
      creative            35.0%  30.4%  -70.6% 101.0
      documentation       41.0%  34.0%  -94.0% 128.0
      email               46.2%  37.5%  -92.5% 130.1
      instructional       37.9%  29.6%  -69.6% 99.2
      journalism          39.3%  33.8% -101.0% 134.8
      legal               39.2%  33.7%  -96.1% 129.9
      marketing           38.5%  33.2%  -71.2% 104.4
      medical             38.5%  33.3%  -84.4% 117.7
      support             43.8%  35.2%  -75.9% 111.1
      technical           34.9%  29.1%  -70.1% 99.2

    [HOLDOUT] (45 samples)
      Char compression:  39.7%
      Byte compression:  33.7%
      TOKEN compression: -81.2%
      Tokens: 3,097 -> 5,613 (saved -2,516)
      Gaps: char->byte 6.0pp | byte->token 115.0pp

      Category            Char%  Byte%  Token%  B->T
      ────────────────── ────── ────── ─────── ─────
      academic            35.1%  32.4% -106.6% 139.1
      ai_conversation     43.2%  37.2%  -74.8% 112.0
      business            42.5%  35.4%  -90.8% 126.1
      casual              36.3%  29.7%  -63.6% 93.4
      conversational_ai   40.7%  34.8%  -78.5% 113.3
      creative            36.5%  31.0%  -72.4% 103.4
      documentation       40.3%  33.8%  -86.3% 120.0
      email               46.1%  37.1%  -77.2% 114.2
      instructional       33.6%  28.5%  -67.7% 96.1
      journalism          39.3%  34.0%  -97.2% 131.2
      legal               40.5%  33.9% -103.3% 137.2
      marketing           39.7%  32.5%  -86.4% 118.9
      medical             36.3%  32.3%  -70.5% 102.8
      support             46.6%  39.0%  -75.8% 114.8
      technical           40.0%  34.1%  -79.2% 113.2

  o200k_base:

    [TRAIN] (210 samples)
      Char compression:  39.8%
      Byte compression:  33.5%
      TOKEN compression: -66.3%
      Tokens: 14,343 -> 23,851 (saved -9,508)
      Gaps: char->byte 6.3pp | byte->token 99.8pp

      Category            Char%  Byte%  Token%  B->T
      ────────────────── ────── ────── ─────── ─────
      academic            40.0%  34.2%  -88.8% 123.0
      ai_conversation     40.1%  33.5%  -62.9% 96.4
      business            41.5%  35.2%  -77.2% 112.4
      casual              36.8%  30.1%  -50.6% 80.6
      conversational_ai   39.9%  33.6%  -67.1% 100.7
      creative            36.1%  30.5%  -56.1% 86.6
      documentation       42.4%  35.4%  -72.2% 107.6
      email               45.5%  37.8%  -56.5% 94.2
      instructional       36.6%  29.7%  -55.7% 85.4
      journalism          37.3%  32.3%  -81.8% 114.0
      legal               37.1%  32.9%  -81.1% 114.0
      marketing           39.1%  32.5%  -65.9% 98.4
      medical             38.6%  32.9%  -65.6% 98.5
      support             46.3%  38.1%  -55.7% 93.8
      technical           40.0%  33.9%  -65.3% 99.2

    [VAL] (45 samples)
      Char compression:  39.7%
      Byte compression:  33.4%
      TOKEN compression: -65.4%
      Tokens: 3,047 -> 5,041 (saved -1,994)
      Gaps: char->byte 6.3pp | byte->token 98.9pp

      Category            Char%  Byte%  Token%  B->T
      ────────────────── ────── ────── ─────── ─────
      academic            39.7%  34.2%  -78.4% 112.6
      ai_conversation     41.0%  34.9%  -66.9% 101.8
      business            41.7%  35.0%  -75.7% 110.7
      casual              35.5%  29.5%  -51.3% 80.9
      conversational_ai   42.3%  36.6%  -59.4% 95.9
      creative            35.0%  30.4%  -58.2% 88.6
      documentation       41.0%  34.0%  -73.8% 107.9
      email               46.2%  37.5%  -68.5% 106.0
      instructional       37.9%  29.6%  -51.9% 81.5
      journalism          39.3%  33.8%  -84.7% 118.5
      legal               39.2%  33.7%  -74.9% 108.7
      marketing           38.5%  33.2%  -61.7% 95.0
      medical             38.5%  33.3%  -73.4% 106.6
      support             43.8%  35.2%  -50.6% 85.8
      technical           34.9%  29.1%  -57.3% 86.4

    [HOLDOUT] (45 samples)
      Char compression:  39.7%
      Byte compression:  33.7%
      TOKEN compression: -66.3%
      Tokens: 3,056 -> 5,081 (saved -2,025)
      Gaps: char->byte 6.0pp | byte->token 100.0pp

      Category            Char%  Byte%  Token%  B->T
      ────────────────── ────── ────── ─────── ─────
      academic            35.1%  32.4% -105.7% 138.2
      ai_conversation     43.2%  37.2%  -61.3% 98.4
      business            42.5%  35.4%  -68.9% 104.3
      casual              36.3%  29.7%  -57.4% 87.2
      conversational_ai   40.7%  34.8%  -64.2% 99.0
      creative            36.5%  31.0%  -60.7% 91.7
      documentation       40.3%  33.8%  -69.2% 103.0
      email               46.1%  37.1%  -51.3% 88.4
      instructional       33.6%  28.5%  -56.8% 85.3
      journalism          39.3%  34.0%  -78.4% 112.4
      legal               40.5%  33.9%  -78.2% 112.1
      marketing           39.7%  32.5%  -66.1% 98.6
      medical             36.3%  32.3%  -68.7% 101.0
      support             46.6%  39.0%  -50.6% 89.6
      technical           40.0%  34.1%  -64.9% 98.9

-- SUMMARY FOR PAPER --

  Tokenizer: cl100k_base
  Config: config_sonnet_best.py

  Split        Char%   Byte%   Token%  C->B  B->T
  ────────── ─────── ─────── ──────── ───── ─────
  train        39.8%   33.5%   -81.3%  6.3 114.8
  val          39.7%   33.4%   -80.7%  6.3 114.2
  holdout      39.7%   33.7%   -81.2%  6.0 115.0
```

---

## Full Output: config_opus_v2_best.py

```
======================================================================
HLC TOKEN MEASUREMENT REPORT
Config: config_opus_v2_best.py
SYMBOL_MAP: 1120 | PHRASE_CODEBOOK: 617
Corpus: train(210), val(45), holdout(45)
======================================================================

-- SYMBOL TOKENIZATION AUDIT --

  cl100k_base:
    Efficient: 112/1120 (10%)
    Neutral:   405  |  Wasteful: 603
    Wasteful (top 10):
      'into' (1t) -> 'ՠ' (2t) = -1
      'there' (1t) -> 'Ӄ' (2t) = -1
      'other' (1t) -> 'ǈ' (2t) = -1
      'them' (1t) -> 'Ѥ' (2t) = -1
      'well' (1t) -> 'ƾ' (2t) = -1
      'work' (1t) -> 'ǎ' (2t) = -1
      'know' (1t) -> 'ѧ' (2t) = -1
      'good' (1t) -> 'Ȭ' (2t) = -1
      'way' (1t) -> 'ǁ' (2t) = -1
      'want' (1t) -> 'һ' (2t) = -1
    Token cost distribution: {1: 247, 2: 873}

  o200k_base:
    Efficient: 142/1120 (13%)
    Neutral:   477  |  Wasteful: 501
    Wasteful (top 10):
      'into' (1t) -> 'ՠ' (2t) = -1
      'there' (1t) -> 'Ӄ' (2t) = -1
      'other' (1t) -> 'ǈ' (2t) = -1
      'them' (1t) -> 'Ѥ' (2t) = -1
      'well' (1t) -> 'ƾ' (2t) = -1
      'know' (1t) -> 'ѧ' (2t) = -1
      'good' (1t) -> 'Ȭ' (2t) = -1
      'way' (1t) -> 'ǁ' (2t) = -1
      'year' (1t) -> 'ǖ' (2t) = -1
      'zero' (1t) -> 'ʩ' (2t) = -1
    Token cost distribution: {1: 402, 2: 718}

-- CORPUS: CHARS vs BYTES vs TOKENS --

  cl100k_base:

    [TRAIN] (210 samples)
      Char compression:  53.4%
      Byte compression:  47.9%
      TOKEN compression: -70.5%
      Tokens: 14,531 -> 24,780 (saved -10,249)
      Gaps: char->byte 5.5pp | byte->token 118.4pp

      Category            Char%  Byte%  Token%  B->T
      ────────────────── ────── ────── ─────── ─────
      academic            54.7%  49.8%  -86.8% 136.6
      ai_conversation     51.8%  46.1%  -73.8% 120.0
      business            59.7%  53.7%  -76.7% 130.4
      casual              44.0%  38.7%  -61.3% 100.0
      conversational_ai   53.6%  48.0%  -66.0% 114.0
      creative            45.8%  41.2%  -66.6% 107.9
      documentation       57.3%  51.2%  -77.9% 129.2
      email               59.0%  52.5%  -63.8% 116.4
      instructional       45.6%  40.7%  -62.9% 103.6
      journalism          53.0%  48.1%  -83.7% 131.8
      legal               55.1%  49.4%  -77.4% 126.8
      marketing           52.3%  46.5%  -74.5% 120.9
      medical             54.7%  49.2%  -63.1% 112.3
      support             61.0%  54.6%  -59.0% 113.6
      technical           52.1%  46.7%  -71.5% 118.2

    [VAL] (45 samples)
      Char compression:  57.7%
      Byte compression:  51.0%
      TOKEN compression: -69.3%
      Tokens: 3,080 -> 5,215 (saved -2,135)
      Gaps: char->byte 6.6pp | byte->token 120.3pp

      Category            Char%  Byte%  Token%  B->T
      ────────────────── ────── ────── ─────── ─────
      academic            53.6%  48.2%  -79.2% 127.4
      ai_conversation     52.8%  46.6%  -77.6% 124.3
      business            63.0%  56.3%  -71.0% 127.4
      casual              48.0%  40.7%  -65.7% 106.5
      conversational_ai   57.2%  50.8%  -62.4% 113.3
      creative            51.7%  45.5%  -73.2% 118.7
      documentation       61.4%  53.3%  -74.2% 127.5
      email               66.0%  58.4%  -69.8% 128.2
      instructional       52.6%  46.2%  -59.9% 106.2
      journalism          58.3%  52.6%  -79.7% 132.4
      legal               61.7%  54.7%  -71.7% 126.4
      marketing           58.8%  52.3%  -62.9% 115.2
      medical             55.1%  49.2%  -73.5% 122.6
      support             66.1%  58.1%  -60.6% 118.6
      technical           56.4%  49.8%  -65.7% 115.5

    [HOLDOUT] (45 samples)
      Char compression:  48.7%
      Byte compression:  43.7%
      TOKEN compression: -79.1%
      Tokens: 3,097 -> 5,548 (saved -2,451)
      Gaps: char->byte 5.0pp | byte->token 122.9pp

      Category            Char%  Byte%  Token%  B->T
      ────────────────── ────── ────── ─────── ─────
      academic            42.1%  39.7%  -99.9% 139.7
      ai_conversation     50.3%  45.3%  -78.9% 124.2
      business            55.9%  50.0%  -72.3% 122.3
      casual              45.1%  39.5%  -63.7% 103.2
      conversational_ai   50.3%  45.0%  -79.2% 124.2
      creative            44.2%  39.5%  -79.7% 119.2
      documentation       55.3%  48.6%  -83.3% 131.9
      email               50.1%  44.1%  -81.6% 125.7
      instructional       39.0%  35.5%  -68.5% 104.0
      journalism          46.8%  42.7%  -94.6% 137.3
      legal               52.3%  46.5%  -91.2% 137.7
      marketing           48.0%  43.4%  -78.6% 122.0
      medical             45.4%  40.9%  -78.1% 119.0
      support             52.5%  47.2%  -68.0% 115.3
      technical           53.5%  47.8%  -79.0% 126.8

  o200k_base:

    [TRAIN] (210 samples)
      Char compression:  53.4%
      Byte compression:  47.9%
      TOKEN compression: -58.3%
      Tokens: 14,343 -> 22,699 (saved -8,356)
      Gaps: char->byte 5.5pp | byte->token 106.2pp

      Category            Char%  Byte%  Token%  B->T
      ────────────────── ────── ────── ─────── ─────
      academic            54.7%  49.8%  -73.7% 123.6
      ai_conversation     51.8%  46.1%  -60.9% 107.0
      business            59.7%  53.7%  -61.6% 115.3
      casual              44.0%  38.7%  -51.2% 89.9
      conversational_ai   53.6%  48.0%  -59.7% 107.7
      creative            45.8%  41.2%  -56.7% 97.9
      documentation       57.3%  51.2%  -61.7% 112.9
      email               59.0%  52.5%  -47.6% 100.1
      instructional       45.6%  40.7%  -51.9% 92.6
      journalism          53.0%  48.1%  -69.3% 117.4
      legal               55.1%  49.4%  -62.4% 111.8
      marketing           52.3%  46.5%  -63.1% 109.6
      medical             54.7%  49.2%  -53.5% 102.7
      support             61.0%  54.6%  -42.8% 97.4
      technical           52.1%  46.7%  -63.0% 109.7

    [VAL] (45 samples)
      Char compression:  57.7%
      Byte compression:  51.0%
      TOKEN compression: -52.0%
      Tokens: 3,047 -> 4,631 (saved -1,584)
      Gaps: char->byte 6.6pp | byte->token 103.0pp

      Category            Char%  Byte%  Token%  B->T
      ────────────────── ────── ────── ─────── ─────
      academic            53.6%  48.2%  -65.0% 113.3
      ai_conversation     52.8%  46.6%  -60.5% 107.1
      business            63.0%  56.3%  -54.2% 110.6
      casual              48.0%  40.7%  -48.1% 88.8
      conversational_ai   57.2%  50.8%  -53.2% 104.0
      creative            51.7%  45.5%  -58.9% 104.4
      documentation       61.4%  53.3%  -59.2% 112.5
      email               66.0%  58.4%  -44.2% 102.6
      instructional       52.6%  46.2%  -45.8% 92.1
      journalism          58.3%  52.6%  -62.7% 115.3
      legal               61.7%  54.7%  -48.2% 102.9
      marketing           58.8%  52.3%  -51.5% 103.8
      medical             55.1%  49.2%  -56.0% 105.1
      support             66.1%  58.1%  -33.4% 91.5
      technical           56.4%  49.8%  -43.9% 93.7

    [HOLDOUT] (45 samples)
      Char compression:  48.7%
      Byte compression:  43.7%
      TOKEN compression: -66.4%
      Tokens: 3,056 -> 5,086 (saved -2,030)
      Gaps: char->byte 5.0pp | byte->token 110.2pp

      Category            Char%  Byte%  Token%  B->T
      ────────────────── ────── ────── ─────── ─────
      academic            42.1%  39.7%  -97.5% 137.2
      ai_conversation     50.3%  45.3%  -62.5% 107.8
      business            55.9%  50.0%  -55.2% 105.2
      casual              45.1%  39.5%  -51.7% 91.2
      conversational_ai   50.3%  45.0%  -66.4% 111.5
      creative            44.2%  39.5%  -67.3% 106.8
      documentation       55.3%  48.6%  -69.6% 118.2
      email               50.1%  44.1%  -62.4% 106.5
      instructional       39.0%  35.5%  -62.5% 98.0
      journalism          46.8%  42.7%  -85.3% 128.0
      legal               52.3%  46.5%  -68.1% 114.6
      marketing           48.0%  43.4%  -62.9% 106.3
      medical             45.4%  40.9%  -71.8% 112.7
      support             52.5%  47.2%  -53.8% 101.0
      technical           53.5%  47.8%  -65.0% 112.8

-- SUMMARY FOR PAPER --

  Tokenizer: cl100k_base
  Config: config_opus_v2_best.py

  Split        Char%   Byte%   Token%  C->B  B->T
  ────────── ─────── ─────── ──────── ───── ─────
  train        53.4%   47.9%   -70.5%  5.5 118.4
  val          57.7%   51.0%   -69.3%  6.6 120.3
  holdout      48.7%   43.7%   -79.1%  5.0 122.9
```

---

## Conclusions

1. **Token expansion remains the critical problem for HLC**: Both configs show severe negative token compression despite strong byte-level gains.

2. **Opus v2 Best (exp 15) underperforms in token metrics**: While it achieves better byte compression (47.9% vs 33.5%), it has a WORSE byte→token gap (120.3pp vs 114.8pp average).

3. **Symbol efficiency is poor across the board**: 87-94% of symbols are either neutral or wasteful from a token perspective.

4. **Validation set shows highest variance**: Opus v2's val split achieves 57.7% char compression and -69.3% token compression, but the holdout split regresses to 48.7% char / -79.1% token.

5. **Recommendation**: If token compression is the target metric (as it should be for LLM applications), **neither config is production-ready**. The byte→token gap needs to be closed through token-aware symbol selection.
