from argparse import _SubParsersAction, Namespace
from multiprocessing import Queue
from typing import Callable, NoReturn, Tuple


RunFn = Callable[[Queue, Namespace], NoReturn]
SetupFn = Callable[[_SubParsersAction], Tuple[str, RunFn]]
