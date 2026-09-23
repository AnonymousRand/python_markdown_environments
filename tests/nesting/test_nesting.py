import pytest

from markdown_environments import *
from ..tests_utils import run_extension_test


@pytest.mark.parametrize("filename_base", ["nesting/docs_behavior_1"])
def test_nesting(filename_base):
    run_extension_test(
        [
            DivExtension(
                types={
                    "div":  {"html_class": "div"},
                    "div2": {"html_class": "div2"}
                }
            ),
            DropdownExtension(
                types={
                    "dropdown":  {"html_class": "dropdown"},
                    "dropdown2": {"html_class": "dropdown2"}
                }
            ),
            NestedEnvExtension(
                types={
                    "nested_env": {
                        "html_tag": "div",
                        "inner": "inner",
                        "inner_html_tag": "span",
                        "inner_pos": "start"
                    },
                    "nested_env2": {
                        "html_tag": "blockquote",
                        "inner": "inner2",
                        "inner_html_tag": "cite",
                        "inner_pos": "end"
                    }
                }
            ),
            ThmsExtension(
                div_config={
                    "types": {
                        "div_thm":  {"thm_type": "Div Thm"},
                        "div_thm2": {"thm_type": "Div Thm 2"},
                    }
                },
                dropdown_config={
                    "types": {
                        "dropdown_thm":  {"thm_type": "Dropdown Thm"},
                        "dropdown_thm2": {"thm_type": "Dropdown Thm 2"},
                    }
                }
            )
        ],
        filename_base
    )
