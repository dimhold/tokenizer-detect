# Sources for the Y axis and for the resource proxy

Every number in `y-multitude.tsv`, `y-multitude-finetuned-by-llm.tsv`,
`y-pangram4.tsv` and `resource-cc.tsv` was copied character for character from
the tables listed below. Nothing was rounded, averaged, converted or filled in.
Where a source cell is empty, the file carries the source's own em dash and not
a number.

Date of access for all three sources: **2026-09-05**.

---

## 1. MULTITuDE: macro average F1-score per language

**Paper:** Macko et al., *MULTITuDE: Large-Scale Multilingual Machine-Generated
Text Detection Benchmark*, EMNLP 2023.

| what | value |
|---|---|
| arXiv | https://arxiv.org/abs/2310.13606 |
| HTML used for extraction | https://arxiv.org/html/2310.13606v1 |
| Published version used for verification | https://aclanthology.org/2023.emnlp-main.616.pdf |
| Metric | Macro average F1-score |

The metric is stated twice in the paper. In section 5: *"The results are ordered
according to the achieved macro average F1-score (since the test data are highly
imbalanced in terms of machine vs human classes). This metric is used in all
experiments if not stated otherwise."* And in appendix E: *"In Table 10,
performance results (Macro average F1-score) of all statistical and black-box
detectors per each test language are provided. [...] In Tables 11 – 15,
performance results (Macro average F1-score) of all fine-tuned detector models
per each test language are provided."*

The paper reports **no AUC ROC per language**. AUC ROC appears only in Table 3,
aggregated over all languages at once, so there is no second per-language metric
to record.

### Tables taken

| table | page in the ACL PDF | caption, verbatim |
|---|---|---|
| Table 10 | 19 | Table 10: Cross-lingual performance of zero-shot detection models. |
| Table 11 | 20 | Table 11: Cross-lingual performance of all detection models fine-tuned on the English language (evaluated per LLM). |
| Table 12 | 21 | Table 12: Cross-lingual performance of all detection models fine-tuned on the Spanish language (evaluated per LLM). |
| Table 13 | 22 | Table 13: Cross-lingual performance of all detection models fine-tuned on the Russian language (evaluated per LLM). |
| Table 14 | 23 | Table 14: Cross-lingual performance of all detection models fine-tuned on all three train languages (evaluated per LLM). |
| Table 15 | 24 | Table 15: Cross-lingual performance of all detection models fine-tuned on the English language with 3-times more train samples (evaluated per LLM). |

`y-multitude.tsv` holds Table 10 in full (9 detectors x 11 languages) plus the
three summary rows printed at the foot of each of Tables 11-15 (All Detectors
Mean, Multilingual Base Models Mean, Monolingual Base Models Mean), tagged with
the train language of that table: en, es, ru, all, en3.

`y-multitude-finetuned-by-llm.tsv` holds the body of Tables 11-15, that is every
(train LLM x base model) row. It is kept in a separate file because its row
identity carries an extra dimension, the generator LLM, that the Y axis of this
measurement does not have.

