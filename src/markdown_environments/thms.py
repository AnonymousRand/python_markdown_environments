import re
import xml.etree.ElementTree as etree
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.treeprocessors import Treeprocessor

from .mixins import HtmlClassMixin

# TODO: conditional import depending on user config (like if user config includes dropdown, import dropdown)?
from .dropdown import Dropdown
from .div import Div


# TODO: if releasing Counter, test with no adding html/varied params, also linking to counter via URL fragment

# the only reason this is a `Treeprocessor` and not a `Preprocessor`, `InlineProcessor`, or `Postprocessor`, all of
# which make more sense, is because we need this to run after `thms` (`BlockProcessor`) and before the TOC extension
# (`Treeprocessor` with low priority): `thms` generates `counter` syntax, while TOC will duplicate unparsed
# `counter` syntax from headings into the TOC and cause `counter` later to increment twice as much
class Counter(Treeprocessor):
    # TODO: if publishing, verify example
    """
    A counter that is intended to reproduce LaTeX theorem counter functionality by allowing you to specify increments
    for each "counter section".
        - "Counter sections" are the typically period-separated numbers in theorem counters. For example, in
          `Theorem 1.2.4`, the counter sections are 1, 2, and 4.

    Functionality:
        - Increments each section of the counter by specified amount
        - Resets all child counters section to 0 after incrementing a counter
        - Displays only as many counter sections as provided in the Markdown

    Usage:
        ```
        {{<section 1 change>,<section 2 change>,<...>}}
        ```

    Example usage:
        - Markdown:
            ```
            Section {{1}}
            Subsection {{0,1,0}} (displays as many sections as given)
            Lemma {{0,0,0,1}}
            Theorem {{0,0,1}} (the fourth counter section is reset here). Let \(s\) be a lorem ipsum.
            Mental Breakdown {{0,0,0,3}}
            I have no idea what this means {{1,2,0,3,9}}
            ```
        - Output:
            ```
            Section 1
            Subsection 1.1.0 (displays as many sections as given)
            Lemma 1.1.1.1
            Theorem 1.1.2 (the fourth counter section is reset here). Let \(s\) be a lorem ipsum.
            Mental Breakdown 1.1.2.3
            I have no idea what this means 2.3.2.6.9
            ```
    """

    RE = r"{{([0-9,]+)}}"

    def __init__(self, *args, add_html_elem: bool, html_id_prefix: str, html_class: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_html_elem = add_html_elem
        self.html_id_prefix = html_id_prefix
        self.html_class = html_class
        self.counter = []

    def run(self, root):
        for child in root.iter():
            text = child.text
            if text is None:
                continue
            new_text = ""
            prev_match_end = 0
            for m in re.finditer(self.RE, text):
                input_counter = m.group(1)
                parsed_counter = input_counter.split(",")
                # make sure we have enough room to parse counter into `self.counter`
                while len(parsed_counter) > len(self.counter):
                    self.counter.append(0)

                # parse counter
                for i, parsed_item in enumerate(parsed_counter):
                    try:
                        parsed_item = int(parsed_item)
                    except:
                        return False
                    self.counter[i] += parsed_item
                    # if changing current counter section, reset all child sections back to 0
                    if parsed_item != 0 and len(parsed_counter) >= i + 1:
                        self.counter[i+1:] = [0] * (len(self.counter) - (i+1))

                # only output as many counter sections as were inputted
                output_counter = list(map(str, self.counter[:len(parsed_counter)]))
                output_counter_text = ".".join(output_counter)
                if self.add_html_elem:
                    # TODO: convert to more etree-ic way if possible
                    output_counter_text = \
                            f"<span id=\"{self.html_id_prefix}{'-'.join(output_counter)}\" class=\"{self.html_class}\">" \
                            + output_counter_text \
                            + "</span>"
                new_text += text[prev_match_end:m.start()] + output_counter_text
                prev_match_end = m.end()
            # fill in the remaining text after last regex match!
            new_text += text[prev_match_end:]
            child.text = new_text


class ThmHeading(InlineProcessor, HtmlClassMixin):
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

    def __init__(self, *args, html_class: str, thm_type_html_class: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_html_class(html_class)
        self.thm_type_html_class = thm_type_html_class

    def handleMatch(self, m, current_text_block):
        def format_for_html(s: str) -> str:
            s = ("-".join(s.split())).lower() 
            s = s[:-1].replace(".", "-") + s[-1] # replace periods, except trailing ones for counter, with hyphens
            s = re.sub(r"[^A-Za-z0-9-]", "", s)
            return s

        elem = etree.Element("span")
        elem.set("class", self.html_class)
        elem_thm_type = etree.SubElement(elem, "span")
        elem_thm_type.set("class", self.thm_type_html_class)
        elem_thm_type.text = f"{m.group(1)}"
        if m.group(2) is not None:
            # TODO
            elem.text += f" ({m.group(2)})"
            #elem_non_thm_type = etree.SubElement(elem, "span")
            #elem_non_thm_type.text = f" ({m.group(2)})"
            elem.set("id", format_for_html(m.group(2)))
        elif m.group(3) is not None:
            elem.set("id", format_for_html(m.group(3)))
        return elem, m.start(0), m.end(0)


class ThmsExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            "div_html_class": [
                "",
                "HTML `class` attribute to add to div (default: `\"\"`)."
            ],
            "div_types": [
                {},
                "Types of div-based theorem environments to define (default: `{}`)."
            ],
            "dropdown_html_class": [
                "",
                "HTML `class` attribute to add to dropdown (default: `\"\"`)."
            ],
            "dropdown_summary_html_class": [
                "",
                "HTML `class` attribute to add to dropdown summary (default: `\"\"`)."
            ],
            "dropdown_content_html_class": [
                "",
                "HTML `class` attribute to add to dropdown content (default: `\"\"`)."
            ],
            "dropdown_types": [
                {},
                "Types of dropdown-based theorem environments to define (default: `{}`)."
            ],
            "counter_add_html_elem": [
                False,
                "Whether theorem counters are contained in their own HTML element (default: `False`)."
            ],
            "counter_html_id_prefix": [
                "",
                (
                    "Text to prepend to HTML `id` attribute of theorem counters if `counter_add_html_elem` is `True` "
                    "(default: `\"\"`)."
                )
            ],
            "counter_html_class": [
                "",
                "HTML `class` attribute of theorem counters if `counter_add_html_elem` is `True` (default: `\"\"`)."
            ],
            "thm_heading_html_class": [
                "",
                "HTML `class` attribute of theorem heading (default: `\"\"`)."
            ],
            "thm_heading_thm_type_html_class": [
                "",
                "HTML `class` attribute of theorem type HTML element in theorem heading (default: `\"\"`)."
            ]
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        # registering resets state between uses of `markdown.Markdown` object for things like the Counter extension
        md.registerExtension(self)

        # TODO: check if lower priority means breaks toc again
        # priority must be higher than TOC extension
        md.treeprocessors.register(
                Counter(md, add_html_elem=self.getConfig("counter_add_html_elem"),
                        html_id_prefix=self.getConfig("counter_html_id_prefix"),
                        html_class=self.getConfig("counter_html_class")),
                "counter", 999)
        md.inlinePatterns.register(
                ThmHeading(r"{\[(.+?)\]}(?:\[(.+?)\])?(?:{(.+?)})?", md,
                        html_class=self.getConfig("thm_heading_html_class"),
                        thm_type_html_class=self.getConfig("thm_heading_thm_type_html_class")),
                "thm_heading", 105)

        # TODO: test without math counter/thm heading (set to False)
        # set default options for types
        def apply_default_opts_for_types(d: dict):
            for type, opts in d.items():
                opts.setdefault("thm_heading_name", "")
                opts.setdefault("html_class", "")
                opts.setdefault("counter", None)
                opts.setdefault("overrides_heading", False)
                opts.setdefault("punct", ".")
                opts.setdefault("use_punct_if_nameless", True)
            return d
        self.setConfig("div_types", apply_default_opts_for_types(self.getConfig("div_types")))
        self.setConfig("dropdown_types", apply_default_opts_for_types(self.getConfig("dropdown_types")))

        md.parser.blockprocessors.register(
                Div(md.parser, html_class=self.getConfig("div_html_class"), types=self.getConfig("div_types"),
                        use_thm_counter=True, use_thm_headings=True),
                "thms_div", 105)
        md.parser.blockprocessors.register(
                Dropdown(md.parser, html_class=self.getConfig("dropdown_html_class"),
                        summary_html_class=self.getConfig("dropdown_summary_html_class"),
                        content_html_class=self.getConfig("dropdown_content_html_class"),
                        types=self.getConfig("dropdown_types"),
                        use_thm_counter=True, use_thm_headings=True),
                "thms_dropdown", 999)


def makeExtension(**kwargs):
    return ThmsExtension(**kwargs)
