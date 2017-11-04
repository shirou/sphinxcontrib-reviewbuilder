#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        '//footnote[f2][脚注2は@<i>{インライン}@<b>{要素}を@<href>{https://github.com/kmuto/review,含みます}]',
        '#@# コメントです',
        '#@# コメントブロック1\n#@# コメントブロック2',
        '//raw[|html|<hr width=50 size=10>]',
        '@<u>{下線}を引きます',
        '索引@<hidx>{インデックス}インデックスを作ります',  # TODO: インデックス文字が入っている
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
        '//quote{\n百聞は一見にしかず\n//}',
    ]

    for e in expected:
        assert e in re


@with_app(buildername='review', srcdir='tests/root', copy_srcdir_to_tmpdir=True)
def test_list(app, status, warnings):
    app.build()

    re = (app.outdir / 'list.re').read_text()

    expected = [
        ' * 第3の項目 \n\nLorem ipsum dolor sit amet,\n',
        ' 3. 第3の条件 \n\nLorem ipsum dolor sit amet,\n',
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
        ('//table[multiple-paragraph][]{\nA\tnot A\n------------\nLorem ipsum@<br>{}@<br>{}dolor sit amet,\t'
         'consectetur adipiscing elit,\n//}'),
    ]

    for e in expected:
        assert e in re


@with_app(buildername='review', srcdir='tests/root', copy_srcdir_to_tmpdir=True)
def test_figure(app, status, warnings):
    app.build()

    re = (app.outdir / 'figure.re').read_text()

    expected = [
        '//image[picture][ここはfigureのキャプションです。]{',
        '//image[picture][]{',
    ]

    for e in expected:
        assert e in re
