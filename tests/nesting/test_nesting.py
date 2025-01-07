import pytest

from markdown_environments import *
from ..tests_util import run_extension_test


@pytest.mark.parametrize("filename_base", ["nesting/success_1"])
def test_nesting(filename_base):
    run_extension_test(
        [
            CaptionedFigureExtension(
                html_class="md-captioned-figure", caption_html_class="md-captioned-figure__caption"
            ),
            CitedBlockquoteExtension(
                html_class="md-cited-blockquote", citation_html_class="md-cited-blockquote__citation"
            ),
            DivExtension(
                types={
                    "textbox": {"html_class": "md-textbox last-child-no-mb border--1px"}
                }
            ),
            DropdownExtension(
                types = {
                    "dropdown": {"html_class": "md-dropdown--default"}
                },
                html_class="md-dropdown",
                summary_html_class="md-dropdown__summary last-child-no-mb",
                content_html_class="md-dropdown__content last-child-no-mb"
            ),
            ThmsExtension(
                div_config={
                    "types": {
                        "thm": {
                            "thm_type": "Theorem",
                            "html_class": "md-textbox last-child-no-mb border--4px border--custom-orange-deep-light",
                            "thm_counter_incr": "0,0,1"
                        }
                    }
                },
                dropdown_config={
                    "types": {
                        "pf": {
                            "thm_type": "Proof",
                            "html_class": "md-dropdown--pf",
                            "thm_name_overrides_thm_heading": True
                        }
                    },
                    "html_class": "md-dropdown",
                    "summary_html_class": "md-dropdown__summary last-child-no-mb",
                    "content_html_class": "md-dropdown__content last-child-no-mb"
                },
                thm_heading_config={
                    "html_class": "md-thm-heading",
                    "emph_html_class": "md-thm-heading__emph"
                }
            )
        ],
        filename_base
    )
