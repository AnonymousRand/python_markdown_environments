import pytest

from markdown_environments import ThmsExtension
from ...tests_utils import run_extension_test


DIV_TYPES = {
    "thm": {
        "thm_type": "Theorem",
        "thm_counter_incr": "0,0,1"
    },
    "lem": {
        "thm_type": "Lemma",
        "thm_counter_incr": "0,0,1"
    }
}


@pytest.mark.parametrize(
    "extension, filename_base",
    [
        # test for thm headings
        (ThmsExtension(div_config={"types": DIV_TYPES}), "thms/thm_ref/success_1"),
        # test for thm counters
        (ThmsExtension(div_config={"types": DIV_TYPES}), "thms/thm_ref/success_2"),
        # tests both thm headings and thm counters
        (ThmsExtension(div_config={"types": DIV_TYPES}), "thms/thm_ref/success_3"),
        # checks that hidden name for thm counters works inside things like LaTeX `\tag{}`
        (ThmsExtension(div_config={"types": DIV_TYPES}), "thms/thm_ref/success_4")
    ]
)
def test_thm_counter(extension, filename_base):
    run_extension_test([extension], filename_base)
