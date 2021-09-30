from sa_core.image_handler import *
from sa_core.sa_lib import bits_array_to_str

from .kz_config import *
from .kz_common import *


# Extract data that was hidden by Koch-Zhao steganography method
class KochZhaoExtractor:
    __default_threshold = 0
    __default_coeffs = DCT_COEFFICIENTS
    __default_block_size = BLOCK_SIZE
    __default_seed = 0

    def __init__(self, threshold=__default_threshold, coeffs=__default_coeffs,
                 block_size=__default_block_size, seed=__default_seed):
        self.__threshold = self.__default_threshold if threshold is None else threshold
        self.__coeffs = self.__default_coeffs if coeffs is None else coeffs
        self.__block_size = self.__default_block_size if block_size is None else block_size
        self.__seed = self.__default_seed if seed is None else seed

        self.__log = ""

    # Set extractor parameters
    def set_params(self, threshold=None, coeffs=None, block_size=None, seed=None):
        if threshold is not None:
            self.__threshold = threshold
        if coeffs is not None:
            self.__coeffs = coeffs
        if block_size is not None:
            self.__block_size = block_size
        if seed is not None:
            self.__seed = seed

    # Reset extractor parameters to default
    def reset_params(self):
        self.__threshold = self.__default_threshold
        self.__coeffs = self.__default_coeffs
        self.__block_size = self.__default_block_size
        self.__seed = self.__default_seed

    # Returns log of last extraction
    def get_log(self):
        return self.__log

    def extract(self, img, coords=None):
        if isinstance(img, str):
            img = ImageHandler().load(img)
        elif not isinstance(img, ImageHandler):
            raise ValueError("'img' must be ImageHandler instance or string img path")

        # Clear last extraction log
        self.__log = ""

        # Getting image array
        bimar = img.get_blue()  # Only blue channel of image array

        is_random_hiding = self.__seed is not None and self.__seed > 0
        bits_array = []  # List for extracted data

        # Split all pixels into blocks and get frequency representation
        blocks = get_blocks(bimar)
        dct_blocks = get_dct_blocks(blocks)

        # Main extraction operations
        if is_random_hiding:
            # Extract data hidden by Pseudo-random Koch-Zhao method
            try:
                blocks_count = len(dct_blocks)
                indexes = get_random_indexes(blocks_count, self.__seed, blocks_count)

                # Extraction
                for ind in indexes:
                    bit = self.__decode_block(dct_blocks[ind], self.__threshold)
                    if bit is not None:
                        bits_array.append(bit)
            except Exception as ex:
                self.__log += "Extraction error: {0}\n".format(repr(ex))
                return None

        else:
            # Extract data hidden by Linear Koch-Zhao method
            try:
                # Choosing hidden data bounds
                begin, end = 0, len(dct_blocks) - 1
                if coords is not None:
                    if len(coords) == 1:
                        begin = coords[0]
                    elif len(coords) == 2:
                        begin, end = coords

                # Extraction
                for i in range(begin, end + 1):
                    bit = self.__decode_block(dct_blocks[i], self.__threshold)
                    if bit is not None:
                        bits_array.append(bit)
            except Exception as ex:
                self.__log += "Extraction error: {0}\n".format(repr(ex))
                return None

        # Converting bits array to string
        r = bits_array_to_str(bits_array)
        return r

    # Decodes hidden bit from dct block
    def __decode_block(self, block, threshold):
        bc = get_block_coeffs(block)
        dif = get_moduluses_difference(bc[0], bc[1])
        bit = None

        tp, tm = threshold, -threshold  # Definition thresholds

        # Decoding
        if dif > tp:
            bit = 0
        elif dif < tm:
            bit = 1

        return bit
