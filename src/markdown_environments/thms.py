import re
import xml.etree.ElementTree as etree
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.treeprocessors import Treeprocessor

from . import util
from .mixins import HtmlClassMixin


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

        # create theorem heading element
        elem = etree.Element("span")
        if self.html_class != "":
            elem.set("class", self.html_class)
        # create and fill in theorem type subelement
        elem_thm_type = etree.SubElement(elem, "span")
        if self.thm_type_html_class != "":
            elem_thm_type.set("class", self.thm_type_html_class)
        elem_thm_type.text = f"{m.group(1)}"
        # fill in the rest
        if m.group(2) is not None:
            # add theorem name
            elem_thm_type.tail = f" ({m.group(2)})"
            elem.set("id", format_for_html(m.group(2)))
        elif m.group(3) is not None:
            # add theorem `id` from hidden name
            elem.set("id", format_for_html(m.group(3)))
        return elem, m.start(0), m.end(0)


# the only reason this is a `Treeprocessor` and not a `Preprocessor`, `InlineProcessor`, or `Postprocessor`, all of
# which make more sense, is because we need this to run after `thms` (`BlockProcessor`) and before the TOC extension
# (`Treeprocessor` with low priority): `thms` generates `counter` syntax, while TOC will duplicate unparsed
# `counter` syntax from headings into the TOC and cause `counter` later to increment twice as much
class ThmCounter(Treeprocessor):
    """
    A counter that is intended to reproduce LaTeX theorem counter functionality by allowing you to specify increments
    for each "counter segment".
        - "Counter segments" are the typically period-separated numbers in theorem counters. For example, in
          `Theorem 1.2.4`, the three counter segments are 1, 2, and 4.

    Functionality:
        - Increments each counter segment by specified amount
        - Resets all child counters segment to 0 after incrementing a counter
        - Displays only as many counter segments as provided in the Markdown

    Usage:
        ```
        {{<segment 1 change>,<segment 2 change>,<...>}}
        ```

    Example usage:
        - Markdown:
            ```
            Section {{1}}
            Subsection {{0,1,0}} (displays as many segments as given)
            Lemma {{0,0,0,1}}
            Theorem {{0,0,1}} (the fourth counter segment is reset here). Let x be a lorem ipsum.
            Reevaluating Life Choices {{0,0,0,3}}
            What even is this {{1,2,0,3,9}} (first counter segment resets next ones, and so on)
            ```
        - Output:
            ```
            Section 1
            Subsection 1.1.0 (displays as many segments as given)
            Lemma 1.1.0.1
            Theorem 1.1.1 (the fourth counter segment is reset here). Let x be a lorem ipsum.
            Reevaluating Life Choices 1.1.1.3
            What even is this 2.2.0.3.9 (first counter segment resets next ones, and so on)
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
                    # if changing current counter segment, reset all child segments back to 0
                    if parsed_item != 0 and len(parsed_counter) >= i + 1:
                        self.counter[i+1:] = [0] * (len(self.counter) - (i+1))

                # only output as many counter segments as were inputted
                output_counter = list(map(str, self.counter[:len(parsed_counter)]))
                output_counter_text = ".".join(output_counter)
                if self.add_html_elem:
                    elem = etree.Element("span")
                    elem.set("id", self.html_id_prefix + '-'.join(output_counter))
                    if self.html_class != "":
                        elem.set("class", self.html_class)
                    elem.text = output_counter_text
                    output_counter_text = etree.tostring(elem, encoding="unicode")
                new_text += text[prev_match_end:m.start()] + output_counter_text
                prev_match_end = m.end()
            # fill in the remaining text after last regex match!
            new_text += text[prev_match_end:]
            child.text = new_text


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
            "thm_counter_add_html_elem": [
                False,
                "Whether theorem counters are contained in their own HTML element (default: `False`)."
            ],
            "thm_counter_html_id_prefix": [
                "",
                (
                    "Text to prepend to HTML `id` attribute of theorem counters if `counter_add_html_elem` is `True` "
                    "(default: `\"\"`)."
                )
            ],
            "thm_counter_html_class": [
                "",
                "HTML `class` attribute of theorem counters if `counter_add_html_elem` is `True` (default: `\"\"`)."
            ],
            "thm_heading_html_class": [
                "",
                "HTML `class` attribute of theorem heading (default: `\"\"`)."
            ],
            "thm_type_html_class": [
                "",
                "HTML `class` attribute of theorem type HTML element in theorem heading (default: `\"\"`)."
            ]
        }
        util.init_extension_with_configs(self, **kwargs)

        # set default options for individual types
        def apply_default_opts_for_types(d: dict):
            for type, opts in d.items():
                opts.setdefault("thm_type", "")
                opts.setdefault("html_class", "")
                opts.setdefault("thm_counter_incr", "")
                opts.setdefault("thm_name_overrides_heading", False)
                opts.setdefault("thm_heading_punct", ".")
                opts.setdefault("use_punct_if_no_thm_name", True)
            return d
        self.setConfig("div_types", apply_default_opts_for_types(self.getConfig("div_types")))
        self.setConfig("dropdown_types", apply_default_opts_for_types(self.getConfig("dropdown_types")))


    def extendMarkdown(self, md):
        # registering resets state between uses of `markdown.Markdown` object for things like the `ThmCounter` extension
        md.registerExtension(self)

        # remember `ThmCounter`'s priority must be higher than TOC extension
        md.treeprocessors.register(
                ThmCounter(md, add_html_elem=self.getConfig("thm_counter_add_html_elem"),
                        html_id_prefix=self.getConfig("thm_counter_html_id_prefix"),
                        html_class=self.getConfig("thm_counter_html_class")),
                "thm_counter", 999)
        md.inlinePatterns.register(
                ThmHeading(r"{\[(.+?)\]}(?:\[(.+?)\])?(?:{(.+?)})?", md,
                        html_class=self.getConfig("thm_heading_html_class"),
                        thm_type_html_class=self.getConfig("thm_type_html_class")),
                "thm_heading", 105)

        if len(self.getConfig("div_types")) > 0:
            from .div import Div
            md.parser.blockprocessors.register(
                    Div(md.parser, html_class=self.getConfig("div_html_class"),
                            types=self.getConfig("div_types"), is_thm=True),
                    "thms_div", 105)
        if len(self.getConfig("dropdown_types")) > 0:
            from .dropdown import Dropdown
            md.parser.blockprocessors.register(
                    Dropdown(md.parser, html_class=self.getConfig("dropdown_html_class"),
                            summary_html_class=self.getConfig("dropdown_summary_html_class"),
                            content_html_class=self.getConfig("dropdown_content_html_class"),
                            types=self.getConfig("dropdown_types"), is_thm=True),
                    "thms_dropdown", 999)


def makeExtension(**kwargs):
    return ThmsExtension(**kwargs)
