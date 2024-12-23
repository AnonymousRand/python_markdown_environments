import re
import xml.etree.ElementTree as etree
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.treeprocessors import Treeprocessor

# TODO: conditional import depending on user config (like if user config includes dropdown, import dropdown)?
from dropdown import Dropdown
from div import Div


# TODO: if releasing Counter, test with no adding html/varied params, also linking to counter via URL fragment

# the only reason this is a `Treeprocessor` and not a `Preprocessor`, `InlineProcessor`, or `Postprocessor`, all of
# which make more sense, is because we need this to run after `thms` (`BlockProcessor`) and before `toc`
# (`Treeprocessor` with low priority): `thms` generates `counter` syntax, while `toc` will duplicate unparsed
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

    def __init__(self, *args, add_html_elem=False, html_id_prefix="", html_class="", **kwargs):
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
        # registering resets state between uses of `markdown.Markdown` object for things like `Counter`
        md.registerExtension(self)

        regex = r"{\[(.+?)\]}(?:\[(.+?)\])?(?:{(.+?)})?"
        md.inlinePatterns.register(ThmHeading(regex, md), "thm_heading", 105)
        md.treeprocessors.register(Counter(md, add_html_elem=False), "counter", 999)

        # TODO: these need to be passed in via extension config
        # TODO:: test without math counter/thm heading (set to False)
        div_types = {
            "coro": {
                "display_name": "Corollary",
                "html_class": "md-textbox md-textbox-coro last-child-no-mb",
                "counter": "0,0,1"
            },
            "defn": {
                "display_name": "Definition",
                "html_class": "md-textbox md-textbox-defn last-child-no-mb",
                "counter": "0,0,1"
            },
            r"defn\\\*": {
                "display_name": "Definition",
                "html_class": "md-textbox md-textbox-defn last-child-no-mb"
            },
            "ex": {
                "display_name": "Example",
                "html_class": "md-div-ex"
            },
            r"notat\\\*": {
                "display_name": "Notation",
                "html_class": "md-textbox md-textbox-notat last-child-no-mb"
            },
            "prop": {
                "display_name": "Proposition",
                "html_class": "md-textbox md-textbox-prop last-child-no-mb",
                "counter": "0,0,1"
            },
            "thm": {
                "display_name": "Theorem",
                "html_class": "md-textbox md-textbox-thm last-child-no-mb",
                "counter": "0,0,1"
            },
            r"thm\\\*": {
                "display_name": "Theorem",
                "html_class": "md-textbox md-textbox-thm last-child-no-mb"
            }
        }
        dropdown_types = {
            "exer": {
                "display_name": "Exercise",
                "html_class": "md-dropdown-exer",
                "counter": "0,0,1",
                "use_punct_if_nameless": False
            },
            "pf": {
                "display_name": "Proof",
                "html_class": "md-dropdown-pf",
                "overrides_heading": True,
                "use_punct_if_nameless": False
            },
            r"rmk\\\*": {
                "display_name": "Remark",
                "html_class": "md-dropdown-rmk",
                "overrides_heading": True,
                "use_punct_if_nameless": False
            }
        }
        # set default values for dicts
        for d in [dropdown_types, div_types]:
            for type_opts in d.values():
                type_opts.setdefault("display_name", "")
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
