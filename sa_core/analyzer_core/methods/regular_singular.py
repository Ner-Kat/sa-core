from decimal import *
from multiprocessing import Process, Queue

from sa_core.image_handler import *

from .configs.regular_singular_config import *
from ._result_structs import RsRes
from .partial import rs_calc_mp


# Realize Regular-Singular steganalysis method
class RegularSingularMethod:
    def __init__(self, path):
        self.__img = ImageHandler()
        self.__img.load(path)
        self.__imar = self.__img.get_array()

        self.__log = ""
        self.__results = None

    # Returns log of last analysis
    def get_log(self):
        return self.__log

    def execute(self):
        # Clear last analysis data
        self.__results = None
        self.__log = ""

        # Starting log
        path = self.__img.get_path()
        self.__log += "Steganalysis with Regular-Singular method for '" + str(path) + "'\n"

        # Analysis operation
        try:
            r = self.__analyze()
            self.__results = r
        except Exception as ex:
            self.__log += "X\tCritical error: {0}\n".format(repr(ex))
            return None

        # Return and write in log results
        self.__write_results()
        return self.__results

    # Writes results of analysis in log
    def __write_results(self):
        if self.__results is None:
            return

        result = "Detected volume of hidden message: {0:.2%}\n".format(self.__results.volume)
        self.__log += result

    # Main operations of analysis
    def __analyze(self):
        avg_fullness = k = 0

        # Multiprocessing operations data
        d_queues = dict()
        i_queues = dict()
        calcs = []

        # Get image array where inverted all LSB
        inverted_img_array = self.__img.invert_lsb()

        # Calculation of RS result value for each image channel - launching calc processes (RsCalc)
        for channel in ImgChannel:
            d_queues[channel.name] = Queue()
            i_queues[channel.name] = Queue()

            direct_calc = Process(target=rs_calc_mp, args=(d_queues[channel.name], self.__img.get_array(), channel,))
            invert_calc = Process(target=rs_calc_mp, args=(i_queues[channel.name], inverted_img_array, channel,))

            calcs.append(direct_calc)
            calcs.append(invert_calc)

            direct_calc.start()
            invert_calc.start()

        # Getting all RS groups values calculation results
        calc_res = dict()
        for channel in ImgChannel:
            calc_res[channel.name] = (d_queues[channel.name].get(), i_queues[channel.name].get())

        # Waiting for ending of all calculation processes
        for calc in calcs:
            calc.join()

        # Calculation of analysis results
        for channel in ImgChannel:
            self.__log += "|\tChannel: {0}\n".format(channel.name)  # Writing each channel result to log

            # Calc observed volume of hidden data
            p = self.__get_p(calc_res[channel.name][0], calc_res[channel.name][1])
            avg_fullness += p
            k += 1

        # Calculation of single result
        avg_fullness /= k
        r = RsRes(volume=avg_fullness)

        return r

    # Calculation of 'p' value - relative volume of hidden data - by the RS groups values
    def __get_p(self, direct_values, invert_values):
        # Writing to log info about RS groups values
        out_vars = ['RM(p/2)', 'SM(p/2)', 'R_M(p/2)', 'S_M(p/2)', 'RM(1-p/2)', 'SM(1-p/2)', 'R_M(1-p/2)', 'S_M(1-p/2)']
        out_values = [*direct_values, *invert_values]
        out_line = "".join(["|\t\t{0}: {1}\n".format(out_vars[i], out_values[i]) for i in range(8)])
        self.__log += out_line

        #
        # Main calc operation

        d0 = direct_values[0] - direct_values[1]
        d0i = direct_values[2] - direct_values[3]
        d1 = invert_values[0] - invert_values[1]
        d1i = invert_values[2] - invert_values[3]

        self.__log += "|\t\td0 = {0}; d0i = {1}; d1 = {2}; d1i = {3}\n".format(d0, d0i, d1, d1i)

        a = (d1 + d0) * 2
        b = d0i - d1i - d1 - 3 * d0
        c = d0 - d0i

        D = Decimal(b ** 2 - 4 * a * c)

        if D < 0:
            x1 = x2 = min_x = 0
        elif D == 0:
            x1 = x2 = min_x = - (b / 2 * a)
        else:
            x1 = Decimal((-b + Decimal.sqrt(D)) / (2 * a))
            x2 = Decimal((-b - Decimal.sqrt(D)) / (2 * a))

            if abs(x1) < abs(x2):
                min_x = x1
            else:
                min_x = x2

        p = Decimal(min_x / (min_x - Decimal(0.5)))

        self.__log += "|\t\ta = {0}; b = {1}; c = {2}; D = {3}\n".format(a, b, c, D)
        self.__log += ("|\t\tx1 = {0:.5}; x2 = {1:.5}; min_x = {2:.5}; p = {3:.5}\n"
                       .format(float(x1), float(x2), float(min_x), p))

        return max(p, Decimal(0.0))
