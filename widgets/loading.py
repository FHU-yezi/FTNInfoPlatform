from functools import partial
from typing import Callable

from pywebio.output import put_loading

put_green_loading: Callable = partial(put_loading, color="success")
