r"""
The base Markdown syntax defined by this extension is::

    \begin{...}
    ...
    \end{...}

Important:
    - Each `\\begin{}` must be on its own line with a blank line above, and each `\\end{}` must be on its own line with a blank line below.
    - In general, don't expect nesting environments to work consistently unless they are of different types; the behavior is undefined otherwise. This includes not being able to nest environments that are themselves "nested" or "multiple-layered" (`Dropdown`s and `NestedEnv`s) within themselves even if they are different "types" in the config, e.g. exercise vs proof dropdowns. The only exception currently is that `Div` environments *can* be nested within other `Div`s of different config "types", but I would still recommend avoiding such complicated setups if you can avoid it. For a full list of what combinations work and what don't, refer to `tests/nesting/docs_behavior_1_expected.txt` inside the source repo.
"""

from .div import DivExtension
from .dropdown import DropdownExtension
from .nested_env import NestedEnvExtension
from .thms import ThmsExtension


__version__ = "1.11.8"
