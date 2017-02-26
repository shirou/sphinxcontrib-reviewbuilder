#!/usr/bin/env python
# -*- coding: utf-8 -*-

from docutils.utils import column_width
from sphinx.writers.text import MAXWIDTH

from sphinx_testing import with_app


@with_app(buildername='review', srcdir='tests/root', copy_srcdir_to_tmpdir=True)
def test_basic(app, status, warnings):
    app.build()
    print(status.getvalue(), warnings.getvalue())

#    import pdb; pdb.set_trace()

    re = (app.outdir / 'basic.re').read_text()
    print(re)

    expected = ('= section 1')
    assert expected in re

    expected = ('== section 2')
    assert expected in re

    expected = ('=== section 3')
    assert expected in re

    expected = ('==== section 4.0')
    assert expected in re

    expected = ('===== section 5')
    assert expected in re

    expected = ('==== section 4.1')
    assert expected in re

    expected = ('@<i>{強調}')
    assert expected in re
    expected = ('@<b>{強い強調}')
    assert expected in re




@with_app(buildername='review', srcdir='tests/root', copy_srcdir_to_tmpdir=True)
def test_basic(app, status, warnings):
    app.build()
    print(status.getvalue(), warnings.getvalue())

#    import pdb; pdb.set_trace()

    re = (app.outdir / 'basic.re').read_text()
    print(re)

    expected = ('= section 1')
    assert expected in re

    expected = ('== section 2')
    assert expected in re

    expected = ('=== section 3')
    assert expected in re


@with_app(buildername='review', srcdir='tests/root', copy_srcdir_to_tmpdir=True)
def test_code(app, status, warnings):
    app.build()
    print(status.getvalue(), warnings.getvalue())

    re = (app.outdir / 'code.re').read_text()
    print(re)

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
    expected = ('//emlist[][c]{')
    assert expected in re
    expected = ('//emlist[emcaption][c]{')
    assert expected in re
    expected = ('//emlistnum[][ruby]{')
    assert expected in re

    # firstlinenum
    expected = ('//firstlinenum[100]')
    assert expected in re

    # codeinline
    expected = ('@<code>{p = obj.ref_cnt}')
    assert expected in re
