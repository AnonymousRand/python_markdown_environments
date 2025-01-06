import sys
from pathlib import Path

sys.path.insert(0, str(Path("..", "src").resolve()))

project = "Markdown-Environments"
copyright = "2025, AnonymousRand"
author = "AnonymousRand"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode"
]

default_role = "code"           # single backticks render as inline code instead of needing double backticks
#napoleon_custom_sections = [    # custom recognized sections in docstrings
#    "Markdown usage"
#]
source_suffix = [".md", ".rst"] # allows inclusion of `.md` files from project root

html_static_path = ["_static/"]
html_css_files = [
    "css/custom.css",
]
html_theme = "sphinx_rtd_theme"
