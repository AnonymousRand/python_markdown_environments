import re
import xml.etree.ElementTree as etree
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension

from .mixins import HtmlClassMixin, ThmMixin


class Div(BlockProcessor, HtmlClassMixin, ThmMixin):
    """
    A general-purpose `<div>`.

    Usage:
        ```

        \begin{<type>}
        <content>
        \end{<type>}

        ```
        - HTML output:
            ```
            <div class="[html_class] [types[type]['html_class']]">
              [content]
            </div>
            ```
    """

    def __init__(self, *args, types: dict, html_class: str="", use_math_counter: bool=False,
            use_math_thm_heading: bool=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_html_class(html_class)
        self.init_thm(types, use_math_counter, use_math_thm_heading)

    def test(self, parent, block):
        return ThmMixin.test(self, parent, block)

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


class DivExtension(Extension):
    def extendMarkdown(self, md):
        types = {
            "textbox": {"html_class": "md-textbox md-textbox-default last-child-no-mb"}
        }
        md.parser.blockprocessors.register(Div(md.parser, types=types, html_class="md-div"), "div", 105)


def makeExtension(**kwargs):
    return DivExtension(**kwargs)
