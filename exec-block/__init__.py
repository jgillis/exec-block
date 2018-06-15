import os
from docutils.parsers.rst import Directive, directives

from sphinx.writers.latex import LaTeXTranslator
from sphinx.util.nodes import set_source_info

from docutils import nodes
import hashlib
from collections import defaultdict

class ExecBlockAddHeaderDirective(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    headers = defaultdict(list)

    def run(self):
      lang = self.arguments[0]
      if self.content not in self.headers[lang]:
        self.headers[lang].extend(self.content)

      return []
      

class ExecBlockAddFilterDirective(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    filters = set()

    def run(self):
      self.filters.add("\n".join(self.content))
      return []

    @classmethod
    def filter(cl,data):
      for f in cl.filters:
        data = data.replace(f,"")
      return data


def remove_leading_empty_lines(lines):
    if isinstance(lines,str):
      lines = lines.split("\n")
    offset = 0
    for i,L in enumerate(lines):
      if len(L.rstrip())==0:
        offset = i+1
      else:
        break
    
    return u'\n'.join(lines[offset:])

class ExecBlockDirective(Directive):
    """
    Directive for a code block with special highlighting or line numbering
    settings.
    """

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'linenos': directives.flag,
        'dedent': int,
        'lineno-start': int,
        'emphasize-lines': directives.unchanged_required,
        'caption': directives.unchanged_required,
        'class': directives.class_option,
        'name': directives.unchanged,
        'hide-output': bool
    }
    input_hidden = False

    def run(self):
        # type: () -> List[nodes.Node]
        document = self.state.document
        lang = self.arguments[0]


        visible_code_lines = [i for i in self.content if " [hidden]" not in i]


        visible_code = remove_leading_empty_lines(visible_code_lines)

        all_code = u'\n'.join([i.replace(" [hidden]","") for i in self.content])
        
        full_code = u'\n'.join(ExecBlockAddHeaderDirective.headers[lang]+[all_code])
        location = self.state_machine.get_source_and_line(self.lineno)

        linespec = self.options.get('emphasize-lines')
        if linespec:
            try:
                nlines = len(self.content)
                hl_lines = parselinenos(linespec, nlines)
                if any(i >= nlines for i in hl_lines):
                    logger.warning('line number spec is out of range(1-%d): %r' %
                                   (nlines, self.options['emphasize-lines']),
                                   location=location)

                hl_lines = [x + 1 for x in hl_lines if x < nlines]
            except ValueError as err:
                return [document.reporter.warning(str(err), line=self.lineno)]
        else:
            hl_lines = None

        if 'dedent' in self.options:
            location = self.state_machine.get_source_and_line(self.lineno)
            lines = visible_code.split('\n')
            lines = dedent_lines(lines, self.options['dedent'], location=location)
            visible_code = '\n'.join(lines)

        if not self.input_hidden:
          literal = nodes.literal_block(visible_code, visible_code)
          literal['language'] = lang
          literal['linenos'] = 'linenos' in self.options or \
                               'lineno-start' in self.options
          literal['classes'] += self.options.get('class', [])
          extra_args = literal['highlight_args'] = {}
          if hl_lines is not None:
              extra_args['hl_lines'] = hl_lines
          if 'lineno-start' in self.options:
              extra_args['linenostart'] = self.options['lineno-start']
          set_source_info(self, literal)

          caption = self.options.get('caption')
          if caption:
              try:
                  literal = container_wrapper(self, literal, caption)
              except ValueError as exc:
                  return [document.reporter.warning(str(exc), line=self.lineno)]

          # literal will be note_implicit_target that is linked from caption and numref.
          # when options['name'] is provided, it should be primary ID.
          self.add_name(literal)

        m = hashlib.sha256()
        m.update(full_code.encode('utf-8'))
        path = "snippets"
        if not os.path.exists(path):
          os.mkdir("snippets")

        file_prefix = m.hexdigest()
        with open(os.path.join(path,file_prefix+"."+ lang+".in"),"w") as f:
          f.write(full_code)

        try:
          with open(os.path.join(path,file_prefix+"."+ lang+".out"),"r") as f:
            output_text = f.read()
        except:
          output_text = "(Output not available)"


        

        output_hidden = len(output_text.rstrip())==0

        output_text = ExecBlockAddFilterDirective.filter(output_text)


        output_text = remove_leading_empty_lines(output_text)

        output = nodes.literal_block(output_text,output_text)
        output["language"] = "none"
        output['classes'].append("exec-block-output")

        ret = []
        if not self.input_hidden:
          ret.append(literal)
        if not output_hidden:
          ret.append(output)

        return ret

class OutputExecBlockDirective(ExecBlockDirective):
    input_hidden = True


def setup(app):
    app.add_directive('exec-block',  ExecBlockDirective)
    app.add_directive('output-block',  OutputExecBlockDirective)
    app.add_directive('exec-block-add-header',  ExecBlockAddHeaderDirective)
    app.add_directive('exec-block-add-filter',  ExecBlockAddFilterDirective)
