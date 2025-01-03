import pytest

from markdown_environments import ThmsExtension
from ..util import run_extension_test


DIV_TYPES = {
    "lem": {
        "thm_type": "Lemma",
        "html_class": "md-textbox md-textbox-defn last-child-no-mb",
        "thm_counter_incr": "0,0,1",
        "thm_punct": ":"
    },
    "thm": {
        "thm_type": "Theorem",
        "html_class": "md-textbox md-textbox-thm last-child-no-mb",
        "thm_counter_incr": "0,1"
    },
    r"thm\\\*": {
        "thm_type": "Theorem",
        "html_class": "md-textbox md-textbox-thm last-child-no-mb",
        "thm_name_overrides_thm_heading": True
    }
}

DROPDOWN_TYPES = {
    "exer": {
        "thm_type": "Exercise",
        "html_class": "md-dropdown-exer",
        "thm_counter_incr": "0,0,1",
        "thm_punct": " -",
        "use_punct_if_nothing_after": False
    },
    "pf": {
        "thm_type": "Proof",
        "html_class": "md-dropdown-pf",
        "thm_counter_incr": "0,0,150",
        "thm_name_overrides_thm_heading": True
    }
}


@pytest.mark.parametrize(
    "extension, filename_base",
    [
        (ThmsExtension(div_config={"types": DIV_TYPES}, dropdown_config={"types": DROPDOWN_TYPES}), "thms/success_1"),
        (ThmsExtension(div_config={"types": DIV_TYPES}, dropdown_config={"types": DROPDOWN_TYPES}), "thms/success_2"),
        (ThmsExtension(div_config={"types": DIV_TYPES}, dropdown_config={"types": DROPDOWN_TYPES}), "thms/success_3"),
        (ThmsExtension(div_config={"types": DIV_TYPES}, dropdown_config={"types": DROPDOWN_TYPES}), "thms/success_4"),
        (ThmsExtension(div_config={"types": DIV_TYPES}, dropdown_config={"types": DROPDOWN_TYPES}), "thms/success_5"),
        (ThmsExtension(div_config={"types": DIV_TYPES}, dropdown_config={"types": DROPDOWN_TYPES}), "thms/success_6"),
        # readme example
        (
            ThmsExtension(
                div_config={
                    "types": {
                        "thm": {
                            "thm_type": "Theorem",
                            "html_class": "md-thm",
                            "thm_counter_incr": "0,0,1"
                        },
                        r"thm\\\*": {
                            "thm_type": "Theorem",
                            "html_class": "md-thm"
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
                            "thm_punct": ":",
                            "use_punct_if_nothing_after": False
                        },
                        "pf": {
                            "thm_type": "Proof",
                            "thm_counter_incr": "0,0,0,1",
                            "thm_name_overrides_thm_heading": True
                        }
                    },
                    "html_class": "md-dropdown",
                    "summary_html_class": "md-dropdown__summary mb-0"
                },
                thm_heading_config={
                    "html_class": "md-thm-heading",
                    "emph_html_class": "md-thm-heading__emph"
                }
            ),
            "thms/success_7"
        ),
        (ThmsExtension(), "thms/fail_1"),
        (ThmsExtension(div_config={"types": DIV_TYPES}, dropdown_config={"types": DROPDOWN_TYPES}), "thms/fail_2"),
        (ThmsExtension(div_config={"types": DIV_TYPES}, dropdown_config={"types": DROPDOWN_TYPES}), "thms/fail_3")
    ]
)
def test_thms(extension, filename_base):
    run_extension_test(extension, filename_base)
