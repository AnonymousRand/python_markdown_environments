import re
import xml.etree.ElementTree as etree

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension

from . import util


class DivProcessor(BlockProcessor):

    def __init__(self, *args, types: dict, html_class: str, is_thm: bool, **kwargs):
        super().__init__(*args, **kwargs)
        self.html_class = html_class
        self.is_thm = is_thm
        self.types, self.start_regex_choices, self.end_regex_choices = util.init_env_types(types, self.is_thm)
        self.start_regex = None
        self.end_regex = None

    def test(self, parent, block):
        typ = util.test_for_env_types(self.start_regex_choices, parent, block)
        if typ is None:
            return False
        self.type_opts = self.types[typ]
        self.start_regex = self.start_regex_choices[typ]
        self.end_regex = self.end_regex_choices[typ]
        return True

    def run(self, parent, blocks):
        org_block_start = blocks[0]
        # generate default thm heading if applicable
        thm_heading_md = ""
        if self.is_thm:
            thm_heading_md = util.gen_thm_heading_md(self.type_opts, self.start_regex, blocks[0])
        # remove starting delim (after generating thm heading from it, if applicable)
        blocks[0] = re.sub(self.start_regex, "", blocks[0], flags=re.MULTILINE)

        # find and remove ending delim, and extract element
        delim_found = False
        for i, block in enumerate(blocks):
            if re.search(self.end_regex, block, flags=re.MULTILINE):
                delim_found = True
                # remove ending delim
                blocks[i] = re.sub(self.end_regex, "", block, flags=re.MULTILINE)
                # build HTML
                elem = etree.SubElement(parent, "div")
                if self.html_class != "" or self.type_opts.get("html_class") != "":
                    elem.set("class", f"{self.html_class} {self.type_opts.get('html_class')}")
                self.parser.parseBlocks(elem, blocks[0:i + 1])
                # remove used blocks
                for _ in range(0, i + 1):
                    blocks.pop(0)
                # add thm heading if applicable
                util.prepend_thm_heading_md(self.type_opts, elem, thm_heading_md)
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

        becomes…

        .. code-block:: html

            <div class="[html_class] [type's html_class]">
              [content]
            </div>
    """

    def __init__(self, **kwargs):
        r"""
        Initialize div extension, with configuration options passed as the following keyword arguments:

            - **types** (*dict*) -- Types of div environments to define. Defaults to `{}`.
            - **html_class** (*str*) -- HTML `class` attribute to add to divs. Defaults to `""`.

        The key for each type defined in `types` is inserted directly into the regex patterns that search for
        `\\begin{<type>}` and `\\end{<type>}`, so anything you specify will be interpreted as regex. In addition, each
        type's value is itself a dictionary with the following possible options:

            - **html_class** (*str*) -- HTML `class` attribute to add to divs of that type. Defaults to `""`.
        """

        self.config = {
            "types": [
                {},
                "Types of div environments to define. Defaults to `{}`."
            ],
            "html_class": [
                "",
                "HTML `class` attribute to add to div. Defaults to `\"\"`."
            ],
            "is_thm": [
                False,
                (
                    "Whether to use theorem logic (e.g. heading); you shouldn't have to set this value."
                    "Defaults to `False`."
                )
            ]
        }
        util.init_extension_with_configs(self, **kwargs)

        # set default options for individual types
        for type, opts in self.getConfig("types").items():
            opts.setdefault("html_class", "")

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(DivProcessor(md.parser, **self.getConfigs()), "div", 105)


def makeExtension(**kwargs):
    return DivExtension(**kwargs)
