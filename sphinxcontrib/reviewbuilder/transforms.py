# -*- coding: utf-8 -*-
"""
    sphinxcontrib-reviewbuilder
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2013 by the WAKAYAMA Shirou
    :license: LGPLv2, see LICENSE for details.
"""

from __future__ import absolute_import

from docutils import nodes
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


def setup(app):
    app.add_post_transform(DefinitionListTransform)
