import sys
from pathlib import Path

sys.path.insert(0, str(Path("..", "src").resolve()))

project = "Markdown-Environments"
copyright = "2025, AnonymousRand"
author = "AnonymousRand"

extensions = [
    #"autoapi.extension",
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode"
]
#autoapi_dirs = ["../src/"]  # location to parse for API reference
#autoapi_options = [
#    "imported-members",
#    "members",
#    "show-inheritance",
#    "show-module-summary",
#    "special-members"
#]
html_theme = "sphinx_rtd_theme"
source_suffix = [".md", ".rst"]
