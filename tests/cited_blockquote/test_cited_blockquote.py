from markdown_environments.cited_blockquote import *
from ..util import extension_test


def test_cited_blockquote():
    extension_test(
        CitedBlockquoteExtension(),
        "cited_blockquote/1.txt", "cited_blockquote/1.html",
        "test_cited_blockquote.test_cited_blockquote() failed (1)"
    )

    extension_test(
        CitedBlockquoteExtension(html_class="md-cited-blockquote", citation_html_class="md-cited-blockquote__citation"),
        "cited_blockquote/1.txt", "cited_blockquote/2.html",
        "test_cited_blockquote.test_cited_blockquote() failed (2)"
    )


def test_cited_blockquote_fail():
    extension_test(
        CitedBlockquoteExtension(),
        "cited_blockquote/fail_1.txt", "cited_blockquote/fail_1.html",
        "test_cited_blockquote.test_cited_blockquote_fail() failed (1)"
    )

    extension_test(
        CitedBlockquoteExtension(),
        "cited_blockquote/fail_2.txt", "cited_blockquote/fail_2.html",
        "test_cited_blockquote.test_cited_blockquote_fail() failed (2)"
    )

    extension_test(
        CitedBlockquoteExtension(),
        "cited_blockquote/fail_3.txt", "cited_blockquote/fail_3.html",
        "test_cited_blockquote.test_cited_blockquote_fail() failed (3)"
    )

    extension_test(
        CitedBlockquoteExtension(),
        "cited_blockquote/fail_4.txt", "cited_blockquote/fail_4.html",
        "test_cited_blockquote.test_cited_blockquote_fail() failed (4)"
    )
