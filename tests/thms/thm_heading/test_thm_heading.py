import pytest

from markdown_environments import ThmsExtension
from ...tests_utils import run_extension_test


@pytest.mark.parametrize(
    "extension, filename_base",
    [
        (ThmsExtension(), "thms/thm_heading/success_1"),
        (ThmsExtension(), "thms/thm_heading/success_2"),
        (ThmsExtension(), "thms/thm_heading/success_3"),
        (ThmsExtension(), "thms/thm_heading/success_4"),
        (ThmsExtension(), "thms/thm_heading/success_5"),
        (
            ThmsExtension(thm_heading_config={
                "html_id_prefix": "defenestrate-", "html_class": "bottom-text", "emph_html_class": "top-text"
            }),
            "thms/thm_heading/success_6"
        ),

        # test that curly braces (e.g. from LaTeX) don't interfere with parsing
        (ThmsExtension(), "thms/thm_heading/success_7"),
        (ThmsExtension(), "thms/thm_heading/fail_1")
    ]
)
def test_thm_heading(extension, filename_base):
    run_extension_test([extension], filename_base)
