import pytest

from markdown_environments.thms import *
from markdown_environments.utils import *

from ..tests_utils import read_file


def test_init_extension_with_configs_error():
    with pytest.raises(KeyError) as e:
        _ = ThmsExtension(nonexistent_config="")
        assert "'nonexistent_config' (did you pass in an invalid config key to ThmsExtension.__init__()?)" in e


# no test for `init_env_types()` right now because dealing with escape characters with comparing regex strings is pain
# and i have school tomorrow (i deserve coal for christmas)


TYPES = {
    "lem": {
        "thm_type": "Lemma",
        "html_class": "md-textbox md-textbox-defn last-child-no-mb",
        "thm_counter_incr": "0,0,1",
        "thm_punct": ":",
        "use_punct_if_nothing_after": False
    },
    "thm": {
        "thm_type": "Theorem",
        "html_class": "md-textbox md-textbox-thm last-child-no-mb",
        "thm_counter_incr": "0,1"
    },
    r"thm\\\*": {
        "thm_type": "Theorem",
        "html_class": "md-textbox md-textbox-thm last-child-no-mb",
        "thm_counter_incr": "",
        "thm_name_overrides_thm_heading": True
    }
}


@pytest.mark.parametrize(
    "filename_base",
    [
        ("utils/test_for_env_types_1"),
        ("utils/test_for_env_types_2"),
        ("utils/test_for_env_types_3"),
        ("utils/test_for_env_types_4"),
        ("utils/test_for_env_types_5")
    ]
)
def test_test_for_env_types(filename_base):
    block = read_file(f"{filename_base}.txt")
    parent = etree.Element("p")
    parent.text = block
    _, start_regex_choices, _ = utils.init_env_types(types=TYPES, is_thm=True)

    expected = read_file(f"{filename_base}_expected.txt")
    actual = utils.test_for_env_types(start_regex_choices, parent, block)
    print(actual, end="\n")
    assert actual == expected


@pytest.mark.parametrize(
    "filename_base",
    [
        ("utils/gen_thm_heading_md_1"),
        ("utils/gen_thm_heading_md_2"),
        ("utils/gen_thm_heading_md_3"),
        ("utils/gen_thm_heading_md_4"),
        ("utils/gen_thm_heading_md_5"),
        ("utils/gen_thm_heading_md_6"),
        # test that curly braces (e.g. from LaTeX) don't interfere with parsing
        ("utils/gen_thm_heading_md_7"),
        # test that thm headings with no trailing newlines are not parsed
        ("utils/gen_thm_heading_md_8")
    ]
)
def test_gen_thm_heading_md(filename_base):
    block = read_file(f"{filename_base}.txt")
    parent = etree.Element("p")
    parent.text = block
    _, start_regex_choices, _ = utils.init_env_types(types=TYPES, is_thm=True)
    typ = utils.test_for_env_types(start_regex_choices, parent, block)

    expected = read_file(f"{filename_base}_expected.txt")
    # if nothing detected, check that indeed nothing is supposed to change
    if typ == "":
        print(block, end="\n")
        assert block == expected
    else:
        type_opts = TYPES[typ]
        start_regex = start_regex_choices[typ]
        actual = utils.gen_thm_heading_md(type_opts, start_regex, block)
        print(actual, end="\n")
        assert actual == expected


def test_prepend_thm_heading_md():
    type_opts = TYPES["thm"] # doesn't matter for this test

    # test when there's no `<p>` child
    elem = etree.Element("div")
    subelem = etree.SubElement(elem, "span")
    subelem.text = "not a para!"
    utils.prepend_thm_heading_md(type_opts, elem, "heading.")
    assert etree.tostring(elem, encoding="unicode") == "<div><p>heading.</p> <span>not a para!</span></div>"

    # test when there is a `<p>` child
    elem = etree.Element("div")
    elem.text = "outside para"
    para_1 = etree.SubElement(elem, "p")
    para_1 .text = "inside para 1"
    para_2 = etree.SubElement(elem, "p")
    para_2.text = "inside para 2"
    utils.prepend_thm_heading_md(type_opts, elem, "sd")
    assert elem.text == "outside para"
    assert para_1.text == "sd inside para 1" # should prepend into this only
    assert para_2.text == "inside para 2"
