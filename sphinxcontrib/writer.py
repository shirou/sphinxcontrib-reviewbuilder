#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import textwrap
from itertools import groupby

from six import itervalues, text_type
from six.moves import zip_longest
from six.moves import range

from docutils import nodes, writers, languages
from docutils.utils import column_width

from sphinx import addnodes
from sphinx.locale import admonitionlabels, _
from sphinx.util import logging
from sphinx.util.i18n import format_date

from sphinx.writers.text import TextTranslator


if False:
    # For type annotation
    from typing import Any, Callable, Tuple, Union  # NOQA
    from sphinx.builders.text import TextBuilder  # NOQA


class ReVIEWWriter(writers.Writer):
    supported = ('review',)
    settings_spec = ('No options here.', '', ())
    settings_defaults = {}  # type: Dict

    output = None

    def __init__(self, builder):
        # type: (ReviewBuilder) -> None
        writers.Writer.__init__(self)
        self.builder = builder
        self.translator_class = self.builder.translator_class or ReVIEWTranslator

    def translate(self):
        visitor = self.translator_class(self.document, self.builder)
        self.document.walkabout(visitor)
        self.output = visitor.body

STDINDENT = 0


class ReVIEWTranslator(TextTranslator):
    sectionchar = u"="

    admonitionlabels = {
        "note": "note",
        "tip": "tip",
        "info": "info",
        "warning": "warning",
        "important": "important",
        "caution": "caution",
        "notice": "notice",
        "attention": "notice",
        "danger": "caution",
        "error": "caution",
        "hint": "info",
    }

    def end_state(self, wrap=True, end=[''], first=None):
        content = self.states.pop()
        maxindent = sum(self.stateindent)
        indent = self.stateindent.pop()
        result = []
        toformat = []

        def do_format():
            if not toformat:
                return
            res = ''.join(toformat).splitlines()
            if end:
                res += end
            result.append((indent, res))
        for itemindent, item in content:
            if itemindent == -1:
                toformat.append(item)
            else:
                do_format()
                result.append((indent + itemindent, item))
                toformat = []
        do_format()
        if first is not None and result:
            itemindent, item = result[0]
            result_rest, result = result[1:], []
            if item:
                toformat = [first + ' '.join(item)]
                do_format()  # re-create `result` from `toformat`
                _dummy, new_item = result[0]
                result.insert(0, (itemindent - indent, [new_item[0]]))
                result[1] = (itemindent, new_item[1:])
                result.extend(result_rest)
        self.states[-1].extend(result)


    def visit_section(self, node):
        self._title_char = self.sectionchar * self.sectionlevel
        self.sectionlevel += 1

    def depart_title(self, node):
        text = text_type(''.join(x[1] for x in self.states.pop() if x[0] == -1))
        self.stateindent.pop()
        text = unicode(text)  # TODO

        title = [u'{} {}'.format(self.sectionchar * self.sectionlevel, text)]

        self.states[-1].append((0, title))
        self.add_text('\n')

    def visit_title_reference(self, node):
        """inline citation reference"""
        self.add_text('@<code>{')

    def depart_title_reference(self, node):
        self.add_text('}')

    def visit_reference(self, node):
        if 'name' in node:
            self.add_text('@<href>{%s,%s}' % (node['refuri'], node['name']))
        else:
            self.add_text('@<href>{%s}' % (node['refuri']))
        raise nodes.SkipNode

    def visit_emphasis(self, node):
        self.add_text('@<i>{')

    def depart_emphasis(self, node):
        self.add_text('}')

    def visit_literal_emphasis(self, node):
        self.add_text('@<i>{')

    def depart_literal_emphasis(self, node):
        self.add_text('}')

    def visit_strong(self, node):
        self.add_text('@<b>{')

    def depart_strong(self, node):
        self.add_text('}')

    def visit_literal_strong(self, node):
        self.add_text('@<b>{')

    def depart_literal_strong(self, node):
        self.add_text('}')

    def visit_abbreviation(self, node):
        self.add_text('')

    def visit_list_item(self, node):
        if self.list_counter[-1] == -1:
            # bullet list
            self.new_state(0)
        elif self.list_counter[-1] == -2:
            # definition list
            pass
        else:
            # enumerated list
            self.list_counter[-1] += 1
            self.new_state(0)

    def depart_term(self, node):
        if not self._classifier_count_in_li:
            self.end_state(first=" : ", end='')

    def depart_list_item(self, node):
        if self.list_counter[-1] == -1:
            self.end_state(first='{} '.format('*' * len(self.list_counter)), end='')
        elif self.list_counter[-1] == -2:
            pass
        else:
            self.end_state(first='{}. '.format(self.list_counter[-1]), end=None)

    def visit_literal_block(self, node):
        self.new_state(0)
        # TODO: remove highlight args

        lang = node['language']
        names = False  # get reference if exists
        t = "emlist"
        if 'names' in node and len(node['names']) > 0:
            names = ''.join(node['names'])
            t = "list"

        caption = ""
        if isinstance(node.parent[0], nodes.caption):
            caption = node.parent[0].astext()

        if 'linenos' in node and node['linenos']:
            if 'highlight_args' in node and 'linenostart' in node['highlight_args']:
                n = node['highlight_args']['linenostart']
                self.add_text('//firstlinenum[%s]\n' % n)
                # TODO: remove highlight args line
            t += "num"

        if names:
            self.add_text('//%s[%s][%s][%s]{\n' % (t, names, caption, lang))
        else:
            self.add_text('//%s[%s][%s]{\n' % (t, caption, lang))

    def depart_literal_block(self, node):
        self.end_state(end=['//}\n'], wrap=False)

    def visit_caption(self, node):
        raise nodes.SkipNode

    def visit_literal(self, node):
        self.add_text('@<code>{')

    def depart_literal(self, node):
        self.add_text('}')

    def _make_visit_admonition(name):
        def visit_admonition(self, node):
            caption = None
            if len(node.children) > 1:
                caption = node.children[0].astext()
                node.children.pop(0)
            if caption:
                f = u'//%s[%s]{\n' % (self.admonitionlabels[name], caption)
            else:
                f = u'//%s{\n' % (self.admonitionlabels[name])
            self.add_text(f)

        return visit_admonition

    def _depart_named_admonition(self, node):
        self.add_text("\n//}\n")

    visit_attention = _make_visit_admonition('attention')
    depart_attention = _depart_named_admonition
    visit_caution = _make_visit_admonition('caution')
    depart_caution = _depart_named_admonition
    visit_danger = _make_visit_admonition('danger')
    depart_danger = _depart_named_admonition
    visit_error = _make_visit_admonition('error')
    depart_error = _depart_named_admonition
    visit_hint = _make_visit_admonition('hint')
    depart_hint = _depart_named_admonition
    visit_important = _make_visit_admonition('important')
    depart_important = _depart_named_admonition
    visit_note = _make_visit_admonition('note')
    depart_note = _depart_named_admonition
    visit_tip = _make_visit_admonition('tip')
    depart_tip = _depart_named_admonition
    visit_warning = _make_visit_admonition('warning')
    depart_warning = _depart_named_admonition

    def visit_block_quote(self, node):
        self.add_text("//quote{\n")

    def depart_block_quote(self, node):
        self.add_text("\n//}\n")

    def visit_math(self, node):
        self.add_text("@<m>{")

    def depart_math(self, node):
        self.add_text("}")

    def visit_math_block(self, node):
        self.add_text('//texequation{\n')

    def depart_math_block(self, node):
        self.add_text('\n}\n')


    def visit_footnote_reference(self, node):
        self.add_text('@<fn>{%s}' % node['refid'])
        raise nodes.SkipNode

    def visit_footnote(self, node):
        label = node['ids'][0]
        self.add_text('//footnote[%s][%s]\n' % (label, node.children[1].astext()))
        raise nodes.SkipNode
