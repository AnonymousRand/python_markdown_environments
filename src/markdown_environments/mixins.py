import re
import xml.etree.ElementTree as etree
from abc import ABC


class HtmlClassMixin(ABC):
    def init_html_class(self, html_class: str):
        self.html_class = html_class


class ThmMixin(ABC):
    def init_thm(self, types: dict, is_thm: bool):
        self.types = types
        self.is_thm = is_thm
        self.type_opts = None
        self.re_start = None
        self.re_end = None

        # init regex patterns
        self.re_start_choices = {}
        self.re_end_choices = {}
        for typ, opts in self.types.items():
            # set default options for individual types
            opts.setdefault("thm_type", "")
            opts.setdefault("html_class", "")
            opts.setdefault("thm_counter_incr", "")
            opts.setdefault("thm_punct", ".")
            opts.setdefault("thm_name_overrides_thm_heading", False)
            opts.setdefault("use_punct_if_nothing_after", True)
            # add type to regex choices
            if self.is_thm:
                self.re_start_choices[typ] = rf"^\\begin{{{typ}}}(?:\[(.+?)\])?(?:{{(.+?)}})?"
            else:
                self.re_start_choices[typ] = rf"^\\begin{{{typ}}}"
            self.re_end_choices[typ] = rf"^\\end{{{typ}}}"

    def gen_thm_heading_md(self, block: str) -> str:
        if not self.is_thm:
            return ""

        # override theorem heading with theorem name if applicable
        re_start_match = re.match(self.re_start, block, re.MULTILINE)
        thm_name = re_start_match.group(1)
        if self.type_opts.get("thm_name_overrides_thm_heading") and thm_name is not None:
            return "{[" + thm_name + "]}{" + thm_name + "}"

        # else find rest of theorem heading's pieces using regex
        thm_type = self.type_opts.get("thm_type")
        thm_hidden_name = re_start_match.group(2)
        # fill in theorem counter using `ThmCounter`'s syntax
        thm_counter_incr = self.type_opts.get("thm_counter_incr")
        if thm_counter_incr != "":
            thm_type += " {{" + thm_counter_incr + "}}"

        # assemble theorem heading into `ThmHeading`'s syntax
        thm_heading_md = "{[" + thm_type + "]}"
        if thm_name is not None:
            thm_heading_md += "[" + thm_name + "]"
        if thm_hidden_name is not None:
            thm_heading_md += "{" + thm_hidden_name + "}"
        return thm_heading_md

    def prepend_thm_heading_md(self, target_elem: etree.Element, thm_heading_md: str) -> None:
        if not self.is_thm or thm_heading_md == "":
            return

        # add to first `<p>` child if possible to put it on the same line and minimize CSS `display: inline` chaos
        first_p = target_elem.find("p")
        target_elem = first_p if first_p is not None else target_elem
        if target_elem.text is not None:
            target_elem.text = f"{thm_heading_md}{self.type_opts.get('thm_punct')} {target_elem.text}"
        else:
            if self.type_opts.get("use_punct_if_nothing_after"):
                target_elem.text = f"{thm_heading_md}{self.type_opts.get('thm_punct')}"
            else:
                target_elem.text = thm_heading_md

    # def not best practice to assume child class is a `BlockProcessor` implementing `test()`
    # but i'm addicted to code reuse
    def test(self, parent, block) -> bool:
        for typ, regex in self.re_start_choices.items():
            if re.match(regex, block, re.MULTILINE):
                self.type_opts = self.types[typ]
                self.re_start = regex
                self.re_end = self.re_end_choices[typ]
                return True
        return False
