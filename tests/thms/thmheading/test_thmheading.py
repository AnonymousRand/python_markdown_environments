from markdown_environments.thms import *
from ...util import extension_test


def test_thmheading():
    extension_test(
        ThmsExtension(),
        "thms/thmheading/1.txt", "thms/thmheading/1.html",
        "test_thms.test_thmheading() failed (1)"
    )

    extension_test(
        ThmsExtension(),
        "thms/thmheading/2.txt", "thms/thmheading/2.html",
        "test_thms.test_thmheading() failed (2)"
    )

    extension_test(
        ThmsExtension(),
        "thms/thmheading/3.txt", "thms/thmheading/3.html",
        "test_thms.test_thmheading() failed (3)"
    )

    extension_test(
        ThmsExtension(),
        "thms/thmheading/4.txt", "thms/thmheading/4.html",
        "test_thms.test_thmheading() failed (4)"
    )
    # TODO: test with configs


def test_thmheading_fail():
    extension_test(
        ThmsExtension(),
        "thms/thmheading/fail_1.txt", "thms/thmheading/fail_1.html",
        "test_thms.test_thmheading_fail() failed (1)"
    )
