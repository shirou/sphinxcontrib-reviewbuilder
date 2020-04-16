#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import


from os import path
import codecs

from six import iteritems
from docutils import nodes
from docutils.io import StringOutput
from sphinx.builders.text import TextBuilder
from sphinx.util.fileutil import copy_asset_file
from sphinx.util import logging
from sphinx.util.osutil import ensuredir
from sphinx.util.console import bold
from sphinx.util.template import SphinxRenderer

from sphinxcontrib.reviewbuilder.writer import ReVIEWWriter, ReVIEWTranslator

logger = logging.getLogger(__name__)

TEMPLATE = """
PREDEF:
{%- for item in predef %}
- {{ item }}
{%- endfor %}

CHAPS:
{%- for item in chaps %}
- {{ item }}
{%- endfor %}

APPENDIX:
{%- for item in appendix %}
- {{ item }}
{%- endfor %}

POSTDEF:
{%- for item in postdef %}
- {{ item }}
{%- endfor %}
"""


class ReVIEWBuilder(TextBuilder):
    name = 'review'
    format = 'review'
    out_suffix = '.re'
    out_files = []
    supported_image_types = ['image/svg+xml', 'image/png',
                             'image/gif', 'image/jpeg']
    default_translator_class = ReVIEWTranslator

    def prepare_writing(self, docnames):
        self.writer = ReVIEWWriter(self)

    def write_doc(self, docname, doctree):
        self.current_docname = docname
        destination = StringOutput(encoding='utf-8')
        self.writer.write(doctree, destination)

        filename = path.basename(docname) + self.out_suffix
        try:
            with codecs.open(path.join(self.outdir, filename), 'w', 'utf-8') as f:
                f.write(self.writer.output)
            self.out_files.append(filename)
        except (IOError, OSError) as err:
            logger.warn("error writing file %s: %s" % (filename, err))

        self.post_process_images(docname, doctree)

    def get_target_uri(self, docname, typ=None):
        # type: (unicode, unicode) -> unicode
        return docname

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
                    logger.warn(
                        'no matching candidate for image URI %r' % node['uri'],
                        '%s:%s' % (node.source, getattr(node, 'line', '')))
                    continue
                node['uri'] = candidate
            else:
                candidate = node['uri']
            if candidate not in self.env.images:
                # non-existing URI; let it alone
                continue
            dest = path.join(path.basename(docname), self.env.images[candidate][1])
            self.images[dest] = candidate

    def finish(self):
        if self.config.review_catalog_file:
            copy_asset_file(path.join(self.srcdir, self.config.review_catalog_file), self.outdir)
        else:
            catalogfile = path.join(self.outdir, "catalog.yml")
            with codecs.open(catalogfile, 'w', 'utf-8') as f:
                template = SphinxRenderer()
                f.write(template.render_string(TEMPLATE, {'chaps': self.out_files}))

        # copy image files
        if self.images:
            logger.info(bold('copying images...'), nonl=True)
            for dest, src in iteritems(self.images):
                logger.info(' ' + src, nonl=True)
                outdir = path.join(self.outdir, "images")
                outfile = path.join(outdir, dest)
                ensuredir(path.dirname(outfile))
                copy_asset_file(path.join(self.srcdir, src),
                                outfile)



def setup(app):
    app.add_builder(ReVIEWBuilder)
    app.add_config_value('review_catalog_file', '', 'review')
    app.add_config_value('review_keep_comments', False, 'review')
    app.add_config_value('review_use_cmd_block', True, 'review')
