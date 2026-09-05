"""
X axis for T1: tokens per word per language, on the same sentences in every
language (FLORES-200 devtest, 1012 human-translated sentences).

Writes one row per (language, tokenizer) to fertility.tsv. No model calls.
Usage: python fertility.py <path to flores200_dataset/devtest> <out.tsv>
"""
import os, sys, json, unicodedata

devtest, out_path = sys.argv[1], sys.argv[2]

import tiktoken
encoders = {
    "cl100k_base": tiktoken.get_encoding("cl100k_base"),
    "o200k_base": tiktoken.get_encoding("o200k_base"),
}

# GPT-2 and XLM-R come from the tokenizers library if their vocabularies are
# reachable; their absence is recorded rather than silently skipped.
extra = {}
try:
    from tokenizers import Tokenizer
    for name, repo in (("gpt2", "gpt2"), ("xlm-roberta-base", "xlm-roberta-base")):
        try:
            extra[name] = Tokenizer.from_pretrained(repo)
        except Exception as e:
            print(f"skip {name}: {e}", file=sys.stderr)
except ImportError as e:
    print(f"skip tokenizers lib: {e}", file=sys.stderr)

def count_words(text):
    return len(text.split())

def count_chars(text):
    # Codepoints excluding whitespace, so scripts are compared on content and
    # not on how many spaces the language happens to use.
    return sum(1 for ch in text if not ch.isspace())

rows = []
files = sorted(f for f in os.listdir(devtest) if f.endswith(".devtest"))
for i, fn in enumerate(files):
    lang = fn[: -len(".devtest")]
    with open(os.path.join(devtest, fn), encoding="utf-8") as fh:
        lines = [l.rstrip("\n") for l in fh if l.strip()]
    text = "\n".join(lines)
    words, chars, sents = count_words(text), count_chars(text), len(lines)

    for tname, enc in encoders.items():
        ids = enc.encode(text, disallowed_special=())
        singles = sum(1 for t in ids if len(enc.decode([t]).strip()) == 1)
        rows.append(dict(lang=lang, tokenizer=tname, sentences=sents, words=words,
                         chars=chars, tokens=len(ids),
                         tokens_per_word=len(ids) / words if words else None,
                         tokens_per_char=len(ids) / chars if chars else None,
                         single_char_token_share=singles / len(ids) if ids else None))
    for tname, tok in extra.items():
        ids = tok.encode(text, add_special_tokens=False).ids
        singles = sum(1 for t in ids if len(tok.decode([t]).strip()) == 1)
        rows.append(dict(lang=lang, tokenizer=tname, sentences=sents, words=words,
                         chars=chars, tokens=len(ids),
                         tokens_per_word=len(ids) / words if words else None,
                         tokens_per_char=len(ids) / chars if chars else None,
                         single_char_token_share=singles / len(ids) if ids else None))
    if i % 25 == 0:
        print(f"{i}/{len(files)} {lang}", file=sys.stderr, flush=True)

cols = ["lang", "tokenizer", "sentences", "words", "chars", "tokens",
        "tokens_per_word", "tokens_per_char", "single_char_token_share"]
with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\t".join(cols) + "\n")
    for r in rows:
        fh.write("\t".join(
            f"{r[c]:.6f}" if isinstance(r[c], float) else str(r[c]) for c in cols) + "\n")

print(f"wrote {len(rows)} rows over {len(files)} languages, "
      f"tokenizers: {sorted(list(encoders) + list(extra))}")
