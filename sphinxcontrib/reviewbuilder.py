#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
import codecs

from six import iteritems
from docutils import nodes
from docutils.io import FileOutput, StringOutput
from docutils.frontend import OptionParser
from docutils.nodes import Text, paragraph
from sphinx.builders.text import TextBuilder
from sphinx.util.fileutil import copy_asset_file
from sphinx.util.osutil import ensuredir, os_path
from sphinx.util.console import bold, darkgreen

from writer import ReVIEWWriter

TEMPLATE = """
PREDEF:

CHAPS:
%s

APPENDIX:

POSTDEF:
"""


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
    out_files = []

    def prepare_writing(self, docnames):
        self.writer = ReVIEWWriter(self)

    def write_doc(self, docname, doctree):
        self.current_docname = docname
        destination = StringOutput(encoding='utf-8')
        self.writer.write(doctree, destination)
        outfilename = path.join(self.outdir, os_path(docname) + self.out_suffix)

        ensuredir(path.dirname(outfilename))
        try:
            with codecs.open(outfilename, 'w', 'utf-8') as f:
                f.write(self.writer.output)
            self.out_files.append(outfilename)
        except (IOError, OSError) as err:
            self.warn("error writing file %s: %s" % (outfilename, err))

        self.post_process_images(docname, doctree)

    def post_process_images(self, docname, doctree):
        """Pick the best candidate for all image URIs."""
        for node in doctree.traverse(nodes.image):
            if '?' in node['candidates']:
                # don't rewrite nonlocal image URIs
                continue
            if '*' not in node['candidates']:
                for imgtype in self.supported_image_types:
                    candidate = node['candidates'].get(imgtype, None)
                    if candidate:
                        break
                else:
                    self.warn(
                        'no matching candidate for image URI %r' % node['uri'],
                        '%s:%s' % (node.source, getattr(node, 'line', '')))
                    continue
                node['uri'] = candidate
            else:
                candidate = node['uri']
            if candidate not in self.env.images:
                # non-existing URI; let it alone
                continue
            self.images[candidate] = path.join(docname, self.env.images[candidate][1])

    def finish(self):
        chaps = []
        for f in self.out_files:
            chaps.append('  - %s' % path.basename(f))
        catalogfile = path.join(self.outdir, "catalog.yml")
        with codecs.open(catalogfile, 'w', 'utf-8') as f:
            f.write(TEMPLATE % '\n'.join(chaps))

        # copy image files
        if self.images:
            self.info(bold('copying images...'), nonl=1)
            for src, dest in iteritems(self.images):
                self.info(' ' + src, nonl=1)
                outdir = path.join(self.outdir, "images")
                outfile = path.join(outdir, dest)
                ensuredir(path.dirname(outfile))
                copy_asset_file(path.join(self.srcdir, src),
                                outfile)
            self.info()


def setup(app):
    app.add_builder(ReVIEWBuilder)
    app.connect("doctree-resolved", trunc_whitespace)
