# tokenizer-detect

**Does the fertility of a tokenizer explain how well a machine text detector
works on a language?**

No. The hypothesis is refuted by a condition that was written down before the
first number was counted. The reason is sharper than a weak correlation: the
sign of the correlation is set by the language the detector was trained on.
Fertility only stands in for the distance between that language and the
language under test.

## The decisive evidence

MULTITuDE publishes the same detectors fine-tuned on different languages and
evaluated on the same 10 languages. Fertility of those languages does not
change between the 2 columns. The ordering does.

| fine-tuned on English | F1 | fertility | | fine-tuned on Russian | F1 | fertility |
|---|---:|---:|---|---|---:|---:|
| English | 0.945 | 1.24 | | Russian | 0.800 | 3.41 |
| Dutch | 0.563 | 1.90 | | Ukrainian | 0.745 | 4.20 |
| Spanish | 0.530 | 1.61 | | Arabic | 0.600 | 4.19 |
| Catalan | 0.518 | 1.90 | | Spanish | 0.392 | 1.61 |
| Portuguese | 0.482 | 1.72 | | Czech | 0.384 | 2.98 |
| Czech | 0.473 | 2.98 | | Portuguese | 0.369 | 1.72 |
| Ukrainian | 0.461 | 4.20 | | German | 0.368 | 1.98 |
| German | 0.454 | 1.98 | | Dutch | 0.367 | 1.90 |
| Arabic | 0.444 | 4.19 | | Catalan | 0.360 | 1.90 |
| Russian | 0.441 | 3.41 | | **English** | **0.351** | **1.24** |

**Under the detector fine-tuned on Russian, English stands last out of 10 while
having the lowest fertility of all 10.** Under the detector fine-tuned on
English, the same English stands first, at the same fertility of 1.24. If
fertility drove detector quality, English would be first in both columns.

The partial rank correlation between fertility and quality follows the same
flip, on the same 10 languages and the same tokenizer cl100k_base:

| MULTITuDE detectors, fine-tuned on | partial rho with fertility |
|---|---:|
| English | -0.884 |
| English, 3 times more training samples | -0.959 |
| all languages | -0.921 |
| Spanish | -0.567 |
| **Russian** | **+0.747** |

The refutation condition, fixed in [CRITERIA.md](CRITERIA.md) in advance, was
"Refuted if the sign disagrees between the two Y sources". It disagreed:
MULTITuDE with English training gives partial rho -0.713 at n = 10 and p =
0.029, Pangram 4 FNR gives +0.112 at n = 16 and p = 0.696.

## How it was measured

Zero model calls, zero dollars, one corpus download.

**X axis, fertility.** Tokens per whitespace word on FLORES-200 devtest, 1012
human translated sentences that are the same in every language, over 204
languages and 4 tokenizers (cl100k_base, o200k_base, gpt2, xlm-roberta-base).
Counted here, in `fertility.py`.

**Y axis, detector quality.** Copied verbatim from published tables, never
computed by us: MULTITuDE (EMNLP 2023, [arXiv:2310.13606](https://arxiv.org/abs/2310.13606))
macro-F1 per language and Pangram 4
([arXiv:2607.27183](https://arxiv.org/abs/2607.27183)) table 8, FNR and FPR per
language. Table and page numbers are in [SOURCES.md](SOURCES.md).

**The confounder, named before counting.** Resource level of a language pushes
fertility down and detector quality up at the same time, so the headline number
is the partial Spearman correlation controlling for the share of the language
in CommonCrawl (snapshot CC-MAIN-2026-34). The raw correlation is published
next to it. That control did not remove the relation. The control that removed
it was the training language of the detector and that one was not foreseen.

## What else is in the numbers

- **The statistical detectors are noise.** Entropy, Rank and DetectGPT give
  partial rho -0.776 while their macro-F1 spread across all 10 languages is
  0.0018, that is between 0.470 and 0.472. They are kept in the tables with
  their spread printed next to them, by a rule written before counting.
- **GPTZero, the only commercial detector among them, gives rho -0.062.**
  Its quality spread is the largest of the group at 0.4653.
- **The answer depends on the tokenizer.** On Pangram 4 FNR the partial
  correlation is +0.112 with cl100k_base, +0.509 with o200k_base, +0.107 with
  gpt2 and +0.519 with xlm-roberta-base. All 4 are positive, which is the
  opposite of the hypothesis.
- **Belarusian has no point on the Y axis at all.** It is absent from all 9
  detection benchmarks that were checked, including the 79 language BLUFF built
  for the low resource tail. It stays on the X axis only.

The full report is [RESULTS.md](RESULTS.md). The question was posed by the
Pangram 4 authors themselves, who call it open. They and the 5 neighbouring
works on fertility against downstream quality are listed in
[PRIOR-WORK.md](PRIOR-WORK.md).

## Files

| file | what it is |
|---|---|
| `CRITERIA.md` | criteria, hypothesis, confounder and refutation conditions, written before counting |
| `RESULTS.md` | the full report of the result |
| `PRIOR-WORK.md` | who did what before and what stays ours |
| `SOURCES.md` | every source table, with page and table numbers and how language codes were mapped |
| `fertility.py` | the X axis: tokens per word over FLORES-200 devtest |
| `extract-y.py` | the Y axis and the resource proxy, rebuilt from the sources |
| `join.py` | the join, Spearman, partial correlation and the significance level |
| `fertility.tsv` | 816 rows, 204 languages x 4 tokenizers |
| `y-multitude.tsv` | MULTITuDE table 10 plus the summary rows of tables 11 to 15 |
| `y-multitude-finetuned-by-llm.tsv` | bodies of MULTITuDE tables 11 to 15, per generator LLM |
| `y-pangram4.tsv` | Pangram 4 table 8, 23 language rows |
| `resource-cc.tsv` | CommonCrawl share for the 25 joined languages |
| `cc-languages-raw.tsv` | CommonCrawl share for all 162 CLD2 labels, untouched |
| `join-results.json` | 104 result rows, 4 tokenizers x 26 Y axis series |
| `join-output.txt` | the console output of the last run |

## Reproduction

`join.py` needs nothing but Python 3 and the TSV files in this repository:

```
python join.py
```

Rebuilding the axes from scratch needs the FLORES-200 devtest directory and
network access:

```
python fertility.py <path to flores200_dataset/devtest> fertility.tsv
python extract-y.py
```

`extract-y.py` downloads the 2 papers and the CommonCrawl statistics into
`_cache/`, copies the numbers out of the tables and cross checks every
CommonCrawl value against `languages.csv`. It prints the number of mismatches
and exits nonzero if there is any.

## Citation

MIT license, see [LICENSE](LICENSE). Citation metadata is in
[CITATION.cff](CITATION.cff).
