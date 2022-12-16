from argparse import _SubParsersAction, Namespace
from multiprocessing import Queue
from typing import Callable, NoReturn, Tuple

from ..config import Config

RunFn = Callable[[Queue, Namespace, Config], NoReturn]
SetupFn = Callable[[_SubParsersAction], Tuple[str, RunFn]]
