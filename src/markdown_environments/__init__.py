r"""
The base Markdown syntax defined by this extension is::

    \begin{...}
    ...
    \end{...}

Note that there must be a blank line before each `\\begin{}` and after each `\\end{}`.
"""

from .captioned_figure import CaptionedFigureExtension
from .cited_blockquote import CitedBlockquoteExtension
from .div import DivExtension
from .dropdown import DropdownExtension
from .thms import ThmsExtension


__version__ = "1.0.1"
