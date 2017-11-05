#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from six import text_type
from docutils import nodes, writers

from sphinx import version_info as SPHINX_VERSION
from sphinx.writers.text import TextTranslator


if False:
    # For type annotation
    from typing import Any, Callable, Tuple, Union  # NOQA
    from sphinx.builders.text import TextBuilder  # NOQA


class Table(object):
    def __init__(self):
        self.col = 0
        self.colcount = 0
        self.colspec = None
        self.rowcount = 0
        self.had_head = False
        self.has_problematic = False
        self.has_verbatim = False
        self.caption = None
        self.longtable = False


class ReVIEWWriter(writers.Writer):
    supported = ('review',)
    settings_spec = ('No options here.', '', ())
    settings_defaults = {}  # type: Dict

    output = None

    def __init__(self, builder):
        # type: (ReviewBuilder) -> None
        writers.Writer.__init__(self)
        self.builder = builder
        if SPHINX_VERSION < (1, 6):
            self.translator_class = ReVIEWTranslator

    def translate(self):
        if SPHINX_VERSION < (1, 6):
            visitor = self.translator_class(self.document, self.builder)
        else:
            visitor = self.builder.create_translator(self.document, self.builder)
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

    def __init__(self, document, builder):
        nodes.NodeVisitor.__init__(self, document)
        self.builder = builder

        newlines = builder.config.text_newlines
        if newlines == 'windows':
            self.nl = '\r\n'
        elif newlines == 'native':
            self.nl = os.linesep
        else:
            self.nl = '\n'
        self.end = "%s//}%s" % (self.nl, self.nl)
        self.states = [[]]
        self.stateindent = [0]
        self.list_counter = []
        self.sectionlevel = 0
        self.lineblocklevel = 0
        self.table = None

    def end_state(self, wrap=True, end=[''], first=None):
        content = self.states.pop()
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

    def visit_paragraph(self, node):
        self.new_state(0)

    def depart_paragraph(self, node):
        self.end_state()

    def depart_title(self, node):
        if self.table:
            return

        text = text_type(''.join(x[1] for x in self.states.pop() if x[0] == -1))
        self.stateindent.pop()
        text = text_type(text)

        marker = self.sectionchar * self.sectionlevel
        if node.parent['ids']:
            title = ['', u'%s{%s} %s' % (marker, node.parent['ids'][0], text)]
        else:
            title = ['', u'%s %s' % (marker, text)]
        if len(self.states) == 2 and len(self.states[-1]) == 0:
            # remove an empty line before title if it is first section title in the document
            title.pop(0)
        self.states[-1].append((0, title))
        self.add_text(self.nl)

    def visit_title_reference(self, node):
        """inline citation reference"""
        self.add_text('@<code>{')

    def depart_title_reference(self, node):
        self.add_text('}')

    def visit_reference(self, node):
        if 'internal' in node and node['internal']:
            # TODO: ターゲットごとに変える
            self.add_text('@<chap>{%s}' % (node.get('refuri', '').replace('#', '')))
        else:  # URL
            if 'name' in node:
                self.add_text('@<href>{%s,%s}' % (node.get('refuri', ''), node['name']))
            else:
                self.add_text('@<href>{%s}' % (node.get('refuri', '')))
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

    def depart_definition(self, node):
        pos = len(self.states[-2])
        TextTranslator.depart_definition(self, node)

        # replace a blank line by ``@<br>{}``
        while pos < len(self.states[-1]) - 1:
            item = self.states[-1][pos]
            if item[1] and item[1][-1] == '':
                item[1].pop()
                item[1][-1] += '@<br>{}'
            pos += 1

    def depart_bullet_list(self, node):
        TextTranslator.depart_bullet_list(self, node)
        if len(self.list_counter) == 0:
            self.add_text('')

    def depart_enumerated_list(self, node):
        TextTranslator.depart_enumerated_list(self, node)
        if len(self.list_counter) == 0:
            self.add_text('')

    def depart_list_item(self, node):
        # remove trailing space
        content = self.states[-1][-1][1]
        if content and content[-1] == '':
            content.pop()

        if self.list_counter[-1] == -1:
            self.end_state(first=' {} '.format('*' * len(self.list_counter)), end='')
        elif self.list_counter[-1] == -2:
            pass
        else:
            self.end_state(first=' {}. '.format(self.list_counter[-1]), end=None)

    def visit_literal_block(self, node):
        # TODO: remove highlight args
        self.new_state(0)

        lang = node.get('language', 'guess')

        if lang == "bash":  # use cmd
            self.add_text('//cmd{' + self.nl)
            return

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
                self.add_text('//firstlinenum[%s]%s' % (n, self.nl))
                # TODO: remove highlight args line
            t += "num"

        if names:
            self.add_text('//%s[%s][%s][%s]{%s' % (t, names, caption, lang, self.nl))
        else:
            self.add_text('//%s[%s][%s]{%s' % (t, caption, lang, self.nl))

    def depart_literal_block(self, node):
        self.end_state(end=['//}' + self.nl], wrap=False)

    def visit_caption(self, node):
        raise nodes.SkipNode

    def visit_literal(self, node):
        self.add_text('@<code>{')

    def depart_literal(self, node):
        self.add_text('}')

    def _make_visit_admonition(name):
        def visit_admonition(self, node):
            self.states[-1].append((0, [u'//%s{' % self.admonitionlabels[name]]))

        return visit_admonition

    def _depart_named_admonition(self, node):
        # remove trailing space
        content = self.states[-1][-1][1]
        while content and content[-1] == '':
            content.pop()
        self.states[-1].append((0, [u'//}']))

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
        self.add_text('//quote{\n%s%s' % (node.astext(), self.end))
        raise nodes.SkipNode

    def visit_math(self, node):
        self.add_text("@<m>{")

    def depart_math(self, node):
        self.add_text("}")

    def visit_math_block(self, node):
        self.add_text('//texequation{' + self.nl)

    def depart_math_block(self, node):
        self.add_text(self.end)

    def visit_footnote_reference(self, node):
        self.add_text('@<fn>{%s}' % node['refid'])
        raise nodes.SkipNode

    def visit_footnote(self, node):
        label = node['ids'][0]
        self.add_text('//footnote[%s][' % label)
        self.new_state(0)

    def depart_footnote(self, node):
        # convert all text inside footnote to single line
        self.end_state(wrap=False, end=None)
        footnote_text = self.states[-1].pop()[1]
        for line in footnote_text:
            self.add_text(line)

        self.add_text(']%s' % self.nl)

    def visit_table(self, node):
        if self.table:
            raise NotImplementedError('Nested tables are not supported.')
        self.table = [[]]
        label = ""
        if len(node['ids']) > 0:
            label = node['ids'][0]

        title = ""
        if isinstance(node.children[0], nodes.title):
            title = node.children[0].astext()
            node.children.pop(0)

        self.add_text(u'//table[%s][%s]{%s' % (label, title, self.nl))

    def visit_entry(self, node):
        if len(node) == 0:
            # Fill single-dot ``.`` for empty table cells
            self.table[-1].append('.')
            raise nodes.SkipNode
        else:
            TextTranslator.visit_entry(self, node)

    def depart_entry(self, node):
        TextTranslator.depart_entry(self, node)

        # replace return codes by @<br>{}
        text = self.table[-1].pop().strip()
        text = text.replace('\n', '@<br>{}')
        self.table[-1].append(text)

    def depart_row(self, node):
        self.add_text(u'\t'.join(self.table.pop()))
        self.add_text(self.nl)

    def depart_thead(self, node):
        self.add_text('------------' + self.nl)

    def depart_table(self, node):
        self.table = None
        self.add_text("//}" + self.nl)

    def visit_figure(self, node):
        self.new_state(0)

    def visit_image(self, node):
        caption = None
        for c in node.parent.children:
            if isinstance(c, nodes.caption):
                caption = c.astext()
        legend = None
        for c in node.parent.children:
            if isinstance(c, nodes.legend):
                legend = c.astext()

        filename = os.path.basename(os.path.splitext(node['uri'])[0])
        if node.get('inline'):
            self.add_text('@<icon>{%s}' % filename)
            raise nodes.SkipNode
        elif caption:
            self.add_text('//image[%s][%s]{%s' % (filename, caption, self.nl))
        else:
            self.add_text('//image[%s][]{%s' % (filename, self.nl))
        if legend:
            self.add_text(legend)

        self.add_text(self.nl + "//}" + self.nl)
        raise nodes.SkipNode

    def visit_legend(self, node):
        raise nodes.SkipNode

    def depart_figure(self, node):
        self.end_state()

    def visit_comment(self, node):
        for c in node.astext().splitlines():
            self.add_text('#@# %s%s' % (c, self.nl))

        raise nodes.SkipNode

    def visit_raw(self, node):
        form = node.get('format', '')
        self.new_state(0)
        self.add_text('//raw[|%s|%s]' % (form, node.astext()))
        self.end_state(wrap=False)
        raise nodes.SkipNode

    def visit_subscript(self, node):
        self.add_text('@<u>{')

    def depart_subscript(self, node):
        self.add_text('}')

    def visit_superscript(self, node):
        pass

    def visit_index(self, node):
        for entry in node.get('entries', []):
            e = []
            if entry[0] == 'single':
                t = [se.strip() for se in entry[1].split(';')]
                e.append('<<>>'.join(t))
            elif entry[0] == 'pair':
                for pair in entry[1].split(';'):
                    e.append(pair.strip())
            else:
                self.builder.warn('index only support single and pair: %s, line:%d' %
                                  (entry[0], node.line))
                continue

            for target in e:
                # TODO: インデックスの文字が入るのでhidxを使っている
                self.add_text('@<hidx>{%s}' % target)

#        i = 0
#        for c in node.parent.children:
#            if isinstance(c, nodes.target):
#                break
#            i += 1
#
#        node.parent.children.pop(i + 1)

        raise nodes.SkipNode
