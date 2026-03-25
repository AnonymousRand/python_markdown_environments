r"""
The base Markdown syntax defined by this extension is::

    \begin{...}
    ...
    \end{...}

Important:
    - Each `\\begin{}` must be on its own line with a blank line above, and each `\\end{}` must be on its own line with a blank line below.
    - Only nesting different types of environments works; nesting the same environment within itself does not.
"""

from .captioned_figure import CaptionedFigureExtension
from .cited_blockquote import CitedBlockquoteExtension
from .div import DivExtension
from .dropdown import DropdownExtension
from .thms import ThmsExtension


__version__ = "1.9.8"
