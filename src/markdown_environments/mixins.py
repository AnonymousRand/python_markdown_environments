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
        for typ in self.types:
            if self.is_thm:
                self.re_start_choices[typ] = rf"^\\begin{{{typ}}}(?:\[(.+?)\])?(?:{{(.+?)}})?"
            else:
                self.re_start_choices[typ] = rf"^\\begin{{{typ}}}"
            self.re_end_choices[typ] = rf"^\\end{{{typ}}}"

    def gen_thm_heading(self, block: str) -> str:
        if not self.is_thm:
            return ""

        re_start_match = re.match(self.re_start, block, re.MULTILINE)
        prepend = ""
        if self.type_opts.get("thm_name_overrides_heading"):
            # override theorem heading with theorem name if applicable
            if re_start_match.group(1) is not None:
                prepend = re_start_match.group(1)
        else:
            prepend = self.type_opts.get("thm_type")
            # fill in math counter by using my `counter` extension's syntax
            thm_counter_incr = self.type_opts.get("thm_counter_incr")
            if thm_counter_incr != "":
                prepend += f" {{{{{thm_counter_incr}}}}}"

        # put math theorem heading into `ThmHeading`'s syntax
        prepend = "{[" + prepend + "]}"
        if not self.type_opts.get("thm_name_overrides_heading") and re_start_match.group(1) is not None:
            prepend += "[" + re_start_match.group(1) + "]"
        if re_start_match.group(2) is not None:
            prepend += "{" + re_start_match.group(2) + "}"
        return prepend

    def prepend_thm_heading(self, target_elem: etree.Element, prepend: str) -> None:
        if not self.is_thm or prepend == "":
            return

        # add to first `<p>` child if possible to put it on the same line and minimize CSS `display: inline` chaos
        first_p = target_elem.find("p")
        target_elem = first_p if first_p is not None else target_elem
        if target_elem.text is not None:
            target_elem.text = f"{prepend}{self.type_opts.get('thm_heading_punct')} {target_elem.text}"
        else:
            if self.type_opts.get("use_punct_if_no_thm_name"):
                target_elem.text = f"{prepend}{self.type_opts.get('thm_heading_punct')}"
            else:
                target_elem.text = prepend

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
