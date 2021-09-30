from math import fabs

from sa_core.image_handler import *
from sa_core.sa_math import dct
from sa_core.stego_module import KochZhaoExtractor as KzEx
from sa_core.stego_module.common_funcs import f_get_dif_of_modules, f_get_blocks, f_get_block_coeffs

from .configs.koch_zhao_analysis_config import *
from ._result_structs import KzaRes


# Realize steganalysis of Koch-Zhao method
class KochZhaoAnalysisMethod:
    def __init__(self, path):
        self.__img = ImageHandler()
        self.__img.load(path)
        self.__imar = self.__img.get_array()

        self.__log = ""
        self.__results = None

    # Returns log of last analysis
    def get_log(self):
        return self.__log

    def execute(self, try_extract=False):
        # Clear last analysis data
        self.__results = None
        self.__log = ""

        # Starting log
        path = self.__img.get_path()
        self.__log += "Steganalysis with Koch-Zhao Analysis method for '" + str(path) + "'\n"

        # Analysis operation
        try:
            r = self.__analyze()
            self.__results = r
        except Exception as ex:
            self.__log += "X\tCritical error: {0}\n".format(repr(ex))
            return None

        # Write in log results
        self.__write_results()

        # Trying to extract hidden data
        ex = [] if try_extract else None
        if try_extract and r.threshold > THRESHOLD:
            decryptor = KzEx(threshold=r.threshold, coeffs=DCT_COEFFICIENTS, block_size=BLOCK_SIZE)
            ex = decryptor.extract(self.__img, coords=r.indexes)
        self.__results.data = ex
        self.__write_extracted_data()  # Writing extracted data to log

        # Return all results
        return self.__results

    # Writes results of analysis in log
    def __write_results(self):
        if self.__results is None:
            return

        if self.__results.threshold > THRESHOLD:
            result = "Detected volume of hidden message: {0} bit\n".format(self.__results.volume)
            result += "Detected threshold for bit decoding: {0:.2f}\n".format(self.__results.threshold)
        else:
            result = "Detected threshold is not large enough to decode data\n"

        self.__log += result

    # Writes results of data extracting in log
    def __write_extracted_data(self):
        if self.__results.data is None:
            return

        self.__log += "\tExtracted data:\n\t-----\n"
        self.__log += self.__results.data
        self.__log += "\n\t-----\n"

    # Main operations of analysis
    def __analyze(self):
        img_array = self.__img.get_blue()  # Working with blue channel only

        c_seq = {"C1": [], "C2": [], "C3": []}  # Sequences of coefficients differences
        interval_start_indexes = {"C1": 0, "C2": 0, "C3": 0}  # Indexes of beginning of founded intervals
        d_seq = {}  # Sequences of c_seq values differences

        # Split all pixels in channel into blocks
        blocks = f_get_blocks(img_array, BLOCK_SIZE)

        for block in blocks:
            dct_block = dct(block, DCT_METHOD)  # Calc dct for block: getting frequency representation

            # Calculation of difference between dct coefficients in all possible pairs of indexes
            c_seq["C1"].append(self.__get_module_dif(dct_block, ((2, 3), (3, 2))))
            c_seq["C2"].append(self.__get_module_dif(dct_block, ((2, 4), (4, 2))))
            c_seq["C3"].append(self.__get_module_dif(dct_block, ((3, 4), (4, 3))))

        # Getting suspicious interval (interval of high c_seq values)
        for key in c_seq:
            il, ir = self.__get_interval(c_seq[key])  # Getting interval indexes

            # Expanding borders if it possible
            il = il - 1 if il > 0 else il
            ir = ir + 2 if ir < len(c_seq[key]) - 2 else ir

            # Truncation of c_seq array in accordance with interval
            c_seq[key] = c_seq[key][il:ir]
            interval_start_indexes[key] = il  # Saving start index of interval (in original c_seq)

            # Calculation of d_seq only by interval values
            d_seq[key] = [c_seq[key][0]]
            for i in range(1, len(c_seq[key])):
                d_seq[key].append(fabs(c_seq[key][i] - c_seq[key][i - 1]))
            d_seq[key].append(c_seq[key][len(c_seq[key]) - 1])

        # Calculation of supposed thresholds
        thresholds, indexes = [], []
        for key in c_seq:
            # Truncation of expanded interval to clearly high-values interval
            r = self.__find_two_maxs(d_seq[key])
            r[1] -= 1

            # Getting threshold value and definition of final interval indexes
            if len(r) < 2 or len(c_seq[key][r[0]:r[1] + 1]) < 8:  # There not hidden data
                M0 = 0.0  # Threshold value
                self.__log += "|\t[{0}] {1} doesn't contains needed sequence\n".format(key, key)
                ind = None
            else:  # Can suppose that img contains hidden data
                M0 = min(c_seq[key][r[0]:r[1]])  # Threshold value: minimum of c_seq (difference of coeffs) value
                self.__log += "|\t[{0}] SEQ = {1}\n".format(key, c_seq[key][r[0]:r[1] + 1])
                ind = (interval_start_indexes[key] + r[0], interval_start_indexes[key] + r[1])

            # Saving threshold and indexes by this pair of dct coefficients
            thresholds.append(M0)
            indexes.append(ind)

            # Write to log results if hiding was supposedly detected
            if M0 != 0.0:
                self.__log += ("|\t[{0}] SEQ = {1}, bounds: from {2} to {3}. M0 = {4}\n"
                               .format(key, key, r[0], r[1], M0))

        # Finding maximum of all saved thresholds (that can indicate data hiding)
        max_ind = thresholds.index(max(thresholds))
        threshold, indexes = thresholds[max_ind], indexes[max_ind]
        threshold = threshold - 0.5 if threshold > 0.5 else threshold

        # Calculation of volume of hidden data (in bits)
        volume = indexes[1] - indexes[0] + 1 if threshold > THRESHOLD else 0

        # Return results
        r = KzaRes(threshold=threshold, indexes=indexes, volume=volume, data=None)
        return r

    # Returns abs of difference between coefficients abs
    def __get_module_dif(self, block, indexes):
        bc = f_get_block_coeffs(block, indexes)
        dif = f_get_dif_of_modules(bc[0], bc[1])
        return fabs(dif)

    # Returns the longest interval of high values in sequence
    def __get_interval(self, seq):
        smax = max(seq)
        trsh = smax * CUT_COEFF

        # Truncation of all sequence values
        aseq = seq.copy()
        for i in range(len(aseq)):
            if aseq[i] < trsh:
                aseq[i] = 0.0

        # Getting all intervals
        sq_inds = []
        il, ir = 0, 0
        for i in range(len(aseq)):
            if aseq[i] == 0.0:
                ir = i
                if ir - il > 0:
                    sq_inds.append((il, ir - 1))
                il = i + 1

        # Choosing the longest interval
        if len(sq_inds) > 0:
            sizes = [j - i + 1 for (i, j) in sq_inds]
            max_size = max(sizes)
            il, ir = sq_inds[sizes.index(max_size)]

        # Return coords of the longest interval
        return il, ir

    # Returns two maximum sequence values in order left to right
    def __find_two_maxs(self, d):
        # Get first value
        m = max(d)
        il = d.index(m)

        # Get second value
        # d[il] = -1
        m = max(d[:il] + [-1] + d[il+1:])
        ir = d.index(m)

        if il < ir:
            return [il, ir]
        else:
            return [ir, il]
