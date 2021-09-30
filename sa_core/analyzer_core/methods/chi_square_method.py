import numpy as np

from sa_core.image_handler import *
from sa_core.sa_math import chi_sqr

from .configs.chi_square_config import *
from ._result_structs import ChiSqrRes


# Realize Chi-Square steganalysis method
class ChiSquareMethod:
    def __init__(self, img_path):
        self.__img = ImageHandler()
        self.__img.load(img_path)
        self.__imar = self.__img.get_array()

        self.__log = ""
        self.__results = None

    # Returns log of last analysis
    def get_log(self):
        return self.__log

    def execute(self, visualize=False):
        # Clear last analysis data
        self.__log = ""
        self.__results = None

        # Starting log
        img_path = self.__img.get_path()
        self.__log += "Steganalysis with Chi-Square method for '" + str(img_path) + "'\n"

        # Analysis operation
        try:
            r = self.__analyze(visualize)
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

        result = "Average image`s fullness: {0:.2%}\n".format(self.__results.fullness)
        self.__log += result

    # Main operations of analysis
    def __analyze(self, visualize):
        blocks_coords = self.__get_blocks_coords()  # Split into blocks and get they coords
        cnum = np.ones(RGB_COLOURS, dtype=np.int32)  # Creation of categories array

        fullness = 0
        vis = np.zeros(shape=self.__imar.shape) if visualize else None

        k = 1
        for coord in blocks_coords:
            # Calculation of frequencies of all colors in block
            block_cnum = self.__calc_colours_by_coord(coord)
            cnum = [x + y for x, y in zip(cnum, block_cnum)]  # Color number array

            # Creating observed and expected arrays
            observed, expected = self.__get_chi_arrays(cnum)
            observed, expected = self.__unify_categories(observed, expected)

            # Calculation of Chi square test values
            chi2, p = chi_sqr(observed, expected)
            fullness += int(p > THRESHOLD)

            # Colorizing blocks with hidden information
            if visualize:
                self.__colorize_block(vis, coord, ImgChannel.RED if p > THRESHOLD else ImgChannel.GREEN)

            self.__log += "|\t[{0}] chi^2 = {1:.5}; p = {2:.5}\n".format(k, chi2, p)
            k += 1

        # Calculation of container fullness (in percents)
        fullness /= len(blocks_coords)

        # Return results
        r = ChiSqrRes(fullness=fullness, visualized=vis)
        return r

    # Creates observed and expected arrays for chi square test
    def __get_chi_arrays(self, cnum):
        observed = []
        expected = []

        ln = len(cnum) // 2
        for i in range(ln):
            new_observed = cnum[2 * i]
            new_expected = (cnum[2 * i] + cnum[2 * i + 1]) / 2

            if new_expected > 0:
                observed.append(new_observed)
                expected.append(new_expected)

        return expected, observed

    # Calculates color number array for one blocks by the block coords
    def __calc_colours_by_coord(self, coord):
        cnum = np.zeros(RGB_COLOURS, dtype=np.int32)
        deep = self.__imar.shape[2]  # Deep - number of image channels

        for i in range(coord[1][0], coord[1][1] + 1):
            for j in range(coord[0][0], coord[0][1] + 1):
                for ch in range(deep):
                    cnum[int(self.__imar[i][j][ch])] += 1

        return cnum

    # Defines block sizes by the image sizes and method settings
    def __get_block_size(self, width, height):
        if USE_ONE_PERCENT_BLOCK_SIZE:  # if block size must be 1% of the image size
            bsize_width = width // 10 + 1
            bsize_height = height // 10 + 1
        else:
            if BLOCK_WIDTH > 0:  # 0 (or less) width means whole image width
                bsize_width = BLOCK_WIDTH
            else:
                bsize_width = width

            if BLOCK_HEIGHT > 0:  # 0 (or less) height means whole image height
                bsize_height = BLOCK_HEIGHT
            else:
                bsize_height = height

        return bsize_width, bsize_height

    # Splits image into blocks and return they coords (as pixel indexes)
    def __get_blocks_coords(self):
        blocks_coords = []
        height, width, deep = self.__imar.shape

        block_width, block_height = self.__get_block_size(width, height)  # Get blocks size
        w_ind = h_ind = 0  # Pointers for X ans Y axes in pixel matrix
        h_last = min(block_height - 1, height - 1)  # First block right down Y axis coord

        # Calculation of blocks coordinates array
        while True:
            w_last = w_ind + block_width - 1
            if w_last >= width:
                w_last = width - 1  # Cutoff last X index by the image width

            # Save current block calculated coords
            blocks_coords.append([(w_ind, w_last), (h_ind, h_last)])

            # Going to next block
            if w_last == width - 1:  # If 'line' is over
                w_ind = 0

                if h_last == height - 1:  # ... And it was last 'line' - we spliited whole image
                    break

                # Going to next 'line' of blocks
                h_ind = h_last + 1
                h_last = h_ind + block_height - 1
                if h_last >= height:
                    h_last = height - 1
            else:
                w_ind = w_last + 1  # Going to next block in 'line'

        return blocks_coords

    # Unifies color categories that contains low-frequency values (unifying low-frequency colors in union category)
    def __unify_categories(self, observed, expected):
        new_observed = []
        new_expected = []
        touni_observed = []
        touni_expected = []

        # Selecting < UNIFY_CONST values in arrays
        for i in range(len(expected)):
            if expected[i] > UNIFY_CONST:  # 'Normal' categories
                new_expected.append(expected[i])
                new_observed.append(observed[i])
            else:  # Categories that needs to be unifying
                touni_expected.append(expected[i])
                touni_observed.append(observed[i])

        # Unifying operation
        stop = False
        while not stop:
            stop = True

            # Unifying adjacent categories
            for i in range(len(touni_expected) // 2):
                touni_expected[2 * i] += touni_expected[2 * i + 1]
                touni_expected[2 * i + 1] = -1
                touni_observed[2 * i] += touni_observed[2 * i + 1]
                touni_observed[2 * i + 1] = -1

            # Moves big enough categories to all categories
            for i in range(len(touni_expected)):
                if touni_expected[i] > UNIFY_CONST:
                    new_expected.append(touni_expected[i])
                    touni_expected[i] = -1
                    new_observed.append(touni_observed[i])
                    touni_observed[i] = -1

            # Cleaning all deleted from unifying operation categories
            for i in range(touni_expected.count(-1)):
                touni_expected.remove(-1)
                touni_observed.remove(-1)

            # Appending last non-pair category to category with minimum value
            if len(touni_expected) == 1:
                if touni_expected[0] > UNIFY_CONST:
                    new_expected.append(touni_expected[0])
                    new_observed.append(touni_observed[0])
                else:
                    ind = new_expected.index(min(new_expected))
                    new_expected[ind] += touni_expected[0]
                    new_observed[ind] += touni_observed[0]

            elif len(touni_expected) > 0:  # Going to next cycle iteration
                stop = False

        return new_observed, new_expected

    # Colorizes block: shifts color component by some offset
    def __colorize_block(self, colorized_array, coord, channel, offset=COLOR_OFFSET):
        for i in range(coord[1][0], coord[1][1] + 1):
            for j in range(coord[0][0], coord[0][1] + 1):
                red, green, blue = self.__imar[i][j]

                if channel == ImgChannel.RED:
                    colorized_array[i][j] = min(red + offset, 255), green, blue
                elif channel == ImgChannel.GREEN:
                    colorized_array[i][j] = red, min(green + offset, 255), blue
                elif channel == ImgChannel.BLUE:
                    colorized_array[i][j] = red, green, min(blue + offset, 255)
