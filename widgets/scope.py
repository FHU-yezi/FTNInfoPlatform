from pywebio.output import use_scope
from functools import partial
from typing import Callable

use_autoclear_scope: Callable = partial(use_scope, clear=True)
