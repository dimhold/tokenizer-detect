# Prior work

Written on 2026-09-02 and rechecked on 2026-09-03, **before a single number was
counted** and extended on 2026-09-05 while the Y axis was being recorded and
still before the axes were joined. The search went through arXiv, the ACL
Anthology and HuggingFace. None of what was found is the measurement we set out
to make.

## Who has already done this

- **arXiv:2604.25860 (Luminol-AIDetect)** explains detector failures on Czech
  and Arabic by the fragmentation of byte level BPE and reports Binoculars with
  FNR 1.000 on both. That is an explanation and 2 points, not a relation.
- **MULTITuDE, EMNLP 2023 (arXiv:2310.13606)** gives macro-F1 over 11
  languages, GPTZero ranging from 0.5626 on English to 0.1042 on Russian.
  Fertility is not computed there.
- **M4GT-Bench (arXiv:2402.11175)** and **CEAID (arXiv:2509.26051)** add more
  points across languages, again without tokenization.
- **Pangram 4 (arXiv:2607.27183), table 8** gives FNR and FPR over 18
  languages. It is the second Y axis and it has no X axis of its own.
- **Work on fertility as such** ties it to inference cost and to translation
  quality, not to detection.

**What stays ours: the join.** Both halves are published separately, no plot of
"fertility against detector quality" exists and **not one of those works
controls for the resource level of the language**. Without that control the
relation proves nothing even once it is drawn. The control is what we add on
top of joining 2 ready tables.

**What this measurement does not contain and does not answer:** it does not
improve detectors, it does not propose a tokenizer and it says nothing about
how a detector behaves on a language that is absent from both tables.

---

## Correction 1, 2026-09-05: the question is named in Pangram 4 itself and declared open there

While copying table 8 it turned out that the authors state our hypothesis
themselves, immediately before that table and declare it untested. Verbatim
(checked in the HTML of the paper, `arxiv.org/html/2607.27183v1`, that is
[arXiv:2607.27183](https://arxiv.org/abs/2607.27183)):

> We hypothesize that higher false negative rates in languages such as Urdu
> (5.31%) and Persian (3.17%) may originate from differences in the base
> model's tokenization; however, the effects of tokenization on multilingual
> AI-text detection remain unknown.

This changes the wording, not the measurement. **Priority for posing the
question is theirs and citing that sentence is mandatory.** What stays ours is
the same as before: they named the hypothesis and did not test it, we test it.
Claiming the question as ours is not allowed.

## Correction 2, 2026-09-05: the neighbouring relation has been built 5 times already and came out weak

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
