# Requires python 3.6 or above
from typing import NamedTuple
import numpy as np
class Barrier(NamedTuple):
    start: np.ndarray
    end: np.ndarray