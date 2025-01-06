import markdown


TESTS_PATH = "tests"


def read_file(filename: str) -> str:
    with open(f"{TESTS_PATH}/{filename}", "r") as file:
        return file.read().rstrip("\n")


def run_extension_test(extension, filename_base):
    fixture = read_file(f"{filename_base}.txt")
    expected = read_file(f"{filename_base}.html")
    actual = markdown.markdown(fixture, extensions=[extension])
    # print for debugging (hatch displays stdout on test fail)
    print(actual, end="\n\n")
    assert actual == expected
