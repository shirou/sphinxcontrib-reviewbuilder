#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path

from docutils.io import FileOutput
from docutils.frontend import OptionParser
from docutils.nodes import Text, paragraph
from sphinx.builders.text import TextBuilder

from writer import ReVIEWWriter


# from japanesesupport.py
def trunc_whitespace(app, doctree, docname):
    for node in doctree.traverse(Text):
        if isinstance(node.parent, paragraph):
            newtext = node.astext()
            for c in "\n\r\t":
                newtext = newtext.replace(c, "")
            newtext = newtext.strip()
            node.parent.replace(node, Text(newtext))


class ReVIEWBuilder(TextBuilder):
    name = 'review'
    format = 'review'
    out_suffix = '.re'

    def prepare_writing(self, docnames):
        self.writer = ReVIEWWriter(self)


def setup(app):
    app.add_builder(ReVIEWBuilder)
    app.connect("doctree-resolved", trunc_whitespace)
