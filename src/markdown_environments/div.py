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

    def __init__(self, *args, html_class: str, types: dict, use_thm_counter: bool, use_thm_headings: bool, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_html_class(html_class)
        self.init_thm(types, use_thm_counter, use_thm_headings)

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
    def __init__(self, **kwargs):
        self.config = {
            "html_class": [
                "",
                "HTML `class` attribute to add to div (default: `\"\"`)."
            ],
            "types": [
                {},
                "Types of div environments to define (default: `{}`)."
            ],
            "use_thm_counter": [
                False,
                "Whether to add theorem counters to div contents; mostly for `ThmExtension` (default: `False`)."
            ],
            "use_thm_headings": [
                False,
                "Whether to add theorem headings to div contents; mostly for `ThmExtension` (default: `False`)."
            ]
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(Div(md.parser, **self.getConfigs()), "div", 105)


def makeExtension(**kwargs):
    return DivExtension(**kwargs)
