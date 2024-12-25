from markdown_environments.dropdown import *
from ..util import extension_test


TYPES = {
    "default": {},
    "O_O": {
        "html_class": "lmao, even"
    }
}


def test_dropdown():
    extension_test(
        DropdownExtension(types=TYPES),
        "dropdown/1",
        "test_dropdown.test_dropdown() failed (1)"
    )

    extension_test(
        DropdownExtension(
            html_class="phd-dropdown",
            summary_html_class="md-dropdown__summary",
            content_html_class="md-dropdown__content",
            types=TYPES
        ),
        "dropdown/2",
        "test_dropdown.test_dropdown() failed (2)"
    )


def test_dropdown_fail():
    extension_test(
        DropdownExtension(),
        "dropdown/fail_1",
        "test_dropdown.test_dropdown_fail() failed (1)"
    )

    extension_test(
        DropdownExtension(types=TYPES),
        "dropdown/fail_2",
        "test_dropdown.test_dropdown_fail() failed (2)"
    )

    extension_test(
        DropdownExtension(types=TYPES),
        "dropdown/fail_3",
        "test_dropdown.test_dropdown_fail() failed (3)"
    )

    extension_test(
        DropdownExtension(types=TYPES),
        "dropdown/fail_4",
        "test_dropdown.test_dropdown_fail() failed (4)"
    )

    extension_test(
        DropdownExtension(types=TYPES),
        "dropdown/fail_5",
        "test_dropdown.test_dropdown_fail() failed (5)"
    )