**Table 4 is not copied separately, because it is the same numbers.** Table 4
(page 7, *"Performance for the test languages based on various train language
combinations. It shows the mean of all trained detectors with multilingual base
models along with 95% confidence interval error bounds. The reported score is
macro average F1-score."*) reproduces exactly the Multilingual Base Models Mean
rows of Tables 11-15 and adds a 95% confidence interval to each. Checked cell by
cell for train=en (0.5448, 0.7335, 0.6793, 0.8104, 0.9292, ...) and train=en3
(0.5605, 0.7484, 0.7289, 0.8244, 0.9392, ...). Only the confidence intervals are
in Table 4 and not in this repository; they are on page 7 of the PDF if needed.

### Verification

Table 10 and the summary rows of Tables 11 and 15 were extracted from the arXiv
HTML rendering and then re-read out of the ACL Anthology PDF with a second tool.
Both renderings agree digit for digit.

---

## 2. Pangram 4: FPR and FNR per language

**Paper:** *Pangram 4* technical report.

| what | value |
|---|---|
| arXiv | https://arxiv.org/abs/2607.27183 |
| HTML used for extraction | https://arxiv.org/html/2607.27183v1 |
| PDF used for verification | https://arxiv.org/pdf/2607.27183 |
| Table | **Table 8**, page 19 of the PDF |

Caption, verbatim:

> Table 8: Multilingual false positive and false negative rates by language.

Surrounding text, verbatim, because it defines what the two columns are measured
on and they are not the same population:

> Table 8 reports the FPR and FNR for supported languages. FPRs are measured on
> pre-2022 per-language subsets of FineWeb2 (Penedo et al., 2025). While not
> reported, we test all 104 languages reported in FineWeb2, finding only 14
> false positives among 996,273 examples, for an overall multilingual FPR of
> 0.0014% with a 95% Wilson confidence interval of (0.0008%, 0.0024%). FNRs are
> measured across 18 supported languages using a test set of 190,149
> multilingual AI generations, which are synthetic mirrors of English data,
> including how-to articles, news articles, and reviews. Pangram 4's overall
> multilingual FNR is 1.24% with a 95% Wilson confidence interval of (1.19%,
> 1.29%). We hypothesize that higher false negative rates in languages such as
> Urdu (5.31%) and Persian (3.17%) may originate from differences in the base
> model's tokenization; however, the effects of tokenization on multilingual
> AI-text detection remain unknown.

Table 8 prints **23 language rows**, not 18. FPR is given for all 23. FNR is
given for 18 and is an em dash for Greek, Hungarian, Polish, Romanian and
Swedish. `CRITERIA.md` says 18 languages, and that count is the FNR count.

Values in the file are copied with their percent sign, as printed.

---

## 3. Resource proxy: share of the language in Common Crawl

Chosen in `CRITERIA.md` before counting: *"share of the language in CommonCrawl,
from the published CC language statistics."*

| what | value |
|---|---|
| Page | https://commoncrawl.github.io/cc-crawl-statistics/plots/languages |
| Underlying data | https://commoncrawl.github.io/cc-crawl-statistics/plots/languages.csv |
| Snapshot used | **CC-MAIN-2026-34**, the latest crawl listed on the page on the date of access |

Page text, verbatim:

> Distribution of Languages. The language of a document is identified by Compact
> Language Detector 2 (CLD2). It is able to identify 160 different languages and
> up to 3 languages per document. The table lists the percentage covered by the
> primary language of a document (returned first by CLD2). So far, only HTML
> pages are passed to the language detector. The underlying data including page
> counts is provided in languages.csv.

The page shows three crawls side by side, CC-MAIN-2026-25, CC-MAIN-2026-30 and
CC-MAIN-2026-34. **One snapshot is used, CC-MAIN-2026-34**, and it is named in
the `cc_snapshot` column of every row so no mixing is possible.

The crawl has 162 language rows including `<unknown>`. All 162 are in
`cc-languages-raw.tsv` with the CLD2 code untouched. `resource-cc.tsv` carries
only the 25 languages that appear in one of the two Y tables.

Every value in `resource-cc.tsv` was checked against the `%pages/crawl` column of
`languages.csv` for crawl CC-MAIN-2026-34. 25 of 25 match exactly, zero
mismatches. English there is 40.4526% of 865,530,140 pages.

The CLD2 codes are ISO 639-3 style, `ara`, `zho`, `fas` and so on. They are
macrolanguage labels, not FLORES-200 codes, so they are kept as they are in the
`orig_code` column and the FLORES-200 code is a separate column.

---

## How language codes were mapped

`lang_code` is FLORES-200. `orig_code` is what the source itself printed: a two
letter code in MULTITuDE, a full English language name in Pangram Table 8, a
CLD2 code in Common Crawl.

**Left blank on purpose, one language:** Chinese. Neither paper says which
script. MULTITuDE calls it *"Mandarin Chinese (Sino-Tibetan)"* and gives the
code `zh`; Pangram writes *"Chinese"*. FLORES-200 has both `zho_Hans` and
`zho_Hant` and picking one would be a guess, so the cell is empty in all three
files. Common Crawl has the same problem: CLD2 emits a single `zho`.

**Mapped, with the choice stated:**

- Arabic, `ar` / `Arabic` / `ara`, mapped to `arb_Arab`, Modern Standard Arabic.
  FLORES-200 also has `acm_Arab`, `ary_Arab`, `arz_Arab` and other varieties.
  MULTITuDE's Arabic comes from news text in MassiveSumm, so MSA is the reading;
  Pangram does not say.
- Persian, `Persian` / `fas`, mapped to `pes_Arab`, Western Persian. FLORES-200
  also has `prs_Arab`, Dari. The papers say only "Persian".

Everything else is one to one and carries no choice: Catalan, Czech, Dutch,
English, French, German, Greek, Hindi, Hungarian, Italian, Japanese, Korean,
Polish, Portuguese, Romanian, Russian, Spanish, Swedish, Turkish, Ukrainian,
Urdu, Vietnamese.
