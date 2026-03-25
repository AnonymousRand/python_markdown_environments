# Contributing

I don't expect this project to be huge, so feel free to drop an issue or pull request on [GitHub](https://github.com/AnonymousRand/python-markdown-environments) to report bugs or suggest features. Running tests and updating documentation before submitting a pull request is appreciated ^^

## Setting Up Development Environment

Install necessary packages in a virtual environment:
```shell
$ mkdir venv
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Running Tests

Run `hatch test` in the project's root directory. Tests are located in `tests/`; carefully modify tests if adding new features. If you are unfamiliar with `hatch`'s tests, here's a brief rundown of how they work:
- Files whose names begin with `file_` or end with `_file` are automatically detected as test drivers, and within them, functions whose names begin with `test_` are run as tests (this is the same behavior as `pytest` since that's what `hatch` uses).
- For each test function, the tests to run (i.e. test files) are passed in via a `@parametrize` decorator.
- Each test corresponds to a pair of test files: the Markdown input `[name].txt` and the expected output `[name]_expected.txt`. For all tests except for those in `tests/utils/`, these filenames are passed to `run_extension_test()` in `tests/tests_utils.py`, so it is imperative that they follow this specific filename format.

(These tests also print out any "incorrect" output, so this can be a good way to test work-in-progress changes without having to set up an actual driver.)

## Generating Documentation

Module, class, and function documentation are generated automatically from docstrings by `sphinx.ext.autodoc`. To update the documentation, simply update the docstrings in the Python source files in `src/`, and Read the Docs will automatically run Sphinx to regenerate the documentation when I create a new release. Alternatively, to generate the documentation manually for testing, run `make html` in the `docs/` directory and then open `docs/_build/html/index.html` in a browser.

Docstrings use Google style, although a sprinkle of reStructuredText/Sphinx style is used for things like controlling syntax highlighting on code blocks.
