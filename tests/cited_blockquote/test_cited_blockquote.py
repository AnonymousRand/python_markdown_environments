import pytest

from markdown_environments import CitedBlockquoteExtension
from ..tests_util import run_extension_test


@pytest.mark.parametrize(
    "extension, filename_base",
    [
        (CitedBlockquoteExtension(), "cited_blockquote/success_1"),
        (
            CitedBlockquoteExtension(html_class="cited-blockquote", citation_html_class="cited-blockquote__citation"),
            "cited_blockquote/success_2"
        ),
        (CitedBlockquoteExtension(), "cited_blockquote/fail_1"),
        (CitedBlockquoteExtension(), "cited_blockquote/fail_2"),
        (CitedBlockquoteExtension(), "cited_blockquote/fail_3"),
        (CitedBlockquoteExtension(), "cited_blockquote/fail_4")
    ]
)
def test_cited_blockquote(extension, filename_base):
    run_extension_test([extension], filename_base)
