# -*- coding: utf-8 -*-
u"""Joining the two axes, and the headline number of measurement T1.

The X axis (`fertility.tsv`) is counted by us on FLORES-200. The Y axis
(`y-pangram4.tsv`, `y-multitude.tsv`) is copied from published tables. The
resource proxy (`resource-cc.tsv`) comes from the CommonCrawl statistics.

The headline number, fixed in CRITERIA before counting, is the **partial**
Spearman rank correlation between fertility and detector quality, controlling
for the resource proxy. The raw one is published next to it but never becomes
the headline.

No detector is dropped: the rule is written in correction 3 to the criteria.
Chinese is excluded from the headline correlation by rule 4 of the criteria (no
whitespace between words), and that was written down before counting.

scipy is not installed on this machine, so ranks, correlation and significance
are computed here: Spearman is Pearson on ranks, first order partial
correlation is the usual formula, significance is the Fisher transform.

Run:  python join.py
"""
import io
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CJK = ('zho_Hans', 'zho_Hant', 'jpn_Jpan', 'tha_Thai', '')   # rule 4 of the criteria
HEADLINE_TOKENIZER = 'cl100k_base'


def read_tsv(name):
    path = os.path.join(HERE, name)
    rows = []
    with io.open(path, encoding='utf-8') as f:
        head = f.readline().rstrip('\n').split('\t')
        for line in f:
            if not line.strip():
                continue
            rows.append(dict(zip(head, line.rstrip('\n').split('\t'))))
    return rows


