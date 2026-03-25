# NOTE: this is not a test file! it's for testing utilities
# to find the tests for `utils.py`, go to `tests/utils/`

import markdown


TESTS_PATH = "tests"


def read_file(filename: str) -> str:
    with open(f"{TESTS_PATH}/{filename}", "r") as file:
        contents = file.read()
        # trim off trailing newline, but only one so that actual trailing whitespace we do want is preserved
        if contents.endswith("\n"):
            return contents[:-1]
        else:
            return contents


def run_extension_test(extensions: list, filename_base: str):
    fixture = read_file(f"{filename_base}.txt")
    expected = read_file(f"{filename_base}_expected.txt")
    actual = markdown.markdown(fixture, extensions=extensions)
    # print for debugging (hatch displays stdout on test fail)
    print(actual, end="\n")
    assert actual == expected
