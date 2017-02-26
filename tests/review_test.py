#!/usr/bin/env python
# -*- coding: utf-8 -*-

from docutils.utils import column_width
from sphinx.writers.text import MAXWIDTH

from sphinx_testing import with_app


@with_app(buildername='review', srcdir='tests/root', copy_srcdir_to_tmpdir=True)
def test_basic(app, status, warnings):
    app.build()

#    import pdb; pdb.set_trace()

    re = (app.outdir / 'basic.re').read_text()

    expected = [
        '= section 1',
        '== section 2',
        '=== section 3',
        '=== section 4.0',
        '==== section 5',
        '=== section 4.1',
    ]
    for e in expected:
        assert e in re

    expected = [
        '@<i>{強調}',
        '@<b>{強い強調}',
        '数式@<m>{a^2 + b^2 = c^2}です',
        '@<href>{https://github.com/kmuto/review/blob/master/doc/format.rdoc,フォーマット}',
        '@<href>{https://github.com/kmuto/review/blob/master/doc/format.rdoc}',
        'ここは@<fn>{f1}脚注@<fn>{f2}',
        '//footnote[f1][脚注1]',
    ]
    for e in expected:
        assert e in re


@with_app(buildername='review', srcdir='tests/root', copy_srcdir_to_tmpdir=True)
def test_code(app, status, warnings):
    app.build()

    re = (app.outdir / 'code.re').read_text()

    # list
    expected = ('//list[なにもなしname][][c]{')
    assert expected in re
    expected = ('//listnum[行番号付きname][][ruby]{')
    assert expected in re

    # TODO: captionとnameを併用できない？
    #    expected = ('//list[キャプション付きname][キャプション][c]{')
    #    assert expected in re
    #    expected = ('//listnum[行番号付きキャプション付きname][行番号付きキャプション][ruby]{')
    #    assert expected in re


    # em
    expected = [
        '//emlist[][c]{',
        '//emlist[][c]{',
        '//emlist[emcaption][c]{',
        '//emlistnum[][ruby]{',
        ]
    for e in expected:
        assert e in re

    # firstlinenum
    expected = ('//firstlinenum[100]')
    assert expected in re

    # codeinline
    expected = ('@<code>{p = obj.ref_cnt}')
    assert expected in re

    # cmd
    expected = ('//cmd{\n$ cd /\n$ sudo rm -rf /\n//}')
    assert expected in re


@with_app(buildername='review', srcdir='tests/root', copy_srcdir_to_tmpdir=True)
def test_admonition(app, status, warnings):
    app.build()

    re = (app.outdir / 'admonition.re').read_text()

    expected = [
        '//tip[tipキャプション]{',
        '//note[noteキャプション]{',
        '//caution[dangerキャプション]{',
        '//info[hintキャプション]{',
        '//warning[warningキャプション]{',
        '//warning{',
#        '//quote{\n百聞は一見にしかず\n//}', #  TODO: 改行が入っている
    ]

    for e in expected:
        assert e in re


@with_app(buildername='review', srcdir='tests/root', copy_srcdir_to_tmpdir=True)
def test_table(app, status, warnings):
    app.build()

    re = (app.outdir / 'table.re').read_text()

    expected = [
        '//table[compact-label][]{\nA\tnot A\n------------\nFalse\tTrue\nTrue\tFalse\n//}',
        '//table[tablename][Frozen Delights!]{\nTreat\tQuantity\tDescription',
    ]

    for e in expected:
        assert e in re
