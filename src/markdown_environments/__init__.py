r"""
The base Markdown syntax defined by this extension is::

    \begin{...}
    ...
    \end{...}

Important:
    - There must be a blank line before each `\\begin{}` and after each `\\end{}`.
    - Only nested different types of environments works; nesting the same environment within itself does not.
"""

from .captioned_figure import CaptionedFigureExtension
from .cited_blockquote import CitedBlockquoteExtension
from .div import DivExtension
from .dropdown import DropdownExtension
from .thms import ThmsExtension


__version__ = "1.2.0"
