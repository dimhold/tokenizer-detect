# Criteria and definitions for T1: token fertility against detector quality

**Written 2026-09-03, before a single number was counted** and committed
separately so the order is visible in git history.

Nothing in this file is rewritten after counting. Corrections are appended at
the end, with a date and a reason.

---

## Question

How much of a machine text detector's quality on a language is explained by how
finely the tokenizer cuts that language up, rather than by the language itself
or by the detector.

## Hypothesis, fixed in advance

Mostly by that. A detector measures how predictable the next token is. When a
word breaks into fragments and half of them are single letters, predicting the
next piece becomes a spelling task rather than a choice the author made. That
part of the signal is equally forced for a person and for a machine, so it
dilutes the part that separates them. The finer the cut, the stronger the
dilution.

## Two axes

**X, fertility.** Tokens per whitespace word, measured on the same content in
every language, so that what varies is the language and the tokenizer and not
the subject matter.

**Y, detector quality.** Taken from published tables, not from a detector we
run ourselves. Two independent sources, reported separately and never averaged
into one number:

| source | what it gives | languages |
|---|---|---|
| MULTITuDE, EMNLP 2023 (arXiv:2310.13606) | macro-F1 per language, several detectors | 11 |
| Pangram 4 (arXiv:2607.27183), table 8 | FNR and FPR per language | 18 |

Two sources exist because agreement between them is itself evidence and
disagreement is a result worth reporting. If the relation holds on one table
and not on the other, that is written down as it stands, not resolved by
picking the friendlier one.

## Corpus

FLORES-200 devtest: 1012 sentences, human translated, the same sentences in
every language. A parallel corpus is not a nicety here. Fertility measured on
web text collected separately for each language would confound the cut with
what people happen to write about in that language and the whole measurement
is about separating those.

Sentence count, character count and word count per language are recorded and
published, because "tokens per word" depends on what counts as a word and in
languages without whitespace boundaries it partly stops meaning anything.

## Which tokenizer

Fertility is a property of a tokenizer, not of a language, so there is no single
number and the report must not pretend there is. Measured over a fixed panel,
each reported separately:

| tokenizer | why it is in the panel |
|---|---|
| GPT-2 BPE | what the older detector literature actually scored with |
| cl100k_base | the vocabulary most current work inherits |
| o200k_base | the current one, larger vocabulary |
| XLM-RoBERTa SentencePiece | a deliberately multilingual vocabulary, the opposite end |

**The headline uses the tokenizer belonging to the detector's stated scoring
model where the paper states it and cl100k_base where it does not.** That rule
is fixed now so it cannot be chosen after seeing which panel member correlates
best.

## What is counted

For each language, on each tokenizer: tokens, whitespace words, characters,
tokens per word, tokens per character and the share of tokens that are a
single character. The last one is the mechanism the hypothesis actually names,
so it is measured directly rather than assumed to travel with fertility.

## The confounder, named before counting

**Resource level.** How much text of a language a model saw during training
drives fertility down and detector quality up at the same time. A raw
correlation between the two would therefore appear whether or not the
tokenization story is true and reporting one as evidence would be wrong.

Handling, fixed in advance:

1. A resource proxy is recorded per language, chosen before counting: share of
   the language in CommonCrawl, from the published CC language statistics.
2. The headline number is the **partial** Spearman correlation between fertility
   and detector quality, controlling for that proxy and never the raw one. Both
   are published.
3. If the partial correlation collapses while the raw one holds, the honest
   result is that this measures resource level and it is published as that.

## What refutes the hypothesis

Fixed now, so it cannot move afterwards.

- **Refuted** if the partial Spearman correlation is weaker than |0.4| on both Y
  sources.
- **Refuted** if the sign disagrees between the two Y sources.
- **Not refuted but not supported** if it holds on one source and not the other.
  That case gets published with both tables and no headline claim.

A refuted hypothesis is published. The measurement is cheap and the negative
result answers the same question.

## Counting rules

1. **Zero model calls.** Tokenizers run locally, detector numbers are read from
   published tables and cited to page or table number.
2. **Only languages present in both a Y table and FLORES-200** enter the
   correlation. The list is written down before the numbers are joined and
   languages dropped are listed with the reason.
3. **No language is dropped after seeing its residual.**
4. Word counting on whitespace is stated as a limitation for Chinese, Japanese
   and Thai. Those languages are reported separately from the headline
   correlation rather than silently included.
