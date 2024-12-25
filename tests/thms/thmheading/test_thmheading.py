from markdown_environments.thms import *
from ...util import extension_test


def test_thmheading():
    extension_test(
        ThmsExtension(),
        "thms/thmheading/1",
        "test_thms.test_thmheading() failed (1)"
    )

    extension_test(
        ThmsExtension(),
        "thms/thmheading/2",
        "test_thms.test_thmheading() failed (2)"
    )

    extension_test(
        ThmsExtension(),
        "thms/thmheading/3",
        "test_thms.test_thmheading() failed (3)"
    )

    extension_test(
        ThmsExtension(),
        "thms/thmheading/4",
        "test_thms.test_thmheading() failed (4)"
    )
    
#    extension_test(
#        ThmsExtension(thm_heading_html_class=""),
#        "thms/thmheading/5",
#        "test_thms.test_thmheading() failed (5)"
#    )


def test_thmheading_fail():
    extension_test(
        ThmsExtension(),
        "thms/thmheading/fail_1",
        "test_thms.test_thmheading_fail() failed (1)"
    )
