import re
import xml.etree.ElementTree as etree

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension

from . import utils
from .thms_impls_base import ThmsImplsBase


class DivProcessor(BlockProcessor, ThmsImplsBase):

    def __init__(self, *args, types: dict, html_class: str, is_thm: bool, **kwargs):
        BlockProcessor.__init__(self, *args, **kwargs)
        ThmsImplsBase.__init__(self, types=types, is_thm=is_thm);
        self.html_class = html_class

    # this is technically not required, but it makes the multiple inheritance situation (where
    # `ThmsImplsBase` is implementing this method required for `BlockProcessor`s) more explicit
    def test(self, parent, block):
        return ThmsImplsBase.test(self, parent, block)

    def run(self, parent, blocks):
        org_block_start = blocks[0]
        # generate default thm heading if applicable
        thm_heading_md = ""
        if self.is_thm:
            thm_heading_md = self.gen_thm_heading_md(blocks[0])
        # remove starting delim (after generating thm heading from it, if applicable)
        blocks[0] = self.start_pattern.sub("", blocks[0])

        # find and remove ending delim, and extract element
        delim_found = False
        for i, block in enumerate(blocks):
            if self.end_pattern.search(block):
                delim_found = True
                # remove ending delim
                blocks[i] = self.end_pattern.sub("", block)
                # build HTML
                elem = etree.SubElement(parent, "div")
                if self.html_class != "" or self.type_opts.get("html_class") != "":
                    elem.set("class", f"{self.html_class} {self.type_opts.get('html_class')}")
                blocks[i] = blocks[i].rstrip() # remove whitespace from newline after `\end{}`
                self.parser.parseBlocks(elem, blocks[0:i + 1])
                # remove used blocks
                for _ in range(0, i + 1):
                    blocks.pop(0)
                # add thm heading if applicable
                ThmsImplsBase.prepend_thm_heading_md(elem, thm_heading_md)
                break
        # if no ending delim, restore and do nothing
        if not delim_found:
            blocks[0] = org_block_start
            return False
        return True


class DivExtension(Extension):
    r"""
    A general-purpose `<div>` that you can tack on HTML `class` es to.

    Usage:
        .. code-block:: py

            import markdown
            from markdown_environments import DivExtension

            input_text = ...
            output_text = markdown.markdown(input_text, extensions=[
                DivExtension(html_class="up", types={
                    type1: {},
                    type2: {"html_class": "never"}
                })
            ])

    Markdown usage:
        .. code-block:: md

            \begin{<type>}
            <content>
            \end{<type>}

        becomes:

        .. code-block:: html

            <div class="[html_class] [type.html_class]">
              [content]
            </div>
    """

    def __init__(self, **kwargs):
        r"""
        Initialize div extension, with configuration options passed as the following keyword
        arguments:

            - **types** (*dict*) -- Types of div environments to define. Defaults to `{}`.
            - **html_class** (*str*) -- HTML `class` attribute to add to all divs. Defaults to `""`.

        The key for each type defined in `types` is inserted directly into the regex patterns
        that search for `\\begin{<type>}` and `\\end{<type>}`, so anything you specify will be
        interpreted as regex. (However, if the key is an empty string, its regex will never be
        matched against, so it is effectively useless.)

        In addition, each type's value is itself a dictionary with the following possible options:

            - **html_class** (*str*) -- HTML `class` attribute to add to divs of that type.
              Defaults to `""`.
        """

        self.config = {
            "types": [
                {},
                "Types of div environments to define. Defaults to `{}`."
            ],
            "html_class": [
                "",
                "HTML `class` attribute to add to all divs. Defaults to `\"\"`."
            ],
            "is_thm": [
                False,
                (
                    "Whether to use theorem logic (e.g. heading); you shouldn't have to set "
                    "this value manually. Defaults to `False`."
                )
            ]
        }
        utils.init_extension_with_configs(self, **kwargs)

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(DivProcessor(md.parser, **self.getConfigs()), "div", 105)


def makeExtension(**kwargs):
    return DivExtension(**kwargs)
