import re
import xml.etree.ElementTree as etree
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor


class Dropdown(BlockProcessor):
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
            <details class="md-dropdown md-dropdown--[type]">
              <summary class="md-dropdown__summary last-child-no-mb">
                [summary]
              </summary>
              <div class="md-dropdown__content last-child-no-mb">
                [collapsible content]
              </div>
            </details>
            ```
    """

    RE_SUMMARY_START = r"^\\begin{summary}"
    RE_SUMMARY_END = r"^\\end{summary}"

    def __init__(self, *args, types: dict, html_class: str="", summary_html_class: str="", content_html_class: str="",
            use_math_counter: bool=False, use_math_thm_heading: bool=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.types = types
        self.html_class = html_class
        self.summary_html_class = summary_html_class
        self.content_html_class = content_html_class
        self.use_math_counter = use_math_counter
        self.use_math_thm_heading = use_math_thm_heading
        self.re_dropdown_start = None
        self.re_dropdown_end = None
        self.type_opts = None

        # init regex patterns
        self.re_dropdown_start_choices = {}
        self.re_dropdown_end_choices = {}
        for typ in self.types:
            if self.use_math_thm_heading:
                self.re_dropdown_start_choices[typ] = rf"^\\begin{{{typ}}}(?:\[(.+?)\])?(?:{{(.+?)}})?"
            else:
                self.re_dropdown_start_choices[typ] = rf"^\\begin{{{typ}}}"
            self.re_dropdown_end_choices[typ] = rf"^\\end{{{typ}}}"
    
    # TODO: way too much shared code here; somehow put this in thms.py instead?
    def gen_auto_prepend(self, block: str) -> str:
        summary_prepend = self.type_opts.get("name")
        if summary_prepend == "":
            return ""

        re_dropdown_start_match = re.match(self.re_dropdown_start, block, re.MULTILINE)
        # override theorem heading with theorem name first if applicable
        if self.use_math_thm_heading:
            if self.type_opts.get("overrides_heading") and re_dropdown_start_match.group(1) is not None:
                summary_prepend = re_dropdown_start_match.group(1)
        # fill in math counter by using my `counter` extension's syntax
        if self.use_math_counter:
            counter = self.type_opts.get("counter")
            if counter is not None:
                summary_prepend += f" {{{{{counter}}}}}"
        # fill in math theorem heading by using my `thm_heading` extension's syntax
        if self.use_math_thm_heading:
            summary_prepend = "{[" + summary_prepend + "]}"
            if not self.type_opts.get("overrides_heading") and re_dropdown_start_match.group(1) is not None:
                summary_prepend += "[" + re_dropdown_start_match.group(1) + "]"
            if re_dropdown_start_match.group(2) is not None:
                summary_prepend += "{" + re_dropdown_start_match.group(2) + "}"
        return summary_prepend

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
        for typ, regex in self.re_dropdown_start_choices.items():
            if re.match(regex, block, re.MULTILINE):
                self.type_opts = self.types[typ]
                self.re_dropdown_start = regex
                self.re_dropdown_end = self.re_dropdown_end_choices[typ]
                return True
        return False

    def run(self, parent, blocks):
        org_blocks = list(blocks)
        # remove summary starting delimiter that must immediately follow dropdown's starting delimiter
        # if no starting delimiter for summary and no default, restore and do nothing
        if not re.match(self.RE_SUMMARY_START, blocks[1], re.MULTILINE):
            if self.type_opts.get("name") is None:
                blocks.clear() # `blocks = org_blocks` doesn't work because that just reassigns function-scoped `blocks`
                blocks.extend(org_blocks)
                return False
        blocks[1] = re.sub(self.RE_SUMMARY_START, "", blocks[1], flags=re.MULTILINE)

        # generate default prepended summary text if applicable
        summary_prepend = self.gen_auto_prepend(blocks[0])
        # remove dropdown starting delimiter (after generated prepended text from it, if applicable)
        blocks[0] = re.sub(self.re_dropdown_start, "", blocks[0], flags=re.MULTILINE)

        # find and remove summary ending delimiter, and extract element
        elem_summary = etree.Element("summary")
        elem_summary.set("class", self.summary_html_class)
        has_valid_summary = self.type_opts.get("name") is not None
        for i, block in enumerate(blocks):
            # if we haven't found summary ending delimiter but have found the overall dropdown ending delimiter,
            # then don't keep going; maybe the summary was omitted since it could've been optional
            if re.search(self.re_dropdown_end, block, flags=re.MULTILINE):
                break
            if re.search(self.RE_SUMMARY_END, block, flags=re.MULTILINE):
                has_valid_summary = True
                # remove ending delimiter
                blocks[i] = re.sub(self.RE_SUMMARY_END, "", block, flags=re.MULTILINE)
                # build HTML for summary
                self.parser.parseBlocks(elem_summary, blocks[:i + 1])
                # remove used blocks
                for _ in range(i + 1):
                    blocks.pop(0)
                break
        # if no valid summary (e.g. no ending delimiter with no default), restore and do nothing
        if not has_valid_summary:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # add prepended text (add to first paragraph child if it exists to let it be on the same line
        # to minimize weird CSS `display: inline` or whatever quirks)
        self.do_auto_prepend(elem_summary, summary_prepend)

        # find and remove dropdown ending delimiter, and extract element
        for i, block in enumerate(blocks):
            if re.search(self.re_dropdown_end, block, flags=re.MULTILINE):
                # remove ending delimiter
                blocks[i] = re.sub(self.re_dropdown_end, "", block, flags=re.MULTILINE)
                # build HTML for dropdown
                elem_details = etree.SubElement(parent, "details")
                elem_details.set("class", f"{self.html_class} {self.type_opts.get('html_class')}")
                elem_details.append(elem_summary)
                elem_details_content = etree.SubElement(elem_details, "div")
                elem_details_content.set("class", self.content_html_class)
                self.parser.parseBlocks(elem_details_content, blocks[0:i + 1])
                # remove used blocks
                for _ in range(0, i + 1):
                    blocks.pop(0)
                return True
        # if no ending delimiter for dropdown, restore and do nothing
        blocks.clear()
        blocks.extend(org_blocks)
        return False


class DropdownExtension(Extension):
    def extendMarkdown(self, md):
        types = {
            "dropdown": {"html_class": "md-dropdown--default"}
        }
        md.parser.blockprocessors.register(
                Dropdown(md.parser, types=types, html_class="md-dropdown",
                        summary_html_class="md-dropdown__summary last-child-no-mb",
                        content_html_class="md-dropdown__content last-child-no-mb"),
                "dropdown", 105)


def makeExtension(**kwargs):
    return DropdownExtension(**kwargs)
