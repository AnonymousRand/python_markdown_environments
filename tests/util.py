import markdown


TESTS_PATH = "tests"


def read_file(filename: str) -> str:
    with open(f"{TESTS_PATH}/{filename}", "r") as file:
        return file.read().rstrip("\n")


def extension_test(extension: markdown.extensions.Extension, filename_base: str, error_msg: str):
    fixture = read_file(f"{filename_base}.txt")
    expected = read_file(f"{filename_base}.html")
    actual = markdown.markdown(fixture, extensions=[extension])
    # print for debugging (hatch display stdout on test fail)
    print(actual)
    print()
    assert actual == expected, error_msg
