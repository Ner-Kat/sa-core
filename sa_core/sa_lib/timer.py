import time


# Realize timer for measuring time between 'start' and 'stop' actions
class Timer:
    def __init__(self):
        self.__start_time = None
        self.__time_count = None

    # Launches the timer
    def start(self):
        if self.__start_time is not None:
            return

        self.__start_time = time.perf_counter()

    # Stops the timer
    def stop(self):
        if self.__start_time is None:
            return

        elapsed_time = time.perf_counter() - self.__start_time
        self.__start_time = None

        self.__time_count = elapsed_time

    # Returns measured time
    def get_time_count(self):
        return self.__time_count