def num(s):
    if s is None:
        return None
    s = s.strip().replace('%', '')
    if s in ('', '-', '--', 'n/a', 'N/A'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def ranks(xs):
    u"""Ranks, averaged over ties."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def pearson(a, b):
    n = len(a)
    if n < 3:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((x - mb) ** 2 for x in b)
    if va == 0 or vb == 0:
        return None
    cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    return cov / math.sqrt(va * vb)


def spearman(a, b):
    return pearson(ranks(a), ranks(b))


def partial(rxy, rxz, ryz):
    u"""First order partial correlation: x against y, controlling for z."""
    if None in (rxy, rxz, ryz):
        return None
    d = (1 - rxz ** 2) * (1 - ryz ** 2)
    if d <= 0:
        return None
    return (rxy - rxz * ryz) / math.sqrt(d)


def pvalue(r, n, controls=0):
    u"""Two sided significance level through the Fisher transform."""
    if r is None or n - 3 - controls <= 0 or abs(r) >= 1:
        return None
    z = 0.5 * math.log((1 + r) / (1 - r)) * math.sqrt(n - 3 - controls)
    return 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))


def fert_map(tokenizer, field='tokens_per_word'):
    out = {}
    for r in read_tsv('fertility.tsv'):
        if r['tokenizer'] == tokenizer:
            v = num(r.get(field))
            if v is not None:
                out[r['lang']] = v
    return out


def cc_map():
    return dict((r['lang_code'], num(r['cc_share_percent']))
                for r in read_tsv('resource-cc.tsv')
                if r['lang_code'] and num(r['cc_share_percent']) is not None)


def series():
    u"""Every Y axis series, each one a separate result row.

    The sign is brought to "higher means a better detector": FNR is the share
    of machine texts that were missed, so it is taken negated, to point the
    same way as macro-F1. That transform is monotone and merely mirrors the
    rank correlation.
    """
    out = []
    pg = read_tsv('y-pangram4.tsv')
    out.append(('Pangram 4', 'FNR (negated)', dict(
        (r['lang_code'], -num(r['fnr'])) for r in pg
        if r['lang_code'] and num(r['fnr']) is not None)))
    out.append(('Pangram 4', 'FPR (negated)', dict(
        (r['lang_code'], -num(r['fpr'])) for r in pg
        if r['lang_code'] and num(r['fpr']) is not None)))
    mt = read_tsv('y-multitude.tsv')
    for det in sorted(set(r['detector'] for r in mt)):
        d = dict((r['lang_code'], num(r['value'])) for r in mt
                 if r['detector'] == det and r['lang_code']
                 and num(r['value']) is not None)
        if len(d) >= 4:
            out.append(('MULTITuDE', det, d))
    return out


def main():
    cc = cc_map()
    rows = []
    for tok in ('cl100k_base', 'o200k_base', 'gpt2', 'xlm-roberta-base'):
        fert = fert_map(tok)
        singles = fert_map(tok, 'single_char_token_share')
        for source, name, ys in series():
            langs = sorted(set(ys) & set(fert) & set(cc) - set(CJK))
            if len(langs) < 4:
                continue
            y = [ys[l] for l in langs]
            x = [fert[l] for l in langs]
            z = [cc[l] for l in langs]
            s = [singles[l] for l in langs]
            rxy, rxz, ryz = spearman(x, y), spearman(x, z), spearman(y, z)
            pr = partial(rxy, rxz, ryz)
            rsy = spearman(s, y)
            rsz = spearman(s, z)
            prs = partial(rsy, rsz, ryz)
            rows.append({
                'tokenizer': tok, 'source': source, 'detector': name,
                'n': len(langs), 'langs': langs,
                'spread_y': round(max(y) - min(y), 4),
                'rho_raw': rxy, 'rho_partial': pr,
                'p_raw': pvalue(rxy, len(langs)),
                'p_partial': pvalue(pr, len(langs), controls=1),
                'rho_singlechar_raw': rsy, 'rho_singlechar_partial': prs,
            })

    def fmt(v):
        return u'%6.3f' % v if v is not None else u'     -'

    for tok in ('cl100k_base', 'o200k_base', 'gpt2', 'xlm-roberta-base'):
        sub = [r for r in rows if r['tokenizer'] == tok]
        if not sub:
            continue
        mark = u'  <- headline' if tok == HEADLINE_TOKENIZER else u''
        print(u'\n=== tokenizer %s%s ===' % (tok, mark))
        print(u'%-70s %3s %8s %8s %8s %9s %9s' % (
            u'Y axis', u'n', u'spread', u'raw', u'partial', u'p raw',
            u'p part'))
        for r in sorted(sub, key=lambda r: (r['source'], r['detector'])):
            print(u'%-70s %3d %8.4f %8s %8s %9s %9s' % (
                (r['source'] + u' / ' + r['detector'])[:70], r['n'],
                r['spread_y'], fmt(r['rho_raw']), fmt(r['rho_partial']),
                (u'%8.3f' % r['p_raw']) if r['p_raw'] is not None else u'       -',
                (u'%8.3f' % r['p_partial']) if r['p_partial'] is not None else u'       -'))

    io.open(os.path.join(HERE, 'join-results.json'), 'w', encoding='utf-8').write(
        json.dumps(rows, ensure_ascii=False, indent=1))
    print(u'\nresult rows: %d, written to join-results.json' % len(rows))
    by_language()


def by_language():
    u"""The evidence that made the measurement worth finishing: the same set of
    languages under a detector fine-tuned on English and under the same
    detector fine-tuned on Russian. If fertility drove quality, the order would
    be the same in both."""
    fert = fert_map(HEADLINE_TOKENIZER)
    mt = read_tsv('y-multitude.tsv')
    print(u'\n=== language order follows the training language, not fertility ===')
    for tl in ('en', 'ru'):
        name = ('Monolingual Base Models Mean [fine-tuned, train_lang=%s]' % tl)
        d = [(r['lang_name'], r['lang_code'], num(r['value'])) for r in mt
             if r['detector'] == name and r['lang_code'] and num(r['value'])]
        d.sort(key=lambda t: -t[2])
        print(u'-- detector fine-tuned on %s' % tl)
        for n, c, v in d:
            print(u'   %-12s F1 %.4f   fertility %.2f' % (n, v, fert.get(c, 0.0)))


if __name__ == '__main__':
    main()
