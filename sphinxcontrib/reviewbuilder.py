#!/usr/bin/env python
# -*- coding: utf-8 -*-

from writer import ReVIEWWriter
from sphinx.builders.text import TextBuilder


class ReVIEWBuilder(TextBuilder):
    name = 'review'
    format = 'review'
    out_suffix = '.re'

    def prepare_writing(self, docnames):
        self.writer = ReVIEWWriter(self)

def setup(app):
    app.add_builder(ReVIEWBuilder)
