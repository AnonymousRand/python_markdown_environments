import pytest

from markdown_environments.thms_impls_base import *

from ..tests_utils import read_file


# no test for `init_type_opts()` right now because dealing with escape characters when comparing
# regex strings is pain, and i have school tomorrow (i deserve coal for christmas)


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
    "filename_base, expected",
    [
        ("thms_impls_base/test_method_1", True),
        ("thms_impls_base/test_method_2", True),
        ("thms_impls_base/test_method_3", True),
        ("thms_impls_base/test_method_4", True),
        ("thms_impls_base/test_method_5", False)
    ]
)
def test_test_method(filename_base, expected):
    thms_impls_base = ThmsImplsBase(types=TYPES, is_thm=True)
    block = read_file(f"{filename_base}.txt")
    parent = etree.Element("p")
    parent.text = block

    has_match = thms_impls_base.test(parent, block)
    assert has_match == expected


@pytest.mark.parametrize(
    "filename_base",
    [
        ("thms_impls_base/gen_thm_heading_md_1"),
        ("thms_impls_base/gen_thm_heading_md_2"),
        ("thms_impls_base/gen_thm_heading_md_3"),
        ("thms_impls_base/gen_thm_heading_md_4"),
        ("thms_impls_base/gen_thm_heading_md_5"),
        ("thms_impls_base/gen_thm_heading_md_6"),
        # test that curly braces (e.g. from LaTeX) don't interfere with parsing
        ("thms_impls_base/gen_thm_heading_md_7"),
        # test that thm headings with no trailing newlines are not parsed
        ("thms_impls_base/gen_thm_heading_md_8")
    ]
)
def test_gen_thm_heading_md(filename_base):
    thms_impls_base = ThmsImplsBase(types=TYPES, is_thm=True)
    block = read_file(f"{filename_base}.txt")
    parent = etree.Element("p")
    parent.text = block
    has_match = thms_impls_base.test(parent, block)

    expected = read_file(f"{filename_base}_expected.txt")
    # if nothing detected, check that indeed nothing is supposed to change
    if not has_match:
        print(block, end="\n")
        assert block == expected
    else:
        actual = thms_impls_base.gen_thm_heading_md(block)
        print(actual, end="\n")
        assert actual == expected


def test_prepend_thm_heading_md():
    # test when there's no `<p>` child
    elem = etree.Element("div")
    subelem = etree.SubElement(elem, "span")
    subelem.text = "not a para!"
    ThmsImplsBase.prepend_thm_heading_md(elem, "heading.")
    assert etree.tostring(elem, encoding="unicode") \
            == "<div><p>heading.</p> <span>not a para!</span></div>"

    # test when there is a `<p>` child
    elem = etree.Element("div")
    elem.text = "outside para"
    para_1 = etree.SubElement(elem, "p")
    para_1 .text = "inside para 1"
    para_2 = etree.SubElement(elem, "p")
    para_2.text = "inside para 2"
    ThmsImplsBase.prepend_thm_heading_md(elem, "sd")
    assert elem.text == "outside para"
    assert para_1.text == "sd inside para 1" # should prepend into this only
    assert para_2.text == "inside para 2"
