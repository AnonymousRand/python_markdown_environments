import markdown


TESTS_PATH = "tests"


def read_file(filename: str) -> str:
    with open(f"{TESTS_PATH}/{filename}", "r") as file:
        return file.read().rstrip("\n")


def extension_test(
    extension: markdown.extensions.Extension, fixture_filename: str,
    expected_filename: str, error_msg: str
):
    fixture = read_file(fixture_filename)
    expected = read_file(expected_filename)
    actual = markdown.markdown(fixture, extensions=[extension])
    # print for debugging (hatch display stdout on test fail)
    print(actual)
    print()
    assert actual == expected, error_msg
