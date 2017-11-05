# -*- coding: utf-8 -*-
"""
    sphinxcontrib-reviewbuilder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2013 by the WAKAYAMA Shirou
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
            for i, item in reversed(list(enumerate(deflist))):
                found = []
                for node in reversed(item[1]):
                    if not isinstance(node, nodes.paragraph):
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


class NumberReferenceConverter(SphinxTransform):
    """Convert number references to Re:VIEW's reference notations."""
    default_priority = 5  # before ReferencesResolver

    def apply(self):
        for node in self.document.traverse(addnodes.pending_xref):
            if node['refdomain'] == 'std' and node['reftype'] == 'numref':
                docname, target_node = self.lookup(node)
                if target_node is None:
                    logger.warning('Invalid number_reference: %s', node, location=node)
                    node.replace_self(node[0])
                    continue

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
                    text = '@<chap>{%s%s}' % (prefix, target_node['ids'][0])
                else:
                    logger.warning('Unsupported number_reference: %s', node,
                                   location=node)
                    continue

                ref = nodes.Text(text, text)
                node.replace_self(ref)

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


def setup(app):
    app.add_post_transform(DefinitionListTransform)
    app.add_post_transform(NumberReferenceConverter)
