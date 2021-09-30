import random as _random
import time as _time
from random import randrange as _randrange


# Returns random index that can be chosen as start index for interval inside array
def get_random_start(interval_length, all_length):
    _random.seed(_time.time_ns())
    free_space = all_length - interval_length
    start = _randrange(free_space - 1)
    return start