5. Every number in the report traces to a script in this directory and a line
   of output committed alongside it.

## Cost

Zero dollars, no model calls, one corpus download.

---

## Who has already done this

That section was written on 2026-09-02, before counting and rechecked on
2026-09-03. It lives in [PRIOR-WORK.md](PRIOR-WORK.md) in this repository,
together with the two corrections below that concern it.

---

## Corrections appended 2026-09-05 while the Y axis was being recorded

Nothing above is rewritten. Everything below was written down **before the axes
were joined and before a single correlation was computed**.

### 1. The question is named in Pangram 4 itself and declared open there

While copying table 8 it turned out that the authors state our hypothesis
themselves, immediately before that table and declare it untested. Verbatim
(checked in the HTML of the paper, `arxiv.org/html/2607.27183v1`):

> We hypothesize that higher false negative rates in languages such as Urdu
> (5.31%) and Persian (3.17%) may originate from differences in the base
> model's tokenization; however, the effects of tokenization on multilingual
> AI-text detection remain unknown.

This changes the wording, not the measurement. **Priority for posing the
question is theirs now and citing that sentence is mandatory.** What stays
ours is the same as before: they named the hypothesis and did not test it, we
test it. Claiming the question as ours is not allowed.

### 2. The neighbouring relation has been built 5 times already and came out weak

The novelty check of 2026-09-05 found what the check of 2026-09-02 had missed:
the link between fertility and downstream quality has been built in at least 5
ways and the result is closer to negative.

- Rust et al. 2021 ([arXiv:2012.15613](https://arxiv.org/abs/2012.15613)): no
  clear correlation across tasks and languages.
- Tokenizer Tax on Indian languages
  ([arXiv:2607.24276](https://arxiv.org/abs/2607.24276)): the visible
  correlation is "mostly explained by the resource availability of the
  language, not by tokenizer behaviour". **That is exactly our prerecorded
  confounder, confirmed by other hands** and it strengthens the requirement to
  compute the partial correlation instead of the raw one.
- Tokenizer Tax on Europe
  ([arXiv:2605.24718](https://arxiv.org/abs/2605.24718)): rho = -0.43 at
  p = 0.34 and n = 7, the authors conclude "at best a weak predictor".
- MorphScore v2 ([arXiv:2507.06378](https://arxiv.org/abs/2507.06378)):
  morphological alignment does not explain a large share of the variance.
- TokLens, ACL 2026 SRW: 24 tokenizers, 15 languages, 6 metrics against
  downstream quality.

**Publishing a strong wording of the hypothesis without naming those 5 results
is not allowed.** The substantive argument why detection might behave
differently still stands: a detector lives directly on the predictability of
the next token rather than on understanding. But that is an argument and not
data and it was written before counting.

### 3. Which detectors enter the correlation, fixed BEFORE the join

While copying table 10 of MULTITuDE it turned out that the statistical
detectors (Entropy, Rank, DetectGPT, Log-Rank, Log-likelihood, GLTR) produce
almost identical numbers across the 11 languages, differing in the third or
fourth digit. A rank correlation on those would be computed over noise.

The temptation to drop them after counting is obvious, so the rule is written
down now: **ALL detectors of table 10 and all aggregate rows of tables 11 to 15
enter the correlation, each as a separate result row. None is dropped, neither
before nor after counting.** The degeneracy of the statistical detectors is
shown by printing the spread of their values next to the correlation, not by
removing them from the table.

For Pangram: **the headline Y axis is FNR**, because FPR is degenerate, being
exactly 0.0000% for 15 languages out of 23. FPR is published next to it with a
note about the degeneracy. FNR and FPR are not combined into one indicator:
they are measured on different populations, FPR on slices of FineWeb2 from
before 2022, FNR on synthetic generations.

### 4. What is known about Belarusian

It is absent from all 9 checked benchmarks of machine text detection, including
the 79 language BLUFF
([arXiv:2603.00634](https://arxiv.org/abs/2603.00634)), which was assembled
specifically for the low resource tail. So **Belarusian does not enter this
correlation at all**: it has no point on the Y axis.

It stays in the measurement on the X axis only, as the rightmost fertility
point and that is how it has to be written, rather than passed off as a point
of the relation. The statement "Belarusian is absent from detection benchmarks"
is checkable and is a result in itself.
