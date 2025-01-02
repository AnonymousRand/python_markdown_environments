import pytest

from markdown_environments import ThmsExtension
from ...util import run_extension_test


@pytest.mark.parametrize(
    "extension, filename_base",
    [
        (ThmsExtension(), "thms/thmcounter/success_1"),
        (ThmsExtension(thm_counter_add_html_elem=True), "thms/thmcounter/success_2"),
        (ThmsExtension(thm_counter_add_html_elem=True, thm_counter_html_id_prefix="foo"), "thms/thmcounter/success_3"),
        (ThmsExtension(thm_counter_add_html_elem=True, thm_counter_html_class=":3"), "thms/thmcounter/success_4"),
        (
            ThmsExtension(
                thm_counter_add_html_elem=True,
                thm_counter_html_id_prefix="alice",
                thm_counter_html_class="bob"),
            "thms/thmcounter/success_5"
        ),
        (ThmsExtension(), "thms/thmcounter/fail_1")
    ]
)
def test_thmcounter(extension, filename_base):
    run_extension_test(extension, filename_base)
