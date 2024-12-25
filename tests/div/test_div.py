from markdown_environments.div import *
from ..util import extension_test


TYPES = {
    "default": {},
    "div2": {
        "html_class": "lol mb-0"
    }
}


def test_div():
    extension_test(
        DivExtension(types=TYPES),
        "div/1.txt", "div/1.html",
        "test_div.test_div() failed (1)"
    )

    extension_test(
        DivExtension(html_class="md-div", types=TYPES),
        "div/1.txt", "div/2.html",
        "test_div.test_div() failed (2)"
    )


def test_div_fail():
    extension_test(
        DivExtension(),
        "div/fail_1.txt", "div/fail_1.html",
        "test_div.test_div_fail() failed (1)"
    )

    extension_test(
        DivExtension(types=TYPES),
        "div/fail_2.txt", "div/fail_2.html",
        "test_div.test_div_fail() failed (2)"
    )

    extension_test(
        DivExtension(types=TYPES),
        "div/fail_3.txt", "div/fail_3.html",
        "test_div.test_div_fail() failed (3)"
    )
