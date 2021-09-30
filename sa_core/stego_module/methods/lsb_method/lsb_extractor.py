from sa_core.image_handler import *
from sa_core.sa_lib import bits_array_to_str

from .lsb_config import *
from .lsb_common import *


# Extract data that was hidden by LSB steganography method
class LsbExtractor:
    __default_seed = 0
    __default_start_index = 0
    __default_length = 0

    def __init__(self, seed=__default_seed, start_ind=__default_start_index, length=__default_length):
        self.__seed = self.__default_seed if seed is None else seed
        self.__start_ind = self.__default_start_index if start_ind is None else start_ind
        self.__length = self.__default_length if length is None else length

        self.__log = ""

    # Set extractor parameters
    def set_params(self, seed=None, start_ind=None, length=None):
        if seed is not None:
            self.__seed = seed
        if start_ind is not None:
            self.__start_ind = start_ind
        if length is not None:
            self.__length = length

    # Reset extractor parameters to default
    def reset_params(self):
        self.__seed = self.__default_seed
        self.__start_ind = self.__default_start_index
        self.__length = self.__default_length

    # Returns log of last extraction
    def get_log(self):
        return self.__log

    def extract(self, img):
        if isinstance(img, str):
            img = ImageHandler().load(img)
        elif not isinstance(img, ImageHandler):
            raise ValueError("'img' must be ImageHandler instance or string img path")

        # Clear last extraction log
        self.__log = ""

        # Getting image array and sizes
        imar = img.get_array()
        height, width, deep = imar.shape

        is_random_hiding = self.__seed is not None and self.__seed > 0

        # Definition length of data needed to extract
        if self.__length is not None and self.__length > 0:  # If length is known
            length = self.__length * 8
        else:  # If length is not known
            length = (height * width - self.__start_ind) * deep

        # Main extraction operations
        if is_random_hiding:
            # Extract data hidden by Pseudo-random LSB method
            try:
                result = self.__extract_lsb_random(img, length)
            except Exception as ex:
                self.__log += "Extraction error: {0}\n".format(repr(ex))
                return None

        else:
            # Extract data hidden by Linear LSB method
            try:
                result = self.__extract_lsb_linear(img, length)
            except Exception as ex:
                self.__log += "Extraction error: {0}\n".format(repr(ex))
                return None

        # Return extracted data
        return result

    # Extracting linear LSB hidden data
    def __extract_lsb_linear(self, img: ImageHandler, length):
        # Getting image array and sizes
        imar = img.get_array()
        height, width, deep = imar.shape

        bits_array = []  # List for extracted data
        linear_imar = imar_to_linear(imar)  # Converts image array to linear array

        # Calc offset for linear array pointer based on known start pixel index
        offset = deep * self.__start_ind

        # Extraction
        for i in range(offset, length + offset):
            img_byte = linear_imar[i]
            img_byte_str = bin(img_byte)

            bit = int(img_byte_str[-1])
            bits_array.append(bit)

            if len(bits_array) >= length:
                break

        # Converting bits array to string
        res = bits_array_to_str(bits_array)
        return res

    # Extracting pseudo-random LSB hidden data
    def __extract_lsb_random(self, img: ImageHandler, length):
        imar = img.get_array()
        height, width, deep = imar.shape

        bits_array = []  # List for extracted data
        linear_imar = imar_to_linear(imar)  # Converts image array to linear array

        # Calc pseudo-random indexes based on known seed
        indexes = generate_indexes_for_linear_array(len(linear_imar), self.__seed, length)

        # Extraction
        for ind in indexes:
            img_byte = linear_imar[ind]
            img_byte_str = bin(img_byte)

            bit = int(img_byte_str[-1])
            bits_array.append(bit)

        # Converting bits array to string
        res = bits_array_to_str(bits_array)
        return res
