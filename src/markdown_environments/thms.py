import re
import xml.etree.ElementTree as etree
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.treeprocessors import Treeprocessor

from . import util
from .mixins import HtmlClassMixin


# the only reason this is a `Treeprocessor` and not a `Preprocessor`, `InlineProcessor`, or `Postprocessor`, all of
# which make more sense, is because we need this to run after `thms` (`BlockProcessor`) and before the TOC extension
# (`Treeprocessor` with low priority): `thms` generates `counter` syntax, while TOC will duplicate unparsed
# `counter` syntax from headings into the TOC and cause `counter` later to increment twice as much
class ThmCounterProcessor(Treeprocessor):
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


class ThmHeadingProcessor(InlineProcessor, HtmlClassMixin):
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

    def __init__(self, *args, html_class: str, emph_html_class: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_html_class(html_class)
        self.emph_html_class = emph_html_class

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
        if self.emph_html_class != "":
            elem_thm_type.set("class", self.emph_html_class)
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


class ThmsExtension(Extension):
    r"""
    A wrapper around divs and dropdowns that provides more configurable options to mimic the theorem capabilities of
    LaTeX.

    In particular, this extension introduces theorem headings and theorem counters, which are used in theorem
    environments but can also be used standalone as described below.

    Theorem headings:
        The terminology I use for the parts of a theorem heading throughout the documentation is as follows:
            
           .. code-block:: text

               Lemma 2.1.3 (Euler's theorem).
                 ^     ^           ^        ^
                thm   thm         thm      thm
               type counter       name    punct

        Markdown usage:
            .. code-block:: md

                {[<thm type><thm counter>]}[<optional thm name>]{<optional hidden thm name>}

            becomes…

            .. code-block:: html

                <span id="[optional thm name/optional hidden thm name]">
                  <span>[thm type][thm counter]</span>
                </span>
                [optional thm name]

            `<optional hidden thm name>` is only used for the HTML `id`, and it is ignored if `<optional thm name>` is
            provided.

    Theorem counters:
        Theorem counters are specified as a (positive) offset from the previous theorem counter, similar to how
        `\\newtheorem` in LaTeX lets you define the counter (but hopefully in a slightly less janky way). Offsets are
        specified per segment, and incrementing a segment resets all following segments to 0. In addition, each counter
        will display only as many segments as provided in its Markdown.

        Markdown usage:
            .. code-block:: md

                Section {{1}}
                Subsection {{0,1,0,0,0,0,0}} (displays as many segments as given)
                Lemma {{0,0,0,1}}
                Theorem {{0,0,1}} (the fourth counter segment is reset here). Let x be a lorem ipsum.
                Reevaluating Life Choices {{0,0,0,3}}
                What even is this {{1,2,0,3,9}} (first counter segment resets next ones, and so on)

            becomes…

            .. code-block:: html

                <p>Section 1</p>
                <p>Subsection 1.1.0.0.0.0.0 (displays as many segments as given)</p>
                <p>Lemma 1.1.0.1</p>
                <p>Theorem 1.1.1 (the fourth counter segment is reset here). Let x be a lorem ipsum.</p>
                <p>Reevaluating Life Choices 1.1.1.3</p>
                <p>What even is this 2.2.0.3.9 (first counter segment resets next ones, and so on)</p>

    Example:
        .. code-block:: py

            import markdown
            from markdown_environments import ThmsExtension

            input_text = ...
            output_text = markdown.markdown(input_text, extensions=[
                ThmsExtension(
                    div_config={
                        "types": {
                            "thm": {
                                "thm_type": "Theorem",
                                "html_class": "md-thm",
                                "thm_counter_incr": "0,0,1"
                            }
                        },
                        "html_class": "md-div"
                    },
                    dropdown_config={
                        "types": {
                            "exer": {
                                "thm_type": "Exercise",
                                "html_class": "md-exer",
                                "thm_counter_incr": "0,0,1",
                            }
                        },
                        "html_class": "md-dropdown",
                        "content_html_class": "md-dropdown__content"
                    },
                    thm_counter_config={
                        "add_html_elem": True,
                        "html_id_prefix": "spanish-inquisition"
                    },
                    thm_heading_config={
                        "html_class": "md-thm-heading",
                    }
                )
            ])

    Markdown usage (div-based):
        .. code-block:: md

            \begin{<type>}[<optional thm name>]{<optional hidden thm name>}
            <content>
            \end{<type>}

        becomes, with theorem heading and counter syntax…

        .. code-block:: md

            \begin{<type>}
            {[<type's thm type> {{<type's thm_counter_incr>}}]}[<optional thm name>]{<optional hidden thm name>}
            <content>
            \end{<type>}

        becomes…

        .. code-block:: html

            <div class="[html_class] [type's html_class]">
              <span id="[optional thm name/optional hidden thm name]">
                <span>[thm type][thm counter]</span>
              </span>
              [optional thm name][type's thm_punct] [content]
            </div>
    """

    def __init__(self, **kwargs):
        r"""
        Initialize dropdown extension, with configuration options passed as the following keyword arguments:

            - **div_config** (*dict*) -- configs for divs. Possible config keys are:

                - **types** (*dict*) -- Types of div-based theorem environments to define. Defaults to `{}`.
                - **html_class** (*str*) -- HTML `class` attribute to add to div-based theorem environments.
                  Defaults to `""`.

            - **dropdown_config** (*dict*) -- configs for dropdowns. Possible config keys are:

                - **types** (*dict*) -- Types of dropdown-based theorem environments to define. Defaults to `{}`.
                - **html_class** (*str*) -- HTML `class` attribute to add to dropdown-based theorem environments.
                  Defaults to `""`.
                - **summary_html_class** (*str*) -- HTML `class` attribute to add to dropdown summaries.
                  Defaults to `""`.
                - **content_html_class** (*str*) -- HTML `class` attribute to add to dropdown contents.
                  Defaults to `""`.

            - **thm_counter_config** (*dict*) -- configs for theorem counter. Possible config keys are:

                - **add_html_elem** (*bool*) -- Whether theorem counters are contained in their own HTML element.
                  Defaults to `False`.
                - **html_id_prefix** (*str*) -- Text to prepend to HTML `id` attribute of theorem counters if
                  `add_html_elem` is `True`. Defaults to `""`.
                - **html_class** (*str*) -- HTML `class` attribute of theorem counters if `add_html_elem` is `True`.
                  Defaults to `""`.

            - **thm_heading_config** (*dict*) -- configs for theorem headings. Possible config keys are:

                - **html_class** (*str*) -- HTML `class` attribute to add to theorem headings. Defaults to `""`.
                - **emph_html_class** (*str*) -- HTML `class` attribute to add to theorem types in theorem headings.
                  Defaults to `""`.

        The key for each type defined in both div and dropdown `types` is inserted directly into the regex patterns that
        search for `\\begin{<type>}` and `\\end{<type>}`, so anything you specify will be interpreted as regex. In
        addition, each type's value is itself a dictionary with the following possible options:

            - **thm_type** (*str*) -- Defaults to `""`.
            - **html_class** (*str*) -- HTML `class` attribute to add to dropdowns of that type. Defaults to `""`.
            - **thm_counter_incr** (*str*) -- Defaults to `""`.
            - **thm_name_overrides_thm_heading** (*bool*) -- Defaults to `False`.
            - **thm_punct** (*str*) -- Defaults to `"."`.
            - **use_punct_if_nothing_after** (*bool*) -- Defaults to `True`.
        """

        self.config = {
            "div_config": [
                {},
                "Config for div"
            ],
            "dropdown_config": [
                {},
                "Config for dropdown"
            ],
            "thm_counter_config": [
                {},
                "Config for theorem counter"
            ],
            "thm_heading_config": [
                {},
                "Config for theorem heading"
            ]
        }
        util.init_extension_with_configs(self, **kwargs)

        # set default configs for each extension, since we no longer have the top-level `self.config` functionality
        # to set defaults for us
        div_config = self.getConfig("div_config")
        div_config.setdefault("types", {})
        div_config.setdefault("html_class", "")

        dropdown_config = self.getConfig("dropdown_config")
        dropdown_config.setdefault("types", {})
        dropdown_config.setdefault("html_class", "")
        dropdown_config.setdefault("summary_html_class", "")
        dropdown_config.setdefault("content_html_class", "")

        thm_counter_config = self.getConfig("thm_counter_config")
        thm_counter_config.setdefault("add_html_elem", False)
        thm_counter_config.setdefault("html_id_prefix", "")
        thm_counter_config.setdefault("html_class", "")

        thm_heading_config = self.getConfig("thm_heading_config")
        thm_heading_config.setdefault("html_class", "")
        thm_heading_config.setdefault("emph_html_class", "")

    def extendMarkdown(self, md):
        # registering resets state between uses of `markdown.Markdown` object for things like the `ThmCounter` extension
        md.registerExtension(self)

        div_config = self.getConfig("div_config")
        dropdown_config = self.getConfig("dropdown_config")
        thm_counter_config = self.getConfig("thm_counter_config")
        thm_heading_config = self.getConfig("thm_heading_config")
        # remember `ThmCounter`'s priority must be higher than TOC extension
        md.treeprocessors.register(
                ThmCounterProcessor(md, add_html_elem=thm_counter_config.get("add_html_elem"),
                        html_id_prefix=thm_counter_config.get("html_id_prefix"),
                        html_class=thm_counter_config.get("html_class")),
                "thm_counter", 999)
        md.inlinePatterns.register(
                ThmHeadingProcessor(r"{\[(.+?)\]}(?:\[(.+?)\])?(?:{(.+?)})?", md,
                        html_class=thm_heading_config.get("html_class"),
                        emph_html_class=thm_heading_config.get("emph_html_class")),
                "thm_heading", 105)

        if len(div_config.get("types", {})) > 0:
            from .div import DivProcessor
            md.parser.blockprocessors.register(
                    DivProcessor(md.parser, types=div_config.get("types"),
                            html_class=div_config.get("html_class"), is_thm=True),
                    "thms_div", 105)
        if len(dropdown_config.get("types", {})) > 0:
            from .dropdown import DropdownProcessor
            md.parser.blockprocessors.register(
                    DropdownProcessor(md.parser, types=dropdown_config.get("types"), 
                            html_class=dropdown_config.get("html_class"),
                            summary_html_class=dropdown_config.get("summary_html_class"),
                            content_html_class=dropdown_config.get("content_html_class"), is_thm=True),
                    "thms_dropdown", 999)


def makeExtension(**kwargs):
    return ThmsExtension(**kwargs)
