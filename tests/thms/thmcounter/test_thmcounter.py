from markdown_environments.thms import *
from ...util import extension_test


def test_thmcounter():
    extension_test(
        ThmsExtension(),
        "thms/thmcounter/1",
        "test_thms.test_thmcounter() failed (1)"
    )

    extension_test(
        ThmsExtension(thm_counter_add_html_elem=True),
        "thms/thmcounter/2",
        "test_thms.test_thmcounter() failed (2)"
    )

    extension_test(
        ThmsExtension(thm_counter_add_html_elem=True, thm_counter_html_id_prefix="foo"),
        "thms/thmcounter/3",
        "test_thms.test_thmcounter() failed (3)"
    )

    extension_test(
        ThmsExtension(thm_counter_add_html_elem=True, thm_counter_html_class=":3"),
        "thms/thmcounter/4",
        "test_thms.test_thmcounter() failed (4)"
    )

    extension_test(
        ThmsExtension(thm_counter_add_html_elem=True, thm_counter_html_id_prefix="alice", thm_counter_html_class="bob"),
        "thms/thmcounter/5",
        "test_thms.test_thmcounter() failed (5)"
    )


def test_thmcounter_fail():
    extension_test(
        ThmsExtension(),
        "thms/thmcounter/fail_1",
        "test_thms.test_thmcounter_fail() failed (1)"
    )
