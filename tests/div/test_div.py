import pytest

from markdown_environments import DivExtension
from ..tests_util import run_extension_test


TYPES = {
    "default": {},
    "div2": {
        "html_class": "lol mb-0"
    }
}


@pytest.mark.parametrize(
    "extension, filename_base",
    [
        (DivExtension(types=TYPES), "div/success_1"),
        (DivExtension(types=TYPES, html_class="md-div"), "div/success_2"),
        (DivExtension(), "div/fail_1"),
        (DivExtension(types=TYPES), "div/fail_2"),
        (DivExtension(types=TYPES), "div/fail_3")
    ]
)
def test_div(extension, filename_base):
    run_extension_test([extension], filename_base)
