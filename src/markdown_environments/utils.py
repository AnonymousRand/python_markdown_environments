import re
import xml.etree.ElementTree as etree


def init_extension_with_configs(obj, **kwargs) -> None:
    try:
        super(obj.__class__, obj).__init__(**kwargs)
    except KeyError as e:
        raise KeyError(f"{e} (did you pass in an invalid config key to {obj.__class__.__name__}.__init__()?)")


def init_env_types(types: dict, is_thm: bool) -> tuple[dict, dict, dict]:
    start_pattern_choices = {}
    end_pattern_choices = {}
    for typ, opts in types.items():
        # set default options for individual types
        opts.setdefault("thm_type", "")
        opts.setdefault("html_class", "")
        opts.setdefault("thm_counter_incr", "")
        opts.setdefault("thm_name_overrides_thm_heading", False)
        # add type to regex pattern choices
        if is_thm:
            start_pattern_choices[typ] = re.compile(rf"^\\begin{{{typ}}}(?:\[(.+?)\])?(?:{{(.+?)}})?", flags=re.MULTILINE)
        else:
            start_pattern_choices[typ] = re.compile(rf"^\\begin{{{typ}}}", flags=re.MULTILINE)
        end_pattern_choices[typ] = re.compile(rf"^\\end{{{typ}}}", flags=re.MULTILINE)
    return types, start_pattern_choices, end_pattern_choices


def test_for_env_types(start_pattern_choices: dict, parent: etree.Element, block: str) -> str | None:
    for typ, pattern in start_pattern_choices.items():
        if pattern.match(block):
            return typ
    return None


def gen_thm_heading_md(type_opts: dict, start_pattern: re.Pattern, block: str) -> str:
    start_pattern_match = start_pattern.match(block)
    thm_type = type_opts.get("thm_type")
    thm_counter_incr = type_opts.get("thm_counter_incr")
    thm_name = start_pattern_match.group(1)
    thm_hidden_name = start_pattern_match.group(2)

    # override theorem heading with theorem name if applicable
    if type_opts.get("thm_name_overrides_thm_heading") and thm_name is not None:
        return "{[" + thm_name + "]}{" + thm_name + "}"
    # else assemble theorem heading into `ThmHeading`'s syntax
    if thm_counter_incr != "":
        # fill in theorem counter using `ThmCounter`'s syntax
        thm_type += " {{" + thm_counter_incr + "}}"
    thm_heading_md = "{[" + thm_type + "]}"
    if thm_name is not None:
        thm_heading_md += "[" + thm_name + "]"
    if thm_hidden_name is not None:
        thm_heading_md += "{" + thm_hidden_name + "}"
    return thm_heading_md


def prepend_thm_heading_md(type_opts: dict, target_elem: etree.Element, thm_heading_md: str) -> None:
    thm_heading_elem = target_elem
    if thm_heading_md == "":
        return
    # if first child is a `<p>`, add thm heading to it instead to put it on the same line
    # without needing CSS `display: inline` chaos
    added_inline = False
    try:
        if target_elem[0].tag == "p":
            added_inline = True
            thm_heading_elem = target_elem[0]
    except IndexError:
        # if no children
        pass

    if not added_inline:
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
