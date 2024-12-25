from markdown_environments.captioned_figure import *
from ..util import extension_test


def test_captioned_figure():
    extension_test(
        CaptionedFigureExtension(),
        "captioned_figure/1",
        "test_captioned_figure.test_captioned_figure() failed (1)"
    )

    extension_test(
        CaptionedFigureExtension(html_class="md-captioned-figure", caption_html_class="md-captioned-figure__caption"),
        "captioned_figure/2",
        "test_captioned_figure.test_captioned_figure() failed (2)"
    )


def test_captioned_figure_fail():
    extension_test(
        CaptionedFigureExtension(),
        "captioned_figure/fail_1",
        "test_captioned_figure.test_captioned_figure_fail() failed (1)"
    )

    extension_test(
        CaptionedFigureExtension(),
        "captioned_figure/fail_2",
        "test_captioned_figure.test_captioned_figure_fail() failed (2)"
    )

    extension_test(
        CaptionedFigureExtension(),
        "captioned_figure/fail_3",
        "test_captioned_figure.test_captioned_figure_fail() failed (3)"
    )

    extension_test(
        CaptionedFigureExtension(),
        "captioned_figure/fail_4",
        "test_captioned_figure.test_captioned_figure_fail() failed (4)"
    )
