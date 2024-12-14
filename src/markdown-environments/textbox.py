import re
import xml.etree.ElementTree as etree
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor


class Textbox(BlockProcessor):
    """
    A textbox.

    Usage:
        ```

        \begin{<type>}
        
        <content>

        \end{<type>}

        ```
        - HTML output:
            ```
            <div class="md-textbox md-textbox--[type] last-child-no-mb">
              [content]
            </div>
            ```
    """

    def __init__(self, *args, types: dict, html_class: str="", use_math_counter: bool=False,
            use_math_thm_heading: bool=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.types = types
        self.html_class = html_class
        self.use_math_counter = use_math_counter
        self.use_math_thm_heading = use_math_thm_heading
        self.re_start = None
        self.re_end = None
        self.type_opts = None

        # init regex patterns
        self.re_start_choices = {}
        self.re_end_choices = {}
        for typ in self.types:
            if self.use_math_thm_heading:
                self.re_start_choices[typ] = rf"^\\begin{{{typ}}}(?:\[(.+?)\])?(?:{{(.+?)}})?"
            else:
                self.re_start_choices[typ] = rf"^\\begin{{{typ}}}"
            self.re_end_choices[typ] = rf"^\\end{{{typ}}}"

    def gen_auto_prepend(self, block: str) -> str:
        prepend = self.type_opts.get("name")
        if prepend is None:
            return ""

        re_start_match = re.match(self.re_start, block, re.MULTILINE)
        # override theorem heading with theorem name first if applicable
        if self.use_math_thm_heading:
            if self.type_opts.get("overrides_heading") and re_start_match.group(1) is not None:
                prepend = re_start_match.group(1)
        # fill in math counter by using my `counter` extension's syntax
        if self.use_math_counter:
            counter = self.type_opts.get("counter")
            if counter is not None:
                prepend += f" {{{{{counter}}}}}"
        # fill in math theorem heading by using my `thm_heading` extension's syntax
        if self.use_math_thm_heading:
            prepend = "{[" + prepend + "]}"
            if not self.type_opts.get("overrides_heading") and re_start_match.group(1) is not None:
                prepend += "[" + re_start_match.group(1) + "]"
            if re_start_match.group(2) is not None:
                prepend += "{" + re_start_match.group(2) + "}"
        return prepend

    def do_auto_prepend(self, elem: etree.Element, prepend: str) -> None:
        if not prepend:
            return

        # add to first paragraph child if it exists to let it be on the same line to minimize weird
        # CSS `display: inline` or whatever chaos
        elem_to_prepend_into = None
        first_p = elem.find("p")
        if first_p is not None:
            elem_to_prepend_into = first_p
        else:
            elem_to_prepend_into = elem

        if elem_to_prepend_into.text is not None:
            elem_to_prepend_into.text = f"{prepend}{self.type_opts.get('punct')} {elem_to_prepend_into.text}"
        else:
            if self.type_opts.get("use_punct_if_nameless"):
                elem_to_prepend_into.text = f"{prepend}{self.type_opts.get('punct')}"
            else:
                elem_to_prepend_into.text = prepend

    def test(self, parent, block):
        for typ, regex in self.re_start_choices.items():
            if re.match(regex, block, re.MULTILINE):
                self.type_opts = self.types[typ]
                self.re_start = regex
                self.re_end = self.re_end_choices[typ]
                return True
        return False

    def run(self, parent, blocks):
        org_block_start = blocks[0]
        # generate default prepended text if applicable
        prepend = self.gen_auto_prepend(blocks[0])
        # remove starting delimiter (after generating prepended text from it, if applicable)
        blocks[0] = re.sub(self.re_start, "", blocks[0], flags=re.MULTILINE)

        # find and remove ending delimiter, and extract element
        elem = etree.SubElement(parent, "div")
        elem.set("class", f"{self.html_class} {self.type_opts.get('html_class')}")
        ending_delim_found = False
        for i, block in enumerate(blocks):
            if re.search(self.re_end, block, flags=re.MULTILINE):
                ending_delim_found = True
                # remove ending delimiter
                blocks[i] = re.sub(self.re_end, "", block, flags=re.MULTILINE)
                # build HTML
                self.parser.parseBlocks(elem, blocks[0:i + 1])
                # remove used blocks
                for _ in range(0, i + 1):
                    blocks.pop(0)
                break
        # if no ending delimiter, restore and do nothing
        if not ending_delim_found:
            blocks[0] = org_block_start
            return False

        # add prepended text if applicable
        self.do_auto_prepend(elem, prepend)
        return True


class TextboxExtension(Extension):
    def extendMarkdown(self, md):
        types = {
            "textbox": {"html_class": "md-dropdown--default"}
        }
        md.parser.blockprocessors.register(
                Textbox(md.parser, types=types, html_class="md-textbox last-child-no-mb"),
                "textbox", 105)


def makeExtension(**kwargs):
    return TextboxExtension(**kwargs)
