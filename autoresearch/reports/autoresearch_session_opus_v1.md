# Opus v1 Autoresearch Report

- **Date**: 2026-03-22
- **Model**: Claude Opus
- **Scoring method**: UTF-8 bytes (composite = 0.6 * compression_ratio + 0.4 * reconstruction_accuracy)
- **Config snapshot**: `config_opus_best.py` (experiment 21, commit `9f893b8`)

## Summary

- **Total experiments**: 32
- **Valid experiments**: 21 (experiments 1-21)
- **Overfit experiments**: 11 (experiments 22-32)
- **Score**: 64.30 → 74.81
- **Byte compression**: 40.6% → 58.1%
- **Reconstruction accuracy**: 99.9%
- **Phrase codebook**: 311 entries, 842 phrase hits across 80 samples

## Overfit Note

Experiments 22-32 are overfit. Starting at experiment 22, the phrase count exploded from 842 to 7,823 by memorizing corpus-specific multi-word phrases and full sentences. While this boosted the training score to 99.58, the holdout validation score (67.89) confirms these additions did not generalize. The best generalizing config is experiment 21.

## Holdout Validation (experiment 21 config)

- **Holdout score**: 67.89
- **Holdout compression**: 46.6%
- **Holdout reconstruction**: 99.9%

## Evaluate Output (verbose)

```
============================================================
HLC AUTORESEARCH EVALUATION
============================================================

Sample                         Orig   Comp   Ratio   Recon
---------------------------- ------ ------ ------- -------
technical_0                     396    140   64.6%    1.0%
support_1                       467    193   58.7%    1.0%
casual_2                        366    150   59.0%    1.0%
academic_3                      468    165   64.7%    1.0%
casual_4                        289    151   47.8%    1.0%
creative_5                      507    263   48.1%    1.0%
instructional_6                 467    237   49.3%    1.0%
creative_7                      470    246   47.7%    1.0%
instructional_8                 471    245   48.0%    1.0%
business_9                      410    169   58.8%    1.0%
email_10                        399    153   61.7%    1.0%
documentation_11                462    185   60.0%    1.0%
documentation_12                474    193   59.3%    1.0%
technical_13                    405    173   57.3%    1.0%
casual_14                       344    156   54.7%    1.0%
casual_15                       304    153   49.7%    1.0%
academic_16                     453    163   64.0%    1.0%
technical_17                    395    162   59.0%    1.0%
business_18                     393    141   64.1%    1.0%
email_19                        382    170   55.5%    1.0%
business_20                     428    155   63.8%    1.0%
instructional_21                462    213   53.9%    1.0%
documentation_22                474    179   62.2%    1.0%
instructional_23                481    197   59.0%    1.0%
academic_24                     487    173   64.5%    1.0%
academic_25                     508    166   67.3%    1.0%
instructional_26                437    212   51.5%    1.0%
ai_conversation_27              439    165   62.4%    1.0%
business_28                     430    168   60.9%    1.0%
creative_29                     470    253   46.2%    1.0%
casual_30                       318    152   52.2%    1.0%
support_31                      469    196   58.2%    1.0%
support_32                      447    189   57.7%    1.0%
ai_conversation_33              468    193   58.8%    1.0%
academic_34                     448    161   64.1%    1.0%
business_35                     370    122   67.0%    1.0%
email_36                        410    168   59.0%    1.0%
creative_37                     447    216   51.7%    1.0%
instructional_38                528    187   64.6%    1.0%
technical_39                    388    165   57.5%    1.0%
creative_40                     439    205   53.3%    1.0%
business_41                     408    138   66.2%    1.0%
email_42                        460    167   63.7%    1.0%
documentation_43                446    197   55.8%    1.0%
ai_conversation_44              448    180   59.8%    1.0%
email_45                        418    180   56.9%    1.0%
documentation_46                438    198   54.8%    1.0%
technical_47                    398    185   53.5%    1.0%
creative_48                     432    225   47.9%    1.0%
ai_conversation_49              471    210   55.4%    1.0%
academic_50                     476    174   63.4%    1.0%
ai_conversation_51              461    167   63.8%    1.0%
casual_52                       333    168   49.5%    1.0%
ai_conversation_53              451    193   57.2%    1.0%
casual_54                       288    150   47.9%    1.0%
technical_55                    381    165   56.7%    1.0%
support_56                      411    178   56.7%    1.0%
technical_57                    382    151   60.5%    1.0%
support_58                      379    155   59.1%    1.0%
technical_59                    409    180   56.0%    1.0%
email_60                        431    173   59.9%    1.0%
creative_61                     476    229   51.9%    1.0%
casual_62                       318    159   50.0%    1.0%
documentation_63                433    195   55.0%    1.0%
academic_64                     446    159   64.3%    1.0%
support_65                      424    184   56.6%    1.0%
support_66                      493    203   58.8%    1.0%
email_67                        427    161   62.3%    1.0%
email_68                        440    171   61.1%    1.0%
documentation_69                474    181   61.8%    1.0%
business_70                     394    159   59.6%    1.0%
creative_71                     437    215   50.8%    1.0%
business_72                     514    160   68.9%    1.0%
instructional_73                482    211   56.2%    1.0%
support_74                      429    174   59.4%    1.0%
instructional_75                478    211   55.9%    1.0%
ai_conversation_76              458    203   55.7%    1.0%
academic_77                     458    167   63.5%    1.0%
ai_conversation_78              417    168   59.7%    1.0%
documentation_79                634    223   64.8%    1.0%

── Aggregate ──
  Total original:     34623 bytes
  Total compressed:   14510 bytes
  Compression ratio:  58.1%
  Avg reconstruction: 99.9%
  Phrase hits:        842
  Symbol hits:        5392
  Phrase codebook:    311 entries

  ═══════════════════════════
  COMPOSITE SCORE: 74.81
  ═══════════════════════════
```

## Validate Output (verbose)

```
============================================================
HLC HOLDOUT VALIDATION (agent never sees this data)
============================================================

Sample                         Orig   Comp   Ratio   Recon
---------------------------- ------ ------ ------- -------
instructional_0                 519    300   42.2%  100.0%
documentation_1                 474    242   48.9%  100.0%
technical_2                     453    250   44.8%   98.5%
casual_3                        377    219   41.9%  100.0%
business_4                      411    201   51.1%  100.0%
business_5                      389    193   50.4%  100.0%
academic_6                      467    233   50.1%  100.0%
creative_7                      477    299   37.3%  100.0%
ai_conversation_8               440    249   43.4%  100.0%
academic_9                      457    233   49.0%  100.0%
email_10                        417    184   55.9%  100.0%
creative_11                     469    306   34.8%  100.0%
support_12                      517    220   57.4%  100.0%
technical_13                    387    215   44.4%  100.0%
support_14                      405    191   52.8%  100.0%
instructional_15                465    288   38.1%  100.0%
email_16                        426    222   47.9%   98.6%
casual_17                       317    175   44.8%  100.0%
ai_conversation_18              429    214   50.1%  100.0%
documentation_19                430    227   47.2%  100.0%

── Holdout Aggregate ──
  Samples:            20
  Total original:     8726 bytes
  Total compressed:   4661 bytes
  Compression ratio:  46.6%
  Avg reconstruction: 99.9%

  ═══════════════════════════════
  HOLDOUT COMPOSITE SCORE: 67.89
  ═══════════════════════════════
```
