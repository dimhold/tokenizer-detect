# -*- coding: utf-8 -*-
"""Extract the Y axis (published detector tables) and the resource proxy.

Zero model calls. Downloads three sources, copies numbers verbatim, writes TSV.
Sources, table numbers and page numbers: SOURCES.md in this directory.

    python extract-y.py       # downloads into ./_cache and rebuilds the TSVs

Outputs
    y-multitude.tsv                    Table 10 + the summary rows of Tables 11-15
    y-multitude-finetuned-by-llm.tsv   bodies of Tables 11-15, per train LLM
    y-pangram4.tsv                     Table 8
    resource-cc.tsv                    CommonCrawl share, 25 joined languages
    cc-languages-raw.tsv               CommonCrawl share, all 162 CLD2 labels
"""
import io
import os
import re
import sys
import html
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_cache")
OUT = HERE

SRC = {
    "multitude.html": "https://arxiv.org/html/2310.13606v1",
    "pangram.html": "https://arxiv.org/html/2607.27183v1",
    "cclang.html": "https://commoncrawl.github.io/cc-crawl-statistics/plots/languages",
    "languages.csv": "https://commoncrawl.github.io/cc-crawl-statistics/plots/languages.csv",
}
CC_SNAPSHOT = "CC-MAIN-2026-34"
CC_URL = SRC["cclang.html"]


def fetch():
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    for name, url in SRC.items():
        path = os.path.join(CACHE, name)
        if os.path.exists(path):
            continue
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=120).read()
        if not data:
            sys.exit("empty response for " + url)
        open(path, "wb").write(data)


def cell_text(chunk):
    text = re.sub(r'<math[^>]*alttext="([^"]*)"[^>]*>.*?</math>', r"\1", chunk, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def html_tables(name):
    src = open(os.path.join(CACHE, name), encoding="utf-8", errors="replace").read()
    found = []
    for fig in re.finditer(r"<figure[^>]*>(.*?)</figure>", src, re.S):
        block = fig.group(1)
        cap = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", block, re.S)
        cap = cell_text(cap.group(1)) if cap else ""
        if not cap.lower().startswith("table"):
            continue
        rows = []
        for tr in re.finditer(r"<tr[^>]*>(.*?)</tr>", block, re.S):
            rows.append([cell_text(c) for c in
                         re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr.group(1), re.S)])
        found.append((cap, rows))
    return found


def table(name, label):
    for cap, rows in html_tables(name):
        if cap.split(":")[0] == label:
            return cap, rows
    sys.exit("table not found: %s in %s" % (label, name))


