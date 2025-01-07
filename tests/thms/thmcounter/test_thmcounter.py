import pytest

from markdown_environments import ThmsExtension
from ...tests_util import run_extension_test


@pytest.mark.parametrize(
    "extension, filename_base",
    [
        # docs example
        (ThmsExtension(), "thms/thmcounter/success_1"),
        (ThmsExtension(thm_counter_config={"add_html_elem": True}), "thms/thmcounter/success_2"),
        (
            ThmsExtension(thm_counter_config={"add_html_elem": True, "html_id_prefix": "foo"}),
            "thms/thmcounter/success_3"
        ),
        (
            ThmsExtension(thm_counter_config={"add_html_elem": True, "html_class": ":3"}),
            "thms/thmcounter/success_4"
        ),
        (
            ThmsExtension(thm_counter_config={"add_html_elem": True, "html_id_prefix": "alice", "html_class": "bob"}),
            "thms/thmcounter/success_5"
        ),
        (ThmsExtension(), "thms/thmcounter/fail_1")
    ]
)
def test_thmcounter(extension, filename_base):
    run_extension_test([extension], filename_base)
