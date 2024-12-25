from markdown_environments.thms import *
from ..util import extension_test


def test_counter():
    extension_test(
        ThmsExtension(),
        "thms/thmcounter/1.txt", "thms/thmcounter/1.html",
        "test_thms.test_counter() failed (1)"
    )

    extension_test(
        ThmsExtension(thm_counter_add_html_elem=True),
        "thms/thmcounter/1.txt", "thms/thmcounter/2.html",
        "test_thms.test_counter() failed (2)"
    )

    extension_test(
        ThmsExtension(thm_counter_add_html_elem=True, thm_counter_html_id_prefix="foo"),
        "thms/thmcounter/1.txt", "thms/thmcounter/3.html",
        "test_thms.test_counter() failed (3)"
    )

    extension_test(
        ThmsExtension(thm_counter_add_html_elem=True, thm_counter_html_class=":3"),
        "thms/thmcounter/1.txt", "thms/thmcounter/4.html",
        "test_thms.test_counter() failed (4)"
    )

    extension_test(
        ThmsExtension(thm_counter_add_html_elem=True, thm_counter_html_id_prefix="alice", thm_counter_html_class="bob"),
        "thms/thmcounter/1.txt", "thms/thmcounter/5.html",
        "test_thms.test_counter() failed (5)"
    )


def test_counter_fail():
    extension_test(
        ThmsExtension(),
        "thms/thmcounter/fail_1.txt", "thms/thmcounter/fail_1.html",
        "test_thms.test_counter_fail() failed (1)"
    )