def write(path, lines):
    with io.open(os.path.join(OUT, path), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("%-38s %d rows" % (path, len(lines) - 1))


# --- language mapping -------------------------------------------------------
# FLORES-200 code, English name, CommonCrawl CLD2 code.
# An empty FLORES code means the source does not say which variety it is and
# guessing would be inventing. See SOURCES.md, "How language codes were mapped".
MAP = {
    "ar": ("arb_Arab", "Arabic", "ara"),
    "ca": ("cat_Latn", "Catalan", "cat"),
    "cs": ("ces_Latn", "Czech", "ces"),
    "de": ("deu_Latn", "German", "deu"),
    "en": ("eng_Latn", "English", "eng"),
    "es": ("spa_Latn", "Spanish", "spa"),
    "nl": ("nld_Latn", "Dutch", "nld"),
    "pt": ("por_Latn", "Portuguese", "por"),
    "ru": ("rus_Cyrl", "Russian", "rus"),
    "uk": ("ukr_Cyrl", "Ukrainian", "ukr"),
    "zh": ("", "Chinese", "zho"),
    "fr": ("fra_Latn", "French", "fra"),
    "el": ("ell_Grek", "Greek", "ell"),
    "hi": ("hin_Deva", "Hindi", "hin"),
    "hu": ("hun_Latn", "Hungarian", "hun"),
    "it": ("ita_Latn", "Italian", "ita"),
    "ja": ("jpn_Jpan", "Japanese", "jpn"),
    "ko": ("kor_Hang", "Korean", "kor"),
    "fa": ("pes_Arab", "Persian", "fas"),
    "pl": ("pol_Latn", "Polish", "pol"),
    "ro": ("ron_Latn", "Romanian", "ron"),
    "sv": ("swe_Latn", "Swedish", "swe"),
    "tr": ("tur_Latn", "Turkish", "tur"),
    "ur": ("urd_Arab", "Urdu", "urd"),
    "vi": ("vie_Latn", "Vietnamese", "vie"),
}
BY_NAME = dict((v[1], k) for k, v in MAP.items())

Y_HEADER = "detector\torig_code\tlang_code\tlang_name\tmetric\tvalue\tsource_table"
TRAIN = [("Table 11", "en"), ("Table 12", "es"), ("Table 13", "ru"),
         ("Table 14", "all"), ("Table 15", "en3")]


def build_multitude():
    main, by_llm = [], []

    _, rows = table("multitude.html", "Table 10")
    langs = rows[0][1:]
    assert langs == ["ar", "ca", "cs", "de", "en", "es", "nl", "pt", "ru", "uk", "zh"], langs
    for row in rows[1:]:
        det, vals = row[0], row[1:]
        assert len(vals) == 11, row
        for code, val in zip(langs, vals):
            flores, name, _ = MAP[code]
            main.append("\t".join([det, code, flores, name, "macro_f1", val,
                                   "MULTITuDE Table 10"]))

    for label, train_lang in TRAIN:
        _, rows = table("multitude.html", label)
        assert rows[1][2:] == langs, rows[1]
        llm = None
        for row in rows[2:]:
            if len(row) == 13:
                llm, base, vals = row[0], row[1], row[2:]
            elif len(row) == 12:
                base, vals = row[0], row[1:]
            else:
                continue
            assert len(vals) == 11, row
            if base.endswith("Mean"):
                det = "%s [fine-tuned, train_lang=%s]" % (base, train_lang)
                sink = main
            else:
                det = "%s [fine-tuned, train_lang=%s, train_llm=%s]" % (base, train_lang, llm)
                sink = by_llm
            for code, val in zip(langs, vals):
                flores, name, _ = MAP[code]
                sink.append("\t".join([det, code, flores, name, "macro_f1", val,
                                       "MULTITuDE " + label]))

    write("y-multitude.tsv", [Y_HEADER] + main)
    write("y-multitude-finetuned-by-llm.tsv", [Y_HEADER] + by_llm)


def build_pangram():
    _, rows = table("pangram.html", "Table 8")
    lines = ["lang_code\torig_code\tlang_name\tfnr\tfpr\tsource_table"]
    for row in rows[1:]:
        for i in (0, 3):
            if len(row) <= i + 2:
                continue
            name, fpr, fnr = row[i].strip(), row[i + 1].strip(), row[i + 2].strip()
            if not name:
                continue
            flores, canon, _ = MAP[BY_NAME[name]]
            lines.append("\t".join([flores, name, canon, fnr, fpr, "Pangram 4 Table 8"]))
    write("y-pangram4.tsv", lines)


def build_commoncrawl():
    src = open(os.path.join(CACHE, "cclang.html"), encoding="utf-8", errors="replace").read()
    rows = []
    for tr in re.finditer(r"<tr[^>]*>(.*?)</tr>", src, re.S):
        cells = [cell_text(c) for c in
                 re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr.group(1), re.S)]
        if cells:
            rows.append(cells)
    col = rows[0].index(CC_SNAPSHOT)
    width = len(rows[0])
    share = dict((r[0], r[col]) for r in rows[2:] if len(r) == width)

    raw = ["cc_language_code\tcc_share_percent\tcc_snapshot"]
    for r in rows[2:]:
        if len(r) == width:
            raw.append("\t".join([r[0], r[col], CC_SNAPSHOT]))
    write("cc-languages-raw.tsv", raw)

    lines = ["lang_code\torig_code\tlang_name\tcc_share_percent\tcc_snapshot\tsource_url"]
    seen = set()
    for key in sorted(MAP, key=lambda k: MAP[k][1]):
        flores, name, cc = MAP[key]
        if name in seen:
            continue
        seen.add(name)
        lines.append("\t".join([flores, cc, name, share[cc], CC_SNAPSHOT, CC_URL]))
    write("resource-cc.tsv", lines)


def verify_commoncrawl():
    """Every CC share must equal the %pages/crawl column of languages.csv."""
    import csv
    path = os.path.join(CACHE, "languages.csv")
    ref = {}
    with io.open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["crawl"] == CC_SNAPSHOT:
                ref[row["primary_language"]] = row["%pages/crawl"]
    bad = 0
    with io.open(os.path.join(OUT, "resource-cc.tsv"), encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if ref.get(f[1]) != f[3]:
                bad += 1
                print("MISMATCH", f[1], f[3], ref.get(f[1]))
    print("commoncrawl cross-check against languages.csv: %d mismatches" % bad)
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    fetch()
    build_multitude()
    build_pangram()
    build_commoncrawl()
    verify_commoncrawl()
