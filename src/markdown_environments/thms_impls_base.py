import re
import xml.etree.ElementTree as etree


# note: this does not inherit from `BlockProcessor` to make this class easier to instantiate
# by itself for testing
class ThmsImplsBase:

    def __init__(self, types: dict, is_thm: bool):
        self.types = types
        self.is_thm = is_thm
        self.start_patterns = {}
        self.end_patterns = {}

        self.start_pattern = None
        self.end_pattern = None
        self.type_opts = None

        self.init_env_types()

    def init_env_types(self) -> None:
        for typ, opts in self.types.items():
            # set default options for individual types
            opts.setdefault("thm_type", "")
            opts.setdefault("html_class", "")
            opts.setdefault("thm_counter_incr", "")
            opts.setdefault("thm_name_overrides_thm_heading", False)
            # add type to regex pattern choices
            if self.is_thm:
                self.start_patterns[typ] = re.compile(
                    rf"^\\begin{{{typ}}}(?:\[(.+?)\])?(?:{{(.+?)}})?$", flags=re.MULTILINE
                )
            else:
                self.start_patterns[typ] = re.compile(rf"^\\begin{{{typ}}}$", flags=re.MULTILINE)
            self.end_patterns[typ] = re.compile(rf"^\\end{{{typ}}}", flags=re.MULTILINE)

    def test(self, parent, block):
        matched_type = ""
        for typ, pattern in self.start_patterns.items():
            if pattern.match(block):
                matched_type = typ
                break;
        if matched_type == "":
            return False

        self.start_pattern = self.start_patterns[matched_type]
        self.end_pattern = self.end_patterns[matched_type]
        self.type_opts = self.types[matched_type]
        return True

    def gen_thm_heading_md(self, block: str) -> str:
        start_pattern_match = self.start_pattern.match(block)
        thm_type = self.type_opts["thm_type"]
        thm_counter_incr = self.type_opts["thm_counter_incr"]
        thm_name = start_pattern_match.group(1)
        thm_hidden_name = start_pattern_match.group(2)

        # override theorem heading with theorem name if applicable
        thm_heading_md = ""
        if self.type_opts["thm_name_overrides_thm_heading"] and thm_name is not None:
            thm_heading_md = "{[" + thm_name + "]}{" + thm_name + "}"
        # else assemble theorem heading into `ThmHeading`'s syntax
        else:
            if thm_counter_incr != "":
                # fill in theorem counter using `ThmCounter`'s syntax
                thm_type += " {{" + thm_counter_incr + "}}"
            thm_heading_md = "{[" + thm_type + "]}"
            if thm_name is not None:
                thm_heading_md += "[" + thm_name + "]"
            if thm_hidden_name is not None:
                thm_heading_md += "{" + thm_hidden_name + "}"
        # trailing newline to make sure text within the theorem heading (e.g. LaTeX curly brackets)
        # don't interfere with parsing and cause the regex pattern to stop matching prematurely
        return thm_heading_md + "\n"


    @staticmethod
    def prepend_thm_heading_md(target_elem: etree.Element, thm_heading_md: str) -> None:
        thm_heading_elem = target_elem
        if thm_heading_md == "":
            return
        # if first child is a `<p>`, add thm heading to it instead to put it on the same line
        # without needing CSS `display: inline` chaos
        is_added_inline = False
        if (len(target_elem) > 0) and (target_elem[0].tag == "p"):
            is_added_inline = True
            thm_heading_elem = target_elem[0]

        if not is_added_inline:
            # if not able to add to first `<p>`, wrap theorem heading in its own `<p>` and then prepend to target elem
            # since it's just a `<span>` right now (for bottom margin etc.)
            p_elem = etree.Element("p")
            p_elem.text = thm_heading_md
            p_elem.tail = " "
            thm_heading_elem.insert(0, p_elem)
        else:
            # else just prepend theorem heading normally
            old_text = thm_heading_elem.text if thm_heading_elem.text is not None else ""
            thm_heading_elem.text = f"{thm_heading_md} {old_text}"
