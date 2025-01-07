import pytest

from markdown_environments import CaptionedFigureExtension
from ..tests_util import run_extension_test


@pytest.mark.parametrize(
    "extension, filename_base",
    [
        (CaptionedFigureExtension(), "captioned_figure/success_1"),
        (
            CaptionedFigureExtension(html_class="captioned-figure", caption_html_class="captioned-figure__caption"),
            "captioned_figure/success_2",
        ),
        (CaptionedFigureExtension(), "captioned_figure/fail_1"),
        (CaptionedFigureExtension(), "captioned_figure/fail_2"),
        (CaptionedFigureExtension(), "captioned_figure/fail_3"),
        (CaptionedFigureExtension(), "captioned_figure/fail_4")
    ]
)
def test_captioned_figure(extension, filename_base):
    run_extension_test([extension], filename_base)
