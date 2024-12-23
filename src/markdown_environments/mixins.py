import re
import xml.etree.ElementTree as etree
from abc import ABC


class HtmlClassMixin(ABC):
    def init_html_class(self, html_class: str):
        self.html_class = html_class


class ThmMixin(ABC):
    def init_thm(self, types: dict, use_math_counter: bool, use_math_thm_heading: bool):
        self.types = types
        self.use_math_counter = use_math_counter
        self.use_math_thm_heading = use_math_thm_heading
        self.type_opts = None
        self.re_start = None
        self.re_end = None

        # init regex patterns
        self.re_start_choices = {}
        self.re_end_choices = {}
        for typ in self.types:
            if self.use_math_thm_heading:
                self.re_start_choices[typ] = rf"^\\begin{{{typ}}}(?:\[(.+?)\])?(?:{{(.+?)}})?"
            else:
                self.re_start_choices[typ] = rf"^\\begin{{{typ}}}"
            self.re_end_choices[typ] = rf"^\\end{{{typ}}}"

    def gen_auto_prepend(self, block: str) -> str:
        prepend = self.type_opts.get("display_name")
        if prepend is None:
            return ""

        re_start_match = re.match(self.re_start, block, re.MULTILINE)
        # override theorem heading with theorem name first if applicable
        if self.use_math_thm_heading:
            if self.type_opts.get("overrides_heading") and re_start_match.group(1) is not None:
                prepend = re_start_match.group(1)
        # fill in math counter by using my `counter` extension's syntax
        if self.use_math_counter:
            counter = self.type_opts.get("counter")
            if counter is not None:
                prepend += f" {{{{{counter}}}}}"
        # fill in math theorem heading by using my `thm_heading` extension's syntax
        if self.use_math_thm_heading:
            prepend = "{[" + prepend + "]}"
            if not self.type_opts.get("overrides_heading") and re_start_match.group(1) is not None:
                prepend += "[" + re_start_match.group(1) + "]"
            if re_start_match.group(2) is not None:
                prepend += "{" + re_start_match.group(2) + "}"
        return prepend

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
