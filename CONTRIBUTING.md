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

Run `hatch test` in the project's root directory. Tests are located in `tests/`; carefully modify tests if adding new features.

## Generating Documentation

Module, class, and function documentation are generated automatically from docstrings by `sphinx.ext.autodoc`. To update the documentation, simply update the docstrings and Read the Docs will automatically run Sphinx to generate the documentation when I create a new release. Alternatively, to generate documentation manually for testing, run `make html` in the `docs/` directory and then open `docs/_build/html/index.html` in a browser.

Docstrings use Google style, although a sprinkle of reStructuredText/Sphinx is used for things like controlling syntax highlighting on code blocks.
