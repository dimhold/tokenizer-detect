# Results: T1, tokenizer fertility against detector quality, 2026-09-05

The measurement is closed. **The hypothesis is refuted by the condition written
in [CRITERIA.md](CRITERIA.md) before the first number.** What refutes it is not
weakness of the relation. The relation is there and it is about something other
than tokenization.

Zero model calls. The X axis was counted by us on FLORES-200 devtest (204
languages x 4 tokenizers, `fertility.py`), the Y axis was copied verbatim from
published tables (`SOURCES.md`), the resource proxy is the share of the
language in CC-MAIN-2026-34.

## What exactly is refuted

The expectation was: the finer a tokenizer cuts a language up, the worse a
detector catches it, because predicting the next fragment becomes a spelling
task rather than a choice the author made.

The refutation condition, written in advance: **"Refuted if the sign disagrees
between the two Y sources."** The sign disagreed.

| Y axis, tokenizer cl100k_base | n | raw rho | partial rho | p |
|---|---:|---:|---:|---:|
| MULTITuDE, all detectors, fine-tuned on English | 10 | -0.782 | **-0.713** | 0.029 |
| Pangram 4, FNR | 16 | -0.265 | **+0.112** | 0.696 |

On the older set the relation is strong and points the predicted way. On the
current production detector there is no relation at all and the partial
correlation even flips the sign. And that is still not the main point.

## The main point: the sign is set by the training language of the detector

Inside one source, on the same 10 languages, at the same fertility, the sign of
the correlation flips depending on which language the detector was fine-tuned
on.

| MULTITuDE detectors, fine-tuned on | partial rho with fertility |
|---|---:|
| English | -0.884 |
| English, 3 times more training samples | -0.959 |
| all languages | -0.921 |
| Spanish | -0.567 |
| **Russian** | **+0.747** |

The same repeats in all 3 detector groups: `All Detectors Mean` gives -0.713 on
English training and **+0.922** on Russian, `Multilingual Base Models Mean`
gives -0.582 and **+0.939**.

Fertility cannot hurt and help at the same time. So it does not act at all. It
merely **stands in for another quantity: the distance between the language the
detector was trained on and the language it is tested on.**

The evidence that closes the question is the full ordering of the languages:

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

**Under the detector fine-tuned on Russian, English stands last while having
the finest cut of all 10.** If fertility drove quality, English would be first
in both columns. It is first in the left one and last in the right one and its
fertility is the same 1.24 in both cases.

The left column looks like a confirmation of the hypothesis for exactly one
reason: for a detector trained on English, "far from English" and "cut finely"
are almost the same ordering. Change the training language and the coincidence
falls apart.

## Another reason not to trust the strong numbers

The spread of values across languages shows which series are usable as a Y axis
at all.

| Y axis | spread over 10 languages | partial rho |
|---|---:|---:|
| Entropy, Rank, DetectGPT | 0.0018 | -0.776 |
| Log-Rank | 0.0022 | -0.764 |
| Log-likelihood | 0.0021 | -0.764 |
| GLTR Test-2 (Rank) | 0.0481 | -0.938 |
| ZeroGPT | 0.2924 | -0.842 |
| GPTZero | 0.4653 | -0.062 |

The statistical detectors give rho around -0.8 while their quality varies **in
the third digit**: their macro-F1 lies between 0.470 and 0.472 across all
languages. A rank correlation there is computed over noise and looks
impressive. By the rule written in correction 3 to the criteria they are not
dropped but shown together with their spread, so that it is visible what a
"strong relation" is made of.

And GPTZero, which has the largest quality spread (0.465) and is the only one
of those 5 that is an actual commercial detector, gives rho = -0.062. That is
**no relation at all**.

## Sensitivity to the tokenizer

The answer also depends on which tokenizer fertility is measured with, which by
itself makes the quantity unfit for a strong claim.

| Pangram 4, FNR | raw rho | partial rho |
|---|---:|---:|
| cl100k_base | -0.265 | +0.112 |
| o200k_base | +0.324 | +0.509 |
| gpt2 | -0.159 | +0.107 |
| xlm-roberta-base | +0.503 | +0.519 |

On all 4 the partial correlation is **positive**: the finer the cut, the lower
the share of misses, that is the better the detector. This is the opposite of
the hypothesis and on 2 tokenizers out of 4 it reaches significance.

## What follows from this

1. **The plot "fertility against detector quality" can be drawn and it
   deceives.** It comes out strong and pretty on data where the detector was
   trained on English and it falls apart when the training language changes.
   This is exactly the case the control in the criteria was written for:
   controlling for the resource level of the language did not remove the
   relation and what did remove it was a control we had not foreseen, the
   training language of the detector.
2. **The 5 neighbouring works that found a weak link between fertility and
   downstream quality get an explanation.** The explanation is that the
   quantity stands in for language distance and that its sign depends on the
   setup, rather than that the link is simply weak.
3. **The hypothesis from Pangram 4 itself stays open, but it cannot be tested
   this way.** The authors write that the high FNR of Urdu and Persian "may
   originate from differences in the base model's tokenization; however, the
   effects of tokenization on multilingual AI-text detection remain unknown".
   On published tables this is unresolvable: training language and fertility
   are entangled there and do not separate. Separating them takes a measurement
   where **the language is one and the fertility differs**. Such a measurement
   exists, see below.

## Belarusian is not in this picture

It is in none of the Y axis tables: MULTITuDE, M4GT-Bench, CEAID, MultiSocial,
Luminol-AIDetect, Pangram 4, IndicDetect, MultiGhostBench and the 79 language
BLUFF, which was assembled specifically for the low resource tail, were all
checked. Belarusian therefore does not enter the correlation at all.

On the X axis it is present and remains the rightmost point of the Slavic
group. By the independent data of Petrov et al. 2023 (all of FLORES-200 x 27
tokenizers), cl100k_base, share relative to English: Polish 1.91, Czech 2.11,
Russian 2.49, Serbian 2.92, Ukrainian 3.00, **Belarusian 3.55**.

## What this measurement opens next

Fertility and language distance can be separated in one way only: take **one
language in 2 orthographies**. Narkamaŭka and Taraškievica have the same
language distance to any training language and different fertility. The corpora
for that are already found: FLORES-200 `bel_Cyrl` is Narkamaŭka and
`BibleNLP/ebible` gives `bel-bel` and `bel-beln` in Taraškievica. What does not
exist ready made is the same text in both orthographies and that part is our
own work.

## Reproduction

```
python fertility.py <path to flores200_dataset/devtest> fertility.tsv
                       # X axis, 204 languages x 4 tokenizers
python extract-y.py    # Y axis and the resource proxy, from the sources
python join.py         # the join and the correlations
```

The full output of the last run is in `join-output.txt`, the parsed rows are in
`join-results.json` (104 rows: 4 tokenizers x 26 Y axis series).
