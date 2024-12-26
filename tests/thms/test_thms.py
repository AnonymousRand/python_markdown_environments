import pytest

from markdown_environments.thms import *
from ..util import run_extension_test


DIV_TYPES = {
    "lem": {
        "thm_type": "Lemma",
        "html_class": "md-textbox md-textbox-defn last-child-no-mb",
        "thm_counter_incr": "0,0,1",
        "thm_heading_punct": ":"
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
        "thm_heading_punct": " -",
        "use_punct_if_nothing_after": False
    },
    "pf": {
        "thm_type": "Proof",
        "html_class": "md-dropdown-pf",
        "thm_counter_incr": "0,0,150",
        "thm_name_overrides_heading": True
    }
}


@pytest.mark.parametrize(
    "extension, filename_base",
    [
        (ThmsExtension(div_types=DIV_TYPES, dropdown_types=DROPDOWN_TYPES), "thms/success_1"),
        (ThmsExtension(div_types=DIV_TYPES, dropdown_types=DROPDOWN_TYPES), "thms/success_2"),
        (ThmsExtension(div_types=DIV_TYPES, dropdown_types=DROPDOWN_TYPES), "thms/success_3"),
        (ThmsExtension(div_types=DIV_TYPES, dropdown_types=DROPDOWN_TYPES), "thms/success_4"),
        (ThmsExtension(div_types=DIV_TYPES, dropdown_types=DROPDOWN_TYPES), "thms/success_5"),
        (ThmsExtension(div_types=DIV_TYPES, dropdown_types=DROPDOWN_TYPES), "thms/success_6"),
        (
            ThmsExtension(
                div_html_class="divs", div_types=DIV_TYPES,
                dropdown_html_class="dropdowns", dropdown_summary_html_class="dropdown-summaries",
                dropdown_content_html_class="dropdown-content", dropdown_types=DROPDOWN_TYPES,
                thm_counter_add_html_elem=True, thm_counter_html_id_prefix="counter-", thm_counter_html_class="counter",
                thm_heading_html_class="heading", thm_type_html_class="thm-type"
            ),
            "thms/success_7"
        ),
        (ThmsExtension(), "thms/fail_1"),
        (ThmsExtension(), "thms/fail_2"),
        (ThmsExtension(), "thms/fail_3")
    ]
)
def test_thms(extension, filename_base):
    run_extension_test(extension, filename_base)
