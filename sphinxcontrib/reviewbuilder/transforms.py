# -*- coding: utf-8 -*-
"""
    sphinxcontrib-reviewbuilder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2013 by the WAKAYAMA Shirou, Takeshi Komiya
    :license: LGPLv2, see LICENSE for details.
"""

from __future__ import absolute_import

import os

from docutils import nodes
from sphinx import addnodes
from sphinx.transforms import SphinxTransform
from sphinx.util import logging

logger = logging.getLogger(__name__)


class DefinitionListTransform(SphinxTransform):
    """Transform definition list to fit Re:VIEW format."""
    default_priority = 100

    def apply(self):
        if self.app.builder.name != 'review':
            return

        for deflist in self.document.traverse(nodes.definition_list):
            self.convert_figure_to_image(deflist)
            self.extract_non_paragraph_node(deflist)

    def convert_figure_to_image(self, deflist):
        """Convert figure node to inline (image node)."""
        for node in deflist.traverse(nodes.figure):
            if any(node.traverse(nodes.caption)):
                logger.warning('In Re:VIEW, definition list can\'t contain figures. '
                               'The caption is ignored.', location=node)
            image = node.pop(0)
            image['inline'] = True
            node.replace_self(image)

    def extract_non_paragraph_node(self, deflist):
        """Extract non paragraph node (ex. literal_block) to after the list."""
        ALLOWED_NODES = (nodes.paragraph, nodes.image)

        for i, item in reversed(list(enumerate(deflist))):
            found = []
            for node in reversed(item[1]):
                if not isinstance(node, ALLOWED_NODES):
                    logger.warning('In Re:VIEW, definition list can\'t contain %s. '
                                   'Moved it after the list.',
                                   node.tagname, location=node)
                    found.append(node)

            if found:
                pos = deflist.parent.index(deflist)

                # separate definition list if non paragraph nodes found
                if deflist[i + 1:]:
                    new_deflist = nodes.definition_list()
                    for item in deflist[i + 1:]:
                        deflist.remove(item)
                        new_deflist += item
                    deflist.parent.insert(pos + 1, new_deflist)

                # move non paragraph nodes after the definition list
                for node in found:
                    node.parent.remove(node)
                    deflist.parent.insert(pos + 1, node)


class ReVIEWReferenceResolver(SphinxTransform):
    """Convert Sphinx-references to Re:VIEW's reference notations."""
    default_priority = 5  # before Sphinx's ReferencesResolver

    def apply(self):
        if self.app.builder.name != 'review':
            return

        for node in self.document.traverse(addnodes.pending_xref):
            if node['refdomain'] == 'std' and node['reftype'] == 'numref':
                self.resolve_numref(node)
            elif node['refdomain'] == 'std' and node['reftype'] == 'doc':
                self.resolve_doc(node)
            elif node['refdomain'] == 'std' and node['reftype'] == 'ref':
                self.resolve_section_ref(node)

        for node in self.document.traverse(nodes.reference):
            self.resolve_hyperref(node)

    def resolve_numref(self, node):
        docname, target_node = self.lookup(node)
        if target_node is None:
            logger.warning('Invalid number_reference: %s', node, location=node)
            node.replace_self(node[0])
            return

        if docname == self.env.docname:
            prefix = ''
        else:
            prefix = os.path.basename(docname) + '|'

        if isinstance(target_node, nodes.table):
            text = '@<table>{%s%s}' % (prefix, target_node['ids'][0])
        elif isinstance(target_node, nodes.figure):
            filename = os.path.basename(os.path.splitext(target_node[0]['uri'])[0])
            text = '@<img>{%s%s}' % (prefix, filename)
        elif isinstance(target_node, nodes.literal_block):
            text = '@<list>{%s%s}' % (prefix, ''.join(target_node['names']))
        elif isinstance(target_node, nodes.section):
            if isinstance(target_node.parent, nodes.document):
                text = '@<chap>{%s}' % (os.path.basename(docname))
            else:
                text = '@<hd>{%s%s}' % (prefix, target_node['ids'][0])
        else:
            logger.warning('Unsupported number_reference: %s', node,
                           location=node)
            return

        ref = nodes.Text(text, text)
        node.replace_self(ref)

    def resolve_section_ref(self, node):
        docname, target_node = self.lookup(node)
        if target_node is None:
            logger.warning('Invalid reference: %s', node, location=node)
            node.replace_self(node[0])
            return

        if isinstance(target_node, nodes.section):
            if isinstance(target_node.parent, nodes.document):
                text = '@<chap>{%s}' % (os.path.basename(docname))
            else:
                heading_id = self.get_heading_id(docname, target_node)
                text = '@<hd>{%s}' % '|'.join(heading_id)
        else:
            return  # skip

        ref = nodes.Text(text, text)
        node.replace_self(ref)

    def resolve_hyperref(self, node):
        docname = self.env.docname
        target_node = self.env.get_doctree(docname).ids.get(node.get('refid'))
        if target_node is None:
            return

        if isinstance(target_node, nodes.section):
            if isinstance(target_node.parent, nodes.document):
                text = '@<chap>{%s}' % (os.path.basename(docname))
            else:
                heading_id = self.get_heading_id(docname, target_node)
                text = '@<hd>{%s}' % '|'.join(heading_id)
        else:
            return  # skip

        index = node.parent.index(node)
        ref = nodes.Text(text, text)
        node.parent.insert(index, ref)
        node.parent.remove(node)

    def resolve_doc(self, node):
        text = '@<chap>{%s}' % os.path.basename(node['reftarget'])
        ref = nodes.Text(text, text)
        node.replace_self(ref)

    def get_heading_id(self, docname, node):
        headings = []
        while not isinstance(node.parent, nodes.document):
            if isinstance(node, nodes.section):
                headings.append(node['ids'][0])
            node = node.parent

        if docname != self.env.docname:
            headings.append(os.path.basename(docname))

        return reversed(headings)

    def lookup(self, node):
        std = self.env.get_domain('std')
        if node['reftarget'] in std.data['labels']:
            docname, labelid, _ = std.data['labels'].get(node['reftarget'], ('', '', ''))
        else:
            docname, labelid = std.data['anonlabels'].get(node['reftarget'], ('', ''))

        if not docname:
            return None, None

        target_node = self.env.get_doctree(docname).ids.get(labelid)
        return docname, target_node


class NestedEnumeratedListChecker(SphinxTransform):
    """Check and warn if nested enumerated list exists."""
    default_priority = 999

    def apply(self):
        if self.app.builder.name != 'review':
            return

        ALLOWED_NODES = (nodes.paragraph, nodes.image)
        for node in self.document.traverse(nodes.enumerated_list):
            for item in node:
                for subnode in item:
                    if not isinstance(subnode, ALLOWED_NODES):
                        logger.warning('In Re:VIEW, enumerated list can\'t contain %s.',
                                       subnode.tagname, location=subnode)
                        break


def setup(app):
    app.add_post_transform(DefinitionListTransform)
    app.add_post_transform(ReVIEWReferenceResolver)
    app.add_post_transform(NestedEnumeratedListChecker)
