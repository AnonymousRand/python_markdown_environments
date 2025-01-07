import pytest

from markdown_environments import DropdownExtension
from ..tests_util import run_extension_test


TYPES = {
    "default": {},
    "O_O": {
        "html_class": "lmao, even"
    }
}


@pytest.mark.parametrize(
    "extension, filename_base",
    [
        (DropdownExtension(types=TYPES), "dropdown/success_1"),
        (
            DropdownExtension(
                types=TYPES,
                html_class="phd-dropdown",
                summary_html_class="md-dropdown__summary",
                content_html_class="md-dropdown__content"
            ),
            "dropdown/success_2"
        ),
        (DropdownExtension(), "dropdown/fail_1"),
        (DropdownExtension(types=TYPES), "dropdown/fail_2"),
        (DropdownExtension(types=TYPES), "dropdown/fail_3"),
        (DropdownExtension(types=TYPES), "dropdown/fail_4"),
        (DropdownExtension(types=TYPES), "dropdown/fail_5"),
        (DropdownExtension(types=TYPES), "dropdown/fail_6")
    ]
)
def test_dropdown(extension, filename_base):
    run_extension_test([extension], filename_base)
