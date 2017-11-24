# -*- coding: utf-8 -*-
"""
    sphinxcontrib-reviewbuilder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2013 by the WAKAYAMA Shirou, Takeshi Komiya
    :license: LGPLv2, see LICENSE for details.
"""

from __future__ import absolute_import

from docutils import nodes

from sphinxcontrib.reviewbuilder import reviewbuilder, transforms


# from japanesesupport.py
def trunc_whitespace(app, doctree, docname):
    for node in doctree.traverse(nodes.Text):
        if isinstance(node.parent, nodes.paragraph):
            newtext = node.astext()
            for c in "\n\r\t":
                newtext = newtext.replace(c, "")
            newtext = newtext.strip()
            node.parent.replace(node, nodes.Text(newtext))


def setup(app):
    app.connect("doctree-resolved", trunc_whitespace)
    reviewbuilder.setup(app)
    transforms.setup(app)
