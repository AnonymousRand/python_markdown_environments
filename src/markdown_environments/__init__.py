r"""
The base Markdown syntax defined by this extension is::

    \begin{...}
    ...
    \end{...}

Important:
    - There must be a blank line before each `\\begin{}` and after each `\\end{}`
    - Nesting environments is currently an undefined behavior; it may work with environments of different types but will
      likely not work with environments of the same type
"""

from .captioned_figure import CaptionedFigureExtension
from .cited_blockquote import CitedBlockquoteExtension
from .div import DivExtension
from .dropdown import DropdownExtension
from .thms import ThmsExtension


__version__ = "1.1.0"
