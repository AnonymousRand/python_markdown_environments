import re
import xml.etree.ElementTree as etree
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor

# TODO: conditional import depending on user config (like if user config includes dropdown, import dropdown)?
from app.markdown_extensions.dropdown import Dropdown
from app.markdown_extensions.mixins import HtmlClassMixin, ThmMixin, TypesMixin
from app.markdown_extensions.div import Div


class ThmHeading(InlineProcessor):
    """
    A theorem heading that allows you to add custom styling and can generate linkable HTML `id`s.

    Usage:
        ```
        {[<theorem_heading>]}[<optional_theorem_name>][[<optional_hidden_theorem_name>]]
        ```
        - HTML output:
            ```
            <span id="[optional_theorem_name/optional_hidden_theorem_name]" class="md-thm-heading">
              [theorem_heading]
            </span>
            [optional_theorem_name]
            ```
        - `<optional_hidden_theorem_name>` only adds an HTML `id`, and is not displayed. It is ignored if
          `<optional_theorem_name>` is provided.
    """

    def handleMatch(self, m, current_text_block):
        def format_for_html(s: str) -> str:
            s = ("-".join(s.split())).lower() 
            s = s[:-1].replace(".", "-") + s[-1] # replace periods except if trailing with hyphens (for thm counter)
            s = re.sub(r"[^A-Za-z0-9-]", r"", s)
            return s

        elem = etree.Element("span")
        elem.set("class", "md-thm-heading")
        elem_heading = etree.SubElement(elem, "span")
        elem_heading.set("class", "md-thm-heading__heading")
        elem_heading.text = f"{m.group(1)}"
        if m.group(2) is not None:
            elem_non_heading = etree.SubElement(elem, "span")
            elem_non_heading.text = f" ({m.group(2)})"
            elem.set("id", format_for_html(m.group(2)))
        elif m.group(3) is not None:
            elem.set("id", format_for_html(m.group(3)))
        return elem, m.start(0), m.end(0)


class ThmsExtension(Extension):
    def extendMarkdown(self, md):
        regex = r"{\[(.+?)\]}(?:\[(.+?)\])?(?:{(.+?)})?"
        md.inlinePatterns.register(ThmHeading(regex, md), "thm_heading", 105)

        # TODO: these need to be passed in via extension config
        # TODO:: test without math counter/thm heading (set to False)
        div_types = {
            "coro": {
                "name": "Corollary",
                "html_class": "md-textbox md-textbox--coro last-child-no-mb",
                "counter": "0,0,1"
            },
            "defn": {
                "name": "Definition",
                "html_class": "md-textbox md-textbox--defn last-child-no-mb",
                "counter": "0,0,1"
            },
            r"defn\\\*": {
                "name": "Definition",
                "html_class": "md-textbox md-textbox--defn last-child-no-mb"
            },
            "ex": {
                "name": "Example",
                "html_class": "md-div--ex"
            },
            r"notat\\\*": {
                "name": "Notation",
                "html_class": "md-textbox md-textbox--notat last-child-no-mb"
            },
            "prop": {
                "name": "Proposition",
                "html_class": "md-textbox md-textbox--prop last-child-no-mb",
                "counter": "0,0,1"
            },
            "thm": {
                "name": "Theorem",
                "html_class": "md-textbox md-textbox--thm last-child-no-mb",
                "counter": "0,0,1"
            },
            r"thm\\\*": {
                "name": "Theorem",
                "html_class": "md-textbox md-textbox--thm last-child-no-mb"
            }
        }
        dropdown_types = {
            "exer": {
                "name": "Exercise",
                "html_class": "md-dropdown--exer",
                "counter": "0,0,1",
                "use_punct_if_nameless": False
            },
            "pf": {
                "name": "Proof",
                "html_class": "md-dropdown--pf",
                "overrides_heading": True,
                "use_punct_if_nameless": False
            },
            r"rmk\\\*": {
                "name": "Remark",
                "html_class": "md-dropdown--rmk",
                "overrides_heading": True,
                "use_punct_if_nameless": False
            }
        }
        # set default values for dicts
        for d in [dropdown_types, div_types]:
            for type_opts in d.values():
                type_opts.setdefault("name", "")
                type_opts.setdefault("html_class", "")
                type_opts.setdefault("counter", None)
                type_opts.setdefault("overrides_heading", False)
                type_opts.setdefault("punct", ".")
                type_opts.setdefault("use_punct_if_nameless", True)

        md.parser.blockprocessors.register(
                Div(md.parser, types=div_types, html_class="md-div", use_math_counter=True,
                        use_math_thm_heading=True),
                "thms_div", 105)
        md.parser.blockprocessors.register(
                Dropdown(md.parser, types=dropdown_types, html_class="md-dropdown",
                        summary_html_class="md-dropdown__summary last-child-no-mb",
                        content_html_class="md-dropdown__content last-child-no-mb",
                        use_math_counter=True, use_math_thm_heading=True),
                "thms_dropdown", 999)


def makeExtension(**kwargs):
    return ThmsExtension(**kwargs)
