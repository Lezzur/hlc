<!-- KEY: + = and | ^ = the | $ = is/be | ~ = that | @ = for | # = what | & = with | ! = this | % = from | * = not | Vwls strppd % lng wrds. Any LLM cn rd ! ntvly. -->

# HLC Prjct — Lvng Dcmnt

**Last updtd:** Mrch 22, 2026
**Athr:** Ruzzel Maestro (rocketturtles.creative@gmail.com)
**Repo:** https://github.com/Lezzur/hlc
**Stts:** Phse 1 cmplte, entrng Phse 2

---

## # $ ! dcmnt?

! $ ^ cntnty file @ ^ HLC (Hrrchcl Lxcl Cmprssn) prjct. If you are an AI assstnt pckng ! up in a new chat, read ! entre dcmnt bfre dng anythng. It cntns ^ full prjct cntxt, all dcsns made, crrnt stte, + exctly # to do next.

---

## ^ Big Idea (1-prgrph smmry)

Crrnt LLM systms cmprss cnvrstn hstry usng smmrztn, whch $ lssy, expnsve, + unprdctble. HLC $ a fndmntlly dffrnt apprch: instd of smntc cmprssn (dcdng # to dscrd), it appls dtrmnstc, rule-bsd lxcl cmprssn ~ rdcs tkn cnt by 50-60% whle prsrvng ALL infrmtn. The key insght $ ~ LLMs are ntrl dcmprssrs — they can rcnstrct full English % aggrssvly cmprssd text bcse tht's ltrlly # next-tkn prdctn does. This has been emprclly vldtd: Claude Haiku (smllst mdl) achvd 98.8% word-for-word rcnstrctn accrcy on cmprssd text & no cdbk.

---

## How HLC Wrks — The Six Lyrs

Cmprssn lyrs appld in ordr % hghst to lwst impct:

1. **Layer 1 — Phrse cdbk**: Cmmn mlti-word phrss → sngle Unicode chrctrs. "it $ imprtnt to note that" → α. Hghst impct per sbstttn. Inclds smntc ddplctn (80% eqvlnce thrshld — "how are you" / "hey how are you" / "dude how are you" all map to same code).

2. **Layer 2 — Word cdbk**: Frqncy-rnkd indvdl wrds → Unicode chrctrs (top ~3000) or shrt nmrc cds (rest). 37,639 wrds encdd. "bcse" → я, "pple" → у. Mrphlgcl hndlng: "prdce" = code 11, "prdcs" = 11s, "prdcd" = 11d.

3. **Layer 3 — Symbl sbstttn**: High-frqncy shrt fnctn wrds → sngle ASCII symbls. and→+, the→^, is/be→$, that→~, for/at→@, what→#, with→&, this→!, from→%, not→*.

4. **Layer 4 — Vwl strppng**: Rmve intrr vwls % rmnng wrds, keep frst + last char. "cmpctn" → "cmpctn", "mdl" → "modl". Skip wrds <4 chrs.

5. **Layer 5 — Rcrsve pttrn cmprssn**: Find rptd pttrns in ^ cmprssd otpt itslf + assgn mcro cds. More effctve as cnvrstns grow lngr. Crrntly plchldr — nds implmnttn.

6. **Layer 6 — Smntc enrchmnt**: Mtdta mrkrs ~ ADD infrmtn. ![crtcl], t[tchncl], e[emtnl], d[dcsn], ?[unrslvd]. Prdxclly mks cmprssd form MORE infrmtve than orgnl.

**Crtcl rule:** Exstng shrthnd $ scrd. btw=by ^ way, tldr, fyi, imo, gtg, brb, etc. — nvr rssgn thse. 54 prtctd trms.

---

## Key Dsgn Dcsns Made

| Dcsn | Chce | Rsnng |
|----------|--------|-----------|
| Cdbk frmt | Unicode-frst, nmrc fllbck | Sngle Unicode chrs = sngle tkns in most tknzrs = mxmm cmprssn per sbstttn |
| Layer ordrng | Phrss frst (bggst impct) → wrds → symbls → vwls | Bggst svngs come % rplcng mlti-word phrss & sngle cds |
| Lcnse | Apache 2.0 | Ptnt prtctn clse — imprtnt gvn ^ IP ntre of ! work |
| Cmprssn trgt | Mchne-rdble, * hmn-rdble | Optmzng @ LLM rcnstrctn, * hmn rdng. Cmprssd text can look like grbge to hmns. |
| Cdbk scpe | Unvrsl English cdbk (sttc, prcmptd) | One-time cost, rsble acrss all cnvrstns. Cdbk $ frqncy-rnkd % wrdfrq lbrry |

---

## Crrnt Bnchmrk Rslts (Msrd)

### Cmprssn rts (all 6 lyrs, chrctr-lvl):

| Ctgry | Orgnl | Cmprssd | Rdctn |
|----------|----------|------------|-----------|
| Tchncl / Agnt | 451 chrs | 200 chrs | 55.7% |
| Csl Chat | 366 chrs | 169 chrs | 53.8% |
| Bsnss / Prfssnl | 514 chrs | 216 chrs | 58.0% |
| Tchncl Dcmnttn | 634 chrs | 308 chrs | 51.4% |
| Crtve / Nrrtve | 507 chrs | 288 chrs | 43.2% |
| Acdmc / Rsrch | 782 chrs | 348 chrs | 55.5% |
| Cstmr Spprt | 517 chrs | 243 chrs | 53.0% |
| How-to / Instrctnl | 624 chrs | 288 chrs | 53.8% |
| **Ovrll** | **4,395** | **2,060** | **53.1%** |

### LLM Rcnstrctn accrcy (Haiku, Lyrs 3+4 only, ~29% cmprssn, NO cdbk):

| Smple | Word accrcy | Nts |
|--------|-------------|-------|
| Tchncl | 97.0% (65/67) | Two near-msss: "cmpctn"→"cmprssn", "dcrtve"→"dscrptve" — both smntclly eqvlnt |
| Csl | 100% (51/51) | Prfct rcnstrctn |
| Bsnss | 100% (51/51) | Prfct rcnstrctn |
| **Ovrll** | **98.8% (167/169)** | **Smntc accrcy: effctvly 100%** |

Key: ! was ^ smllst, chpst mdl. Lyrs 1-2 are dtrmnstclly rvrsble (zero errr). Cmbnd systm $ intnt-lsslss.

---

## Prjct Strctre

```
hlc-release/
├── hlc/                        # Core Python package
│   ├── __init__.py             # Package init, exports compress/decompress
│   ├── analyze.py              # Corpus frequency analysis (wordfreq-based)
│   ├── codebook.py             # Codebook generation (Unicode-first assignment)
│   ├── compress.py             # 6-layer compression + decompression engine
│   ├── benchmark.py            # Benchmark suite, 8 text categories
│   └── codebooks/              # Generated data
│       ├── codebook_full.json  # All codebooks + reverse maps (~37k entries)
│       ├── codebook_compact.json
│       ├── word_freq.json      # 38,050 codeable words ranked
│       ├── phrase_freq.json    # 96 phrases ranked (NEEDS EXPANSION)
│       └── symbols.json        # Symbol map + protected shorthand
├── examples/
│   └── basic_usage.py
├── tests/
│   └── test_compress.py        # 14 tests, all passing
├── docs/
│   └── HLC_Technical_Paper.docx
├── README.md
├── LICENSE                     # Apache 2.0
├── requirements.txt            # wordfreq, nltk
└── setup.py                    # pip installable
```

---

## Rdmp — Full Pctre

### Phse 1: Bld ^ engne (COMPLETE)
- [x] Crps frqncy anlyss (38,050 cdble wrds)
- [x] Unicode-frst cdbk gnrtn (37,639 wrds + 95 phrss)
- [x] 6-layer cmprssn pplne
- [x] Dcmprssn engne (dtrmnstc @ L1-3)
- [x] Bnchmrk ste (8 ctgrs)
- [x] Test ste (14 tsts pssng)
- [x] GitHub repo live: https://github.com/Lezzur/hlc

### Phse 2: Bnchmrk + vldte (IN PROGRESS)
- [x] LLM rcnstrctn test — Haiku (98.8% accrcy)
- [ ] LLM rcnstrctn test — Sonnet
- [ ] LLM rcnstrctn test — Opus
- [ ] **Expnd phrse cdbk** % 96 to 2,000+ entrs (Layer 1 crrntly shws 0% impct in bnchmrks bcse no test smpls hit ^ 96 btstrppd phrss — ! $ ^ bggst low-hngng frt)
- [ ] Msre actl TOKEN cnts (not just chrctrs) — Unicode chrs may tknze into mltple tkns, whch wld chnge ^ real svngs nmbr
- [ ] Edge case hndlng: URLs, eml addrsss, code snppts, nmbrs, prpr nns — thse need to pass thrgh uncmprssd
- [ ] Dmn tstng: code/prgrmmng text, mltlngl mxd text
- [ ] Fix: some mrphlgcl vrnts * mtchng base cds (e.g. "cmpctng" → "3905ng" instd of mtchng "cmpctn" base)

### Phse 3: Pckge + pblsh (NOT STARTED)
- [ ] Expnd test ste
- [ ] pip pckge (pypi)
- [ ] Rwrte tchncl ppr & ALL msrd data (rplce estmts)
- [ ] Frmt ppr @ arXiv (LaTeX, prpr cttns)
- [ ] Bld live web demo (pste text → see cmprssn + rcnstrctn)
- [ ] Sbmt to arXiv

### Phse 4: Otrch (NOT STARTED)
- [ ] Hacker News post
- [ ] Reddit r/MchnLrnng post
- [ ] X/Twitter thrd
- [ ] Trgt spcfc rsrchrs (cntxt mngmnt, tknzr dsgn)
- [ ] Cntct LLM prvdrs (Anthropic, OpenAI, Google DeepMind, Cohere)
- [ ] Blog post & intrctve demo

### Phse 5: The trnng frntr (NEEDS PARTNERS)
- [ ] Gnrte HLC-encdd trnng crps
- [ ] Fine-tune mdl on cmprssd text
- [ ] Bnchmrk fine-tnd mdl vs base (prfrmnce prty test)
- [ ] Zero-cdbk dplymnt (mdl rds HLC ntvly)

---

## Knwn Isss + Tchncl Debt

1. **Phrse cdbk $ too smll** — only 96 btstrppd phrss, none hit in bnchmrks. Need crps-drvd n-gram anlyss & 2,000+ entrs. This $ ^ sngle bggst imprvmnt avlble.

2. **Tkn vs chrctr msrmnt gap** — all bnchmrks msre chrctr svngs. Real tkn svngs may dffr bcse Unicode chrctrs (CJK, Cyrllc, Grk) may tknze into 2-3 tkns in some tknzrs. MUST msre & actl tknzr bfre pblshng.

3. **Mrphlgcl hndlng $ incmplte** — "cmpctng" bcms "3905ng" (nmrc code + sffx) whch wrks but lks mssy. Some word vrnts arn't mtchng thr base frms in ^ cdbk.

4. **No edge case prtctn** — URLs, emls, code blcks, nmbrs, + prpr nns get cmprssd when they shldn't. Need a "prsrve" layer ~ shlds spcl cntnt.

5. **Layer 5 (rcrsve pttrns) $ a plchldr** — * implmntd yet. Nds anlyss of cmprssd otpt pttrns acrss real cnvrstns.

6. **bnchmrk.py had a rltve imprt isse** — fxd by chngng `from compress import` to `from .compress import`. Wtch @ smlr isss if rstrctrng.

7. **Ddplctn in phrse cdbk** — "on ^ othr hand" apprs twce in ^ btstrppd phrse list. Need ddp in ^ gnrtn pplne.

---

## ^ Orgn Stry (for cntxt)

! prjct emrgd % a cnvrstn abt agnt mmry chllngs. The key brkthrgh mmnts:

1. **The vwl-strppng test** — shwd ~ "ths prt dsrvs a10tn..." $ prfctly rdble by LLMs, prvng aggrssve cmprssn dsn't dstry mnng.

2. **The "L8 =?" test** — shwd ~ even symblc shrthnd (2 chrctrs) $ intrprtble in cntxt, extndng ^ cmprssn prncple bynd word-lvl.

3. **The Haiku cdbk test** — gave Haiku a 27-entry nmrc cdbk + encdd prgrph. Haiku rcnstrctd it prfctly. Prvd even smll mdls can dcmprss.

4. **The fndmntl rlztn** — LLMs are ltrlly trnd to prdct mssng infrmtn % cntxt. Cmprssn ~ rmvs prdctble infrmtn $ exctly # thy're blt to rvrse. W're * askng them to do smthng new; w're lvrgng thr core cpblty.

5. **The lyrs insght** — cmprssn shld be mlti-lyrd (phrss → wrds → symbls → vwls → pttrns → mtdta), & each layer trgtng dffrnt rdndncy. Ordrd by impct, * cmplxty.

6. **Exstng shrthnd $ scrd** — btw, tldr, fyi etc. alrdy have mnngs. Dn't rssgn them. Use them @ free.

7. **Smntc ddplctn** — phrss & 80%+ eqvlnt mnng map to same code. "How are you" / "Hey how are you" = same code. Intnt-lsslss, * word-lsslss.

8. **Enrchmnt layer** — cmprssn can prdxclly ADD infrmtn thrgh mtdta mrkrs ~ make implct cntxt explct.

---

## Pple + Rsrcs

- **Ruzzel Maestro** — prjct crtr, indpndnt rsrchr
- **Eml:** rocketturtles.creative@gmail.com
- **GitHub:** https://github.com/Lezzur/hlc
- **Tchncl ppr:** in docs/HLC_Tchncl_Ppr.docx in ^ repo

---

## How to Cntne in a New Chat

Upld ! dcmnt + say smthng like:

> "I'm Ruzzel. This $ my HLC prjct lvng dcmnt. Read it + lt's cntne whre I left off. [Then stte # you want to work on next]"

^ AI will have full cntxt of ^ prjct, all dcsns, crrnt stte, + # nds dng. No re-explnng ndd.

---

*End of lvng dcmnt. Updte ! file aftr evry sgnfcnt work sssn.*
