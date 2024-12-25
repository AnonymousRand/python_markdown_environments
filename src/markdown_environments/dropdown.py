import re
import xml.etree.ElementTree as etree
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension

from . import util
from .mixins import HtmlClassMixin, ThmMixin


class Dropdown(BlockProcessor, HtmlClassMixin, ThmMixin):
    """
    A dropdown that can be toggled open or closed, with only a summary (preview) portion shown when closed.

    Usage:
        ```

        \begin{<type>}

        \begin{summary}
        <summary>
        \end{summary}

        <collapsible content>
        \end{<type>}

        ```
        - HTML output:
            ```
            <details class="[html_class] [types[type][html_class]]">
              <summary class="[summary_html_class]">
                [summary]
              </summary>
              <div class="[content_html_class]">
                [collapsible content]
              </div>
            </details>
            ```
    """

    RE_SUMMARY_START = r"^\\begin{summary}"
    RE_SUMMARY_END = r"^\\end{summary}"

    def __init__(self, *args, html_class: str, summary_html_class: str, content_html_class: str, types: dict,
            is_thm: bool, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_html_class(html_class)
        self.init_thm(types, is_thm)
        self.summary_html_class = summary_html_class
        self.content_html_class = content_html_class

    def test(self, parent, block):
        return ThmMixin.test(self, parent, block)

    def run(self, parent, blocks):
        org_blocks = list(blocks)
        # remove summary starting delim that must immediately follow dropdown's starting delim
        # if no starting delim for summary and not a thm dropdown which should provide a default, restore and do nothing
        if not self.is_thm and not re.match(self.RE_SUMMARY_START, blocks[1], re.MULTILINE):
            blocks.clear() # `blocks = org_blocks` doesn't work because that just reassigns function-scoped `blocks`
            blocks.extend(org_blocks)
            return False
        blocks[1] = re.sub(self.RE_SUMMARY_START, "", blocks[1], flags=re.MULTILINE)

        # generate theorem heading to use as default summary text if applicable
        summary_prepend = self.gen_thm_heading(blocks[0])
        # remove dropdown starting delim (after generating thm heading from it if applicable)
        blocks[0] = re.sub(self.re_start, "", blocks[0], flags=re.MULTILINE)

        # find and remove summary ending delim, and extract element
        has_valid_summary = self.is_thm
        for i, block in enumerate(blocks):
            # if we haven't found summary ending delim but have found the overall dropdown ending delim,
            # then don't keep going; maybe the summary was omitted since it could've been optional
            if re.search(self.re_end, block, flags=re.MULTILINE):
                break
            if re.search(self.RE_SUMMARY_END, block, flags=re.MULTILINE):
                has_valid_summary = True
                # remove ending delim
                blocks[i] = re.sub(self.RE_SUMMARY_END, "", block, flags=re.MULTILINE)
                # build HTML for summary
                elem_summary = etree.Element("summary")
                if self.summary_html_class != "":
                    elem_summary.set("class", self.summary_html_class)
                self.parser.parseBlocks(elem_summary, blocks[:i + 1])
                # add thm heading to summary if applicable
                self.prepend_thm_heading(elem_summary, summary_prepend)
                # remove used blocks
                for _ in range(i + 1):
                    blocks.pop(0)
                break
        # if no valid summary (e.g. no ending delim with no default), restore and do nothing
        if not has_valid_summary:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove dropdown ending delim, and extract element
        delim_found = False
        for i, block in enumerate(blocks):
            if re.search(self.re_end, block, flags=re.MULTILINE):
                delim_found = True
                # remove ending delim
                blocks[i] = re.sub(self.re_end, "", block, flags=re.MULTILINE)
                # build HTML for dropdown
                elem_details = etree.SubElement(parent, "details")
                if self.html_class != "" or self.type_opts.get("html_class") != "":
                    elem_details.set("class", f"{self.html_class} {self.type_opts.get('html_class')}")
                elem_details.append(elem_summary)
                elem_details_content = etree.SubElement(elem_details, "div")
                if self.content_html_class != "":
                    elem_details_content.set("class", self.content_html_class)
                self.parser.parseBlocks(elem_details_content, blocks[0:i + 1])
                # remove used blocks
                for _ in range(0, i + 1):
                    blocks.pop(0)
                break
        # if no ending delim for dropdown, restore and do nothing
        if not delim_found:
            blocks.clear()
            blocks.extend(org_blocks)
            return False
        return True


class DropdownExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            "html_class": [
                "",
                "HTML `class` attribute to add to dropdown (default: `\"\"`)."
            ],
            "summary_html_class": [
                "",
                "HTML `class` attribute to add to dropdown summary (default: `\"\"`)."
            ],
            "content_html_class": [
                "",
                "HTML `class` attribute to add to dropdown content (default: `\"\"`)."
            ],
            "types": [
                {},
                "Types of dropdown environments to define (default: `{}`)."
            ],
            "is_thm": [
                False,
                "Whether to use theorem logic (e.g. heading); used only by `ThmExtension` (default: `False`)."
            ]
        }
        util.init_extension_with_configs(self, **kwargs)

        # set default options for individual types
        for type, opts in self.getConfig("types").items():
            opts.setdefault("html_class", "")

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(Dropdown(md.parser, **self.getConfigs()), "dropdown", 105)


def makeExtension(**kwargs):
    return DropdownExtension(**kwargs)
