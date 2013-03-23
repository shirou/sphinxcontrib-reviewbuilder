#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from docutils import nodes, writers, languages


class ReVIEWWriter(writers.Writer):
    def __init__(self, builder):
        self.builder = builder
        writers.Writer.__init__(self)

    def translate(self):
        visitor = ReVIEWTranslator(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.astext()


class ReVIEWTranslator(nodes.NodeVisitor):
    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        self.document = document
        self.settings = settings = document.settings
        lcode = settings.language_code
        self.language = languages.get_language(lcode, document.reporter)
        self.head = []
        self.body = []
        self.foot = []
        self.section_level = 0
        self.context = []
        self.topic_class = ''
        self.colspecs = []
        self.compact_p = 1
        self.compact_simple = None
        # the list style "*" bullet or "#" numbered
        self._list_char = []
        self._line_block = 0
        self.authors = []
        self.section_level = 0
        self._indent = [0]
        self.defs = {
                'indent' : ('.INDENT %.1f\n', '.UNINDENT\n'),
                'definition_list_item' : ('.TP', ''),
                'field_name' : ('.TP\n.B ', '\n'),
                'literal' : ('\\fB', '\\fP'),
                'literal_block' : ('.sp\n.nf\n.ft C\n', '\n.ft P\n.fi\n'),

                'option_list_item' : ('.TP\n', ''),

                'reference' : (r'\fI\%', r'\fP'),
                'emphasis': ('\\fI', '\\fP'),
                'strong' : ('\\fB', '\\fP'),
                'term' : ('\n.B ', '\n'),
                'title_reference' : ('\\fI', '\\fP'),

                'topic-title' : ('== ',),
                'sidebar-title' : ('== ',),

                'problematic' : ('\n.nf\n', '\n.fi\n'),
                    }

    def ensure_eol(self):
        """Ensure the last line in body is terminated by new line."""
        if self.body[-1][-1] != '\n':
            self.body.append('\n')

    def astext(self):
        """Return the final formatted document as a string."""
        del(self.body[0])  # delete first empty line
        return ''.join(self.body)

    def visit_Text(self, node):
        if isinstance(node.parent.parent, nodes.list_item): # TODO
            self.body.pop()
            raise nodes.SkipNode
        elif isinstance(node.parent.parent, nodes.definition):
            d = node.astext().split("\n")  # add white spaces to each line
            d = map((lambda x: "    " + x), d)
            self.body += "\n".join(d)
            raise nodes.SkipNode
        self.body.append(node.astext().strip())

    def depart_Text(self, node):
        pass

    def list_start(self, node):
        class enum_char(object):
            def __init__(self, style, indent):
                self._style = style
                if node.has_key('start'):
                    self._cnt = node['start'] - 1
                else:
                    self._cnt = 0
                self._indent = indent

            def next(self):
                if self._style == 'bullet':
                    return ' ' + ('*' * self._indent) + ' '
                self._cnt += 1
                return " %d. " % self._cnt

            def get_width(self):
                return self._indent

            def indent(self, by=1):
                self._indent += by

        i = len(self._indent) - 1
        if node.has_key('enumtype'):
            self._list_char.append(enum_char(node['enumtype'], i))
        else:
            self._list_char.append(enum_char('bullet', i))

        self.indent(1)
        self._list_char[-1].indent(1)

    def list_end(self):
        self.dedent()
        self._list_char.pop()

    def visit_admonition(self, node, name=None):
        #
        # Make admonitions a simple block quote
        # with a strong heading
        #
        # Using .IP/.RE doesn't preserve indentation
        # when admonitions contain bullets, literal,
        # and/or block quotes.
        #
        if name:
            # .. admonition:: has no name
            name = '%s%s:%s\n' % (
                self.defs['strong'][0],
                self.language.labels.get(name, name).upper(),
                self.defs['strong'][1],
                )
            self.body.append(name)
        self.visit_block_quote(node)

    def depart_admonition(self, node):
        self.depart_block_quote(node)

    def visit_attention(self, node):
        self.visit_admonition(node, 'attention')

    depart_attention = depart_admonition

    def visit_block_quote(self, node):
        self.body.append("//quote{")
        self.indent(1)
        self.indent(0)

    def depart_block_quote(self, node):
        self.dedent()
        self.dedent()
        self.body.append("//}\n")

    def visit_bullet_list(self, node):
        self.list_start(node)

    def depart_bullet_list(self, node):
        self.list_end()

    def visit_caption(self, node):
        pass

    def depart_caption(self, node):
        pass

    def visit_caution(self, node):
        self.visit_admonition(node, 'caution')

    depart_caution = depart_admonition

    def visit_citation(self, node):
        num, text = node.astext().split(None, 1)
        num = num.strip()
        self.body.append('.IP [%s] 5\n' % num)

    def depart_citation(self, node):
        pass

    def visit_citation_reference(self, node):
        self.body.append('['+node.astext()+']')
        raise nodes.SkipNode

    def visit_classifier(self, node):
        pass

    def depart_classifier(self, node):
        pass

    def visit_colspec(self, node):
        self.colspecs.append(node)

    def depart_colspec(self, node):
        pass

    def write_colspecs(self):
        self.body.append("%s.\n" % ('L '*len(self.colspecs)))

    def visit_comment(self, node,
                      sub=re.compile('-(?=-)').sub):
        self.body.append('#@# ' + node.astext())
        raise nodes.SkipNode

    def visit_container(self, node):
        pass

    def depart_container(self, node):
        pass

    def visit_compound(self, node):
        pass

    def depart_compound(self, node):
        pass

    def visit_danger(self, node):
        self.visit_admonition(node, 'danger')

    depart_danger = depart_admonition

    def visit_decoration(self, node):
        pass

    def depart_decoration(self, node):
        pass

    def visit_definition(self, node):
        pass

    def depart_definition(self, node):
        pass

    def visit_definition_list(self, node):
        self.indent(1)

    def depart_definition_list(self, node):
        self.dedent()

    def visit_definition_list_item(self, node):
        self.body.append(": ")

    def depart_definition_list_item(self, node):
        pass

    def visit_description(self, node):
        pass

    def depart_description(self, node):
        pass

    def visit_doctest_block(self, node):
        self.body.append(self.defs['literal_block'][0])
        self._in_literal = True

    def depart_doctest_block(self, node):
        self._in_literal = False
        self.body.append(self.defs['literal_block'][1])

    def visit_document(self, node):
        # no blank line between comment and header.
        self.body.append('\n')
        # writing header is postboned
        self.header_written = 0

    def depart_document(self, node):
        pass

    def visit_emphasis(self, node):
        self.body.append('@<i>{')

    def depart_emphasis(self, node):
        self.body.append('}')

    def visit_entry(self, node):
        # a cell in a table row
        if 'morerows' in node:
            self.document.reporter.warning('"table row spanning" not supported',
                    base_node=node)
        if 'morecols' in node:
            self.document.reporter.warning(
                    '"table cell spanning" not supported', base_node=node)
        self.context.append(len(self.body))

    def depart_entry(self, node):
        start = self.context.pop()
        self._active_table.append_cell(self.body[start:])
        del self.body[start:]

    def visit_enumerated_list(self, node):
        self.list_start(node)

    def depart_enumerated_list(self, node):
        self.list_end()

    def visit_error(self, node):
        self.visit_admonition(node, 'error')

    depart_error = depart_admonition


    def visit_figure(self, node):
        text = []
        if 'alt' in node.attributes:
            text.append(node.attributes['alt'])
        if 'uri' in node.attributes:
            text.append(node.attributes['uri'])
        caption = ''
        if len(node.children) > 1:
            caption = node.children[1].astext()
        self.body.append('//image[%s][%s]{\n' % ('/'.join(text), caption))
        self.body.append('//}\n')
        raise nodes.SkipNode

    def depart_figure(self, node):
        self.visit_admonition(node, 'important')

    def visit_footer(self, node):
        self.document.reporter.warning('"footer" not supported',
                base_node=node)

    def depart_footer(self, node):
        pass

    def visit_footnote(self, node):
        label = node['ids'][0]
        self.body.append('//footnote[%s][' % label)

    def depart_footnote(self, node):
        self.body.pop()
        del(self.body[-2])  # remove new lines afound footnote
        self.body.append(']\n')

    def footnote_backrefs(self, node):
        self.document.reporter.warning('"footnote_backrefs" not supported',
                base_node=node)

    def visit_footnote_reference(self, node):
        self.body.append('[' + node.astext() + ']')
        raise nodes.SkipNode

    def depart_footnote_reference(self, node):
        pass

    def visit_generated(self, node):
        pass

    def depart_generated(self, node):
        pass

    def visit_header(self, node):
        raise NotImplementedError, node.astext()

    def depart_header(self, node):
        pass

    def visit_hint(self, node):
        self.visit_admonition(node, 'hint')

    depart_hint = depart_admonition

    def visit_subscript(self, node):
        self.body.append('\\s-2\\d')

    def depart_subscript(self, node):
        self.body.append('\\u\\s0')

    def visit_superscript(self, node):
        self.body.append('\\s-2\\u')

    def depart_superscript(self, node):
        self.body.append('\\d\\s0')

    def visit_attribution(self, node):
        self.body.append('\\(em ')

    def depart_attribution(self, node):
        self.body.append('\n')

    def visit_image(self, node):
        pass

    def visit_important(self, node):
        pass

    depart_important = depart_admonition

    def visit_label(self, node):
        # footnote and citation
        if (isinstance(node.parent, nodes.footnote)
            or isinstance(node.parent, nodes.citation)):
            raise nodes.SkipNode
        self.document.reporter.warning('"unsupported "label"',
                base_node=node)
        self.body.append('[')

    def depart_label(self, node):
        self.body.append(']\n')

    def visit_legend(self, node):
        pass

    def depart_legend(self, node):
        pass

    # WHAT should we use .INDENT, .UNINDENT ?
    def visit_line_block(self, node):
        self._line_block += 1
        if self._line_block == 1:
            # TODO: separate inline blocks from previous paragraphs
            # see http://hg.intevation.org/mercurial/crew/rev/9c142ed9c405
            # self.body.append('.sp\n')
            # but it does not work for me.
            self.body.append('.nf\n')
        else:
            self.body.append('.in +2\n')

    def depart_line_block(self, node):
        self._line_block -= 1
        if self._line_block == 0:
            self.body.append('.fi\n')
            self.body.append('.sp\n')
        else:
            self.body.append('.in -2\n')

    def visit_line(self, node):
        pass

    def depart_line(self, node):
        self.body.append('\n')

    def visit_list_item(self, node):
        self.body.append(self._list_char[-1].next() + node.astext())

    def depart_list_item(self, node):
        pass

    def visit_literal(self, node):
        self.body.append(self.defs['literal'][0])

    def depart_literal(self, node):
        self.body.append(self.defs['literal'][1])

    def visit_literal_block(self, node):
        # BUG/HACK: indent alway uses the _last_ indention,
        # thus we need two of them.
        self.indent(1)
        self.indent(0)

        names = False  # get reference if exists
        if 'names' in node and len(node['names']) > 0:
            names = node['names'][0]

        if 'linenos' in node and node['linenos']:
            if names:
                self.body.append('//listnum[{0}][{0}]{{\n'.format(names))
            else:
                self.body.append('//emlistnum{\n')
        else:
            if names:
                self.body.append('//list[{0}][{0}]{{\n'.format(names))
            else:
                self.body.append('//emlist{\n')
        self._in_literal = True

    def depart_literal_block(self, node):
        self._in_literal = False
        self.body.append('\n}\n')
        self.dedent()
        self.dedent()

    def visit_math(self, node):
        self.document.reporter.warning('"math" role not supported',
                base_node=node)
        self.visit_literal(node)

    def depart_math(self, node):
        self.depart_literal(node)

    def visit_math_block(self, node):
        self.document.reporter.warning('"math" directive not supported',
                base_node=node)
        self.visit_literal_block(node)

    def depart_math_block(self, node):
        self.depart_literal_block(node)

    def visit_meta(self, node):
        raise NotImplementedError, node.astext()

    def depart_meta(self, node):
        pass

    def visit_note(self, node):
        self.visit_admonition(node, 'note')

    depart_note = depart_admonition

    def indent(self, by=1):
        self._indent.append(by)

    def dedent(self):
        self._indent.pop()

    def visit_option_list(self, node):
        self.indent(1)

    def depart_option_list(self, node):
        self.dedent()

    def visit_option_list_item(self, node):
        # one item of the list
        self.body.append(self.defs['option_list_item'][0])

    def depart_option_list_item(self, node):
        self.body.append(self.defs['option_list_item'][1])

    def visit_option_group(self, node):
        # as one option could have several forms it is a group
        # options without parameter bold only, .B, -v
        # options with parameter bold italic, .BI, -f file
        #
        # we do not know if .B or .BI
        self.context.append('.B')           # blind guess
        self.context.append(len(self.body)) # to be able to insert later
        self.context.append(0)              # option counter

    def depart_option_group(self, node):
        self.context.pop()  # the counter
        start_position = self.context.pop()
        text = self.body[start_position:]
        del self.body[start_position:]
        self.body.append('%s%s\n' % (self.context.pop(), ''.join(text)))

    def visit_option(self, node):
        # each form of the option will be presented separately
        if self.context[-1] > 0:
            self.body.append(', ')
        if self.context[-3] == '.BI':
            self.body.append('\\')
        self.body.append(' ')

    def depart_option(self, node):
        self.context[-1] += 1

    def visit_option_string(self, node):
        # do not know if .B or .BI
        pass

    def depart_option_string(self, node):
        pass

    def visit_option_argument(self, node):
        self.context[-3] = '.BI' # bold/italic alternate
        if node['delimiter'] != ' ':
            self.body.append('\\fB%s ' % node['delimiter'])
        elif self.body[len(self.body)-1].endswith('='):
            # a blank only means no blank in output, just changing font
            self.body.append(' ')
        else:
            # blank backslash blank, switch font then a blank
            self.body.append(' \\ ')

    def depart_option_argument(self, node):
        pass


    def first_child(self, node):
        first = isinstance(node.parent[0], nodes.label) # skip label
        for child in node.parent.children[first:]:
            if isinstance(child, nodes.Invisible):
                continue
            if child is node:
                return 1
            break
        return 0

    def visit_paragraph(self, node):
        # ``.PP`` : Start standard indented paragraph.
        # ``.LP`` : Start block paragraph, all except the first.
        # ``.P [type]``  : Start paragraph type.
        # NOTE dont use paragraph starts because they reset indentation.
        # ``.sp`` is only vertical space
        self.ensure_eol()

    def depart_paragraph(self, node):
        self.body.append('\n')

    def visit_problematic(self, node):
        self.body.append(self.defs['problematic'][0])

    def depart_problematic(self, node):
        self.body.append(self.defs['problematic'][1])

    def visit_raw(self, node):
        if node.get('format') == 'manpage':
            self.body.append(node.astext() + "\n")
        # Keep non-manpage raw text out of output:
        raise nodes.SkipNode

    def visit_reference(self, node):
        """E.g. link or email address."""
        self.body.append('@<href>{')

    def depart_reference(self, node):
        self.body.append('}')


    def visit_row(self, node):
        self._active_table.new_row()

    def depart_row(self, node):
        pass

    def visit_section(self, node):
        self.section_level += 1

    def depart_section(self, node):
        self.section_level -= 1


    def visit_strong(self, node):
        self.body.append("@<b>{")

    def depart_strong(self, node):
        self.body.append("}")

    def visit_substitution_definition(self, node):
        """Internal only."""
        raise nodes.SkipNode

    def visit_substitution_reference(self, node):
        self.document.reporter.warning('"substitution_reference" not supported',
                base_node=node)

    def visit_subtitle(self, node):
        if isinstance(node.parent, nodes.sidebar):
            self.body.append(self.defs['strong'][0])
        elif isinstance(node.parent, nodes.document):
            self.visit_docinfo_item(node, 'subtitle')
        elif isinstance(node.parent, nodes.section):
            self.body.append(self.defs['strong'][0])

    def depart_subtitle(self, node):
        pass

    def visit_system_message(self, node):
        # TODO add report_level
        #if node['level'] < self.document.reporter['writer'].report_level:
        #    Level is too low to display:
        #    raise nodes.SkipNode
        attr = {}
        backref_text = ''
        if node.hasattr('id'):
            attr['name'] = node['id']
        if node.hasattr('line'):
            line = ', line %s' % node['line']
        else:
            line = ''
        self.body.append('.IP "System Message: %s/%s (%s:%s)"\n'
                         % (node['type'], node['level'], node['source'], line))

    def depart_system_message(self, node):
        pass

    def visit_table(self, node):
        self._active_table = Table()

    def depart_table(self, node):
        self.ensure_eol()
        self.body.extend(self._active_table.as_list())
        self._active_table = None

    def visit_target(self, node):
        # targets are in-document hyper targets, without any use for man-pages.
        raise nodes.SkipNode

    def visit_tbody(self, node):
        pass

    def depart_tbody(self, node):
        pass

    def visit_term(self, node):
        pass

    def depart_term(self, node):
        pass

    def visit_tgroup(self, node):
        pass

    def depart_tgroup(self, node):
        pass

    def visit_thead(self, node):
        # MAYBE double line '='
        pass

    def depart_thead(self, node):
        # MAYBE double line '='
        pass

    def visit_tip(self, node):
        self.visit_admonition(node, 'tip')

    depart_tip = depart_admonition

    def visit_title(self, node):
        pre = ('=' * self.section_level) + ' '
        self.body.append(pre + node.astext())
        self.body.append('\n')

        raise nodes.SkipNode

    def depart_title(self, node):
        if isinstance(node.parent, nodes.admonition):
            self.body.append('"')
        self.body.append('\n')

    def visit_title_reference(self, node):
        """inline citation reference"""
        self.body.append('@<code>{')

    def depart_title_reference(self, node):
        self.body.append('}')

    def visit_topic(self, node):
        pass

    def depart_topic(self, node):
        pass

    def visit_sidebar(self, node):
        pass

    def depart_sidebar(self, node):
        pass

    def visit_rubric(self, node):
        pass

    def depart_rubric(self, node):
        pass

    def visit_transition(self, node):
        pass

    def depart_transition(self, node):
        pass

    def visit_warning(self, node):
        self.visit_admonition(node, 'warning')

    depart_warning = depart_admonition

    def visit_compact_paragraph(self, node):
        pass
    def depart_compact_paragraph(self, node):
        pass

    def unimplemented_visit(self, node):
        raise NotImplementedError('visiting unimplemented node type: %s'
                                  % node.__class__.__name__)
