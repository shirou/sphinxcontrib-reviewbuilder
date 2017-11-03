# -*- coding: utf-8 -*-

import os
from tempfile import gettempdir

import pytest
from sphinx.testing.path import path

pytest_plugins = 'sphinx.testing.fixtures'


@pytest.fixture(scope='session')
def rootdir():
    return path(os.path.dirname(__file__) or '.').abspath()


@pytest.fixture(scope='session')
def sphinx_test_tempdir():
    """
    temporary directory that wrapped with `path` class.
    """
    tmpdir = path(gettempdir()).abspath() / 'reviewbuilder'
    if tmpdir.exists():
        tmpdir.rmtree()

    return tmpdir
