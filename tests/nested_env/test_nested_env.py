import pytest

from markdown_environments import NestedEnvExtension
from ..tests_utils import run_extension_test


@pytest.mark.parametrize(
    "extension, filename_base",
    [
        (
            NestedEnvExtension(types={
                "captioned_figure": {
                    "html_tag": "figure",
                    "inner": "caption",
                    "inner_html_tag": "figcaption",
                    "inner_pos": "end"
                }
            }),
            "nested_env/success_1"
        ),
        (
            NestedEnvExtension(types={
                "captioned_figure": {
                    "html_tag": "figure",
                    "html_class": "captioned-figure",
                    "inner": "caption",
                    "inner_html_tag": "figcaption",
                    "inner_html_class": "captioned-figure__caption",
                    "inner_pos": "start"
                }
            }),
            "nested_env/success_2",
        ),
        (
            NestedEnvExtension(html_class="class-1 class-2", types={
                "cited_blockquote": {
                    "html_tag": "blockquote",
                    "html_class": "class-3 class-4",
                    "inner": "citation",
                    "inner_html_tag": "cite",
                    "inner_html_class": "hewwo",
                    "inner_pos": "end_outside"
                }
            }),
            "nested_env/success_3",
        ),
        (
            NestedEnvExtension(html_class="class-1 class-2", types={
                "cited_blockquote": {
                    "html_tag": "blockquote",
                    "inner": "citation",
                    "inner_html_tag": "cite",
                    "inner_html_class": "hewwo",
                    "inner_pos": "end_outside"
                },
                "random": {
                    "html_tag": "div",
                    "html_class": "outer-is-div",
                    "inner": "random_inner",
                    "inner_html_tag": "div",
                    "inner_html_class": "inner-is-also-div",
                    "inner_pos": "start"
                }
            }),
            "nested_env/success_4",
        ),
        (
            NestedEnvExtension(types={
                "captioned_figure": {
                    "html_tag": "figure",
                    "inner": "caption",
                    "inner_html_tag": "figcaption",
                    "inner_pos": "end"
                }
            }),
            "nested_env/fail_1"
        ),
        (
            NestedEnvExtension(types={
                "captioned_figure": {
                    "html_tag": "figure",
                    "inner": "caption",
                    "inner_html_tag": "figcaption",
                    "inner_pos": "end"
                }
            }),
            "nested_env/fail_2"
        ),
        (
            NestedEnvExtension(types={
                "captioned_figure": {
                    "html_tag": "figure",
                    "inner": "caption",
                    "inner_html_tag": "figcaption",
                    "inner_pos": "end"
                }
            }),
            "nested_env/fail_3"
        ),
        (
            NestedEnvExtension(types={
                "captioned_figure": {
                    "html_tag": "figure",
                    "inner": "caption",
                    "inner_html_tag": "figcaption",
                    "inner_pos": "end"
                }
            }),
            "nested_env/fail_4"
        )
    ]
)
def test_nested_env(extension, filename_base):
    run_extension_test([extension], filename_base)


@pytest.mark.parametrize(
    "config, expected_exception, expected_error_text",
    [
        (
            {
                "types": {
                    "missing_html_tag": {
                        "inner": "caption",
                        "inner_html_tag": "figcaption",
                        "inner_pos": "end"
                    }
                }
            },
            KeyError,
            (
                "nested env: missing_html_tag.html_tag, missing_html_tag.inner, "
                "missing_html_tag.inner_html_tag, or missing_html_tag.inner_pos key was not defined"
            )
        ),
        (
            {
                "types": {
                    "missing_inner": {
                        "html_tag": "figure",
                        "inner_html_tag": "figcaption",
                        "inner_pos": "end"
                    }
                }
            },
            KeyError,
            (
                "nested env: missing_inner.html_tag, missing_inner.inner, "
                "missing_inner.inner_html_tag, or missing_inner.inner_pos key was not defined"
            )
        ),
        (
            {
                "types": {
                    "missing_inner_html_tag": {
                        "html_tag": "figure",
                        "inner": "caption",
                        "inner_pos": "end"
                    }
                }
            },
            KeyError,
            (
                "nested env: missing_inner_html_tag.html_tag, missing_inner_html_tag.inner, "
                "missing_inner_html_tag.inner_html_tag, or missing_inner_html_tag.inner_pos key "
                "was not defined"
            )
        ),
        (
            {
                "types": {
                    "missing_inner_pos": {
                        "html_tag": "figure",
                        "inner": "caption",
                        "inner_html_tag": "figcaption"
                    }
                }
            },
            KeyError,
            (
                "nested env: missing_inner_pos.html_tag, missing_inner_pos.inner, "
                "missing_inner_pos.inner_html_tag, or missing_inner_pos.inner_pos key "
                "was not defined"
            )
        ),
        (
            {
                "types": {
                    "missing_multiple": {
                        "html_tag": "figure",
                        "inner_pos": "end"
                    }
                }
            },
            KeyError,
            (
                "nested env: missing_multiple.html_tag, missing_multiple.inner, "
                "missing_multiple.inner_html_tag, or missing_multiple.inner_pos key was not defined"
            )
        ),
        (
            {
                "types": {
                    "bad_inner_pos_value": {
                        "html_tag": "figure",
                        "inner": "caption",
                        "inner_html_tag": "figcaption",
                        "inner_pos": "mrrp"
                    }
                }
            },
            ValueError,
            (
                "nested env: bad_inner_pos_value.inner_pos is \"mrrp\", which is not one of "
                "`start`, `end`, or `end_outside`"
            )
        )
    ]
)
def test_nested_env_errors(config, expected_exception, expected_error_text):
    with pytest.raises(expected_exception) as e:
        _ = NestedEnvExtension(**config)
    print(f"captured exception: {e.value}")
    assert expected_error_text in str(e.value)
