import pytest
import xml.etree.ElementTree as etree

from markdown_environments.mixins import ThmMixin
from ...util import read_file


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


class ThmMixinImpl(ThmMixin):
    def get_types(self):
        return self.types

    def get_is_thm(self):
        return self.is_thm

    def get_type_opts(self):
        return self.type_opts

    def get_start_re(self):
        return self.start_re

    def get_end_re(self):
        return self.end_re

    def get_start_re_choices(self):
        return self.start_re_choices

    def get_end_re_choices(self):
        return self.end_re_choices


@pytest.mark.parametrize("is_thm", [False, True])
def test_init_thm(is_thm):
    thm_mixin_impl = ThmMixinImpl()
    expected_start_re_choices = {}
    expected_end_re_choices = {}
    for typ in TYPES:
        if is_thm:
            expected_start_re_choices[typ] = rf"^\\begin{{{typ}}}(?:\[(.+?)\])?(?:{{(.+?)}})?"
        else:
            expected_start_re_choices[typ] = rf"^\\begin{{{typ}}}"
        expected_end_re_choices[typ] = rf"^\\end{{{typ}}}"

    thm_mixin_impl.init_thm(types=TYPES, is_thm=is_thm)
    assert thm_mixin_impl.get_types() == TYPES
    assert thm_mixin_impl.get_is_thm() == is_thm
    assert thm_mixin_impl.get_type_opts() is None
    assert thm_mixin_impl.get_start_re() is None
    assert thm_mixin_impl.get_end_re() is None
    assert thm_mixin_impl.get_start_re_choices() == expected_start_re_choices
    assert thm_mixin_impl.get_end_re_choices() == expected_end_re_choices


def set_up_functionality_tests(is_thm, input_filename) -> tuple[ThmMixinImpl, etree.Element, str, bool]:
    thm_mixin_impl = ThmMixinImpl()
    thm_mixin_impl.init_thm(types=TYPES, is_thm=is_thm)
    block = read_file(input_filename)
    parent = etree.Element("p")
    parent.text = block
    test_res = thm_mixin_impl.test(parent, block)
    return thm_mixin_impl, parent, block, test_res


@pytest.mark.parametrize(
    "input_filename, expected_type, expected_test_res",
    [
        ("mixins/thm_mixin/test_1.txt", "thm", True),
        ("mixins/thm_mixin/test_2.txt", "thm", True),
        ("mixins/thm_mixin/test_3.txt", r"thm\\\*", True),
        ("mixins/thm_mixin/test_4.txt", "lem", True),
        ("mixins/thm_mixin/test_5.txt", "", False),
    ]
)
def test_test(input_filename, expected_type, expected_test_res):
    thm_mixin_impl, _, _, test_res = set_up_functionality_tests(is_thm=True, input_filename=input_filename)
    assert test_res == expected_test_res
    if expected_test_res:
        assert thm_mixin_impl.get_type_opts() == TYPES[expected_type]
        assert thm_mixin_impl.get_start_re() == thm_mixin_impl.get_start_re_choices()[expected_type]
        assert thm_mixin_impl.get_end_re() == thm_mixin_impl.get_end_re_choices()[expected_type]


@pytest.mark.parametrize(
    "is_thm, filename_base",
    [
        (False, "mixins/thm_mixin/gen_thm_heading_md_1"),
        (True, "mixins/thm_mixin/gen_thm_heading_md_2"),
        (True, "mixins/thm_mixin/gen_thm_heading_md_3"),
        (True, "mixins/thm_mixin/gen_thm_heading_md_4"),
        (True, "mixins/thm_mixin/gen_thm_heading_md_5"),
        (True, "mixins/thm_mixin/gen_thm_heading_md_6"),
        (True, "mixins/thm_mixin/gen_thm_heading_md_7"),
    ]
)
def test_gen_thm_heading_md(is_thm, filename_base):
    thm_mixin_impl, _, block, _ = set_up_functionality_tests(
        is_thm=is_thm,
        input_filename=f"{filename_base}.txt"
    )
    expected = read_file(f"{filename_base}_expected.txt")
    actual = thm_mixin_impl.gen_thm_heading_md(block)
    print(actual, end="\n\n")
    assert actual == expected


@pytest.mark.parametrize(
    "is_thm, filename_base",
    [
        (False, "mixins/thm_mixin/prepend_thm_heading_md_1"),
        (True, "mixins/thm_mixin/prepend_thm_heading_md_2")
    ]
)
def test_prepend_thm_heading_md(is_thm, filename_base):
    thm_mixin_impl, parent, _, _ = set_up_functionality_tests(
        is_thm=is_thm,
        input_filename=f"{filename_base}.txt"
    )
    expected = read_file(f"{filename_base}_expected.txt")
    thm_mixin_impl.prepend_thm_heading_md(parent, "sd")
    actual = etree.tostring(parent, encoding="unicode")
    print(actual, end="\n\n")
    assert actual == expected
