import re
import xml.etree.ElementTree as etree


def init_extension_with_configs(obj, **kwargs) -> None:
    try:
        super(obj.__class__, obj).__init__(**kwargs)
    except KeyError as e:
        raise KeyError(f"{e} (did you pass in an invalid config key to {obj.__class__.__name__}.__init__()?)")


def init_env_types(types: dict, is_thm: bool) -> tuple[dict, dict, dict]:
    start_regex_choices = {}
    end_regex_choices = {}
    for typ, opts in types.items():
        # set default options for individual types
        opts.setdefault("thm_type", "")
        opts.setdefault("html_class", "")
        opts.setdefault("thm_counter_incr", "")
        opts.setdefault("thm_name_overrides_thm_heading", False)
        # add type to regex choices
        if is_thm:
            start_regex_choices[typ] = rf"^\\begin{{{typ}}}(?:\[(.+?)\])?(?:{{(.+?)}})?"
        else:
            start_regex_choices[typ] = rf"^\\begin{{{typ}}}"
        end_regex_choices[typ] = rf"^\\end{{{typ}}}"
    return types, start_regex_choices, end_regex_choices


def test_for_env_types(start_regex_choices: dict, parent: etree.Element, block: str) -> str | None:
    for typ, regex in start_regex_choices.items():
        if re.match(regex, block, re.MULTILINE):
            return typ
    return None


def gen_thm_heading_md(type_opts: dict, start_regex: str, block: str) -> str:
    start_regex_match = re.match(start_regex, block, re.MULTILINE)
    thm_type = type_opts.get("thm_type")
    thm_counter_incr = type_opts.get("thm_counter_incr")
    thm_name = start_regex_match.group(1)
    thm_hidden_name = start_regex_match.group(2)

    # override theorem heading with theorem name if applicable
    if type_opts.get("thm_name_overrides_thm_heading") and thm_name is not None:
        return "{[" + thm_name + "]}{" + thm_name + "}"
    # else assemble theorem heading into `ThmHeading`'s syntax
    # fill in theorem counter using `ThmCounter`'s syntax
    if thm_counter_incr != "":
        thm_type += " {{" + thm_counter_incr + "}}"
    thm_heading_md = "{[" + thm_type + "]}"
    if thm_name is not None:
        thm_heading_md += "[" + thm_name + "]"
    if thm_hidden_name is not None:
        thm_heading_md += "{" + thm_hidden_name + "}"
    return thm_heading_md


def prepend_thm_heading_md(type_opts: dict, target_elem: etree.Element, thm_heading_md: str) -> None:
    if thm_heading_md == "":
        return
    # add to first `<p>` child if possible to put it on the same line and minimize CSS `display: inline` chaos
    first_p = target_elem.find("p")
    target_elem = first_p if first_p is not None else target_elem
    if target_elem.text is not None:
        target_elem.text = f"{thm_heading_md} {target_elem.text}"
    else:
        target_elem.text = f"{thm_heading_md}"
