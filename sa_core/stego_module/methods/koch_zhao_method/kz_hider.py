from sa_core.image_handler import *
from sa_core.sa_lib import get_random_start, str_to_bits_array

from .kz_config import *
from .kz_common import *


# Hide data in image by the Koch-Zhao steganography method
class KochZhaoHider:
    __default_threshold = DEFAULT_THRESHOLD
    __default_coeffs = DCT_COEFFICIENTS
    __default_block_size = BLOCK_SIZE
    __default_seed = 0

    def __init__(self, threshold=__default_threshold, coeffs=__default_coeffs,
                 block_size=__default_block_size, seed=__default_seed):
        self.__threshold = threshold
        self.__coeffs = coeffs
        self.__block_size = block_size
        self.__seed = seed

    # Set hider parameters
    def set_params(self, threshold=None, coeffs=None, block_size=None, seed=None):
        if threshold is not None:
            self.__threshold = threshold
        if coeffs is not None:
            self.__coeffs = coeffs
        if block_size is not None:
            self.__block_size = block_size
        if seed is not None:
            self.__seed = seed

    # Reset parameters to default
    def reset_params(self):
        self.__threshold = self.__default_threshold
        self.__coeffs = self.__default_coeffs
        self.__block_size = self.__default_block_size
        self.__seed = self.__default_seed

    def hide(self, img, data: str):
        if isinstance(img, str):
            img = ImageHandler().load(img)
        elif not isinstance(img, ImageHandler):
            raise ValueError("'img' must be ImageHandler instance or string img path")

        # Getting image array
        image_path = img.get_path()
        imar = img.get_array()  # Image (pixels) array
        bimar = img.get_blue()  # Only blue channel of image array

        is_random_hiding = self.__seed is not None and self.__seed > 0  # Define variation of hiding method

        # Loading bits array of secret data
        bits_array = str_to_bits_array(data)

        # Split all pixels into blocks and get frequency representation
        blocks = get_blocks(bimar, self.__block_size)
        dct_blocks = get_dct_blocks(blocks)

        # Compare of image capacity and secret data size (all in bits)
        capacity, sdata_size = len(dct_blocks), len(bits_array)
        start_block = 0
        to_hide_size = self.__define_available_hiding_size(capacity, sdata_size)  # Getting maximum available data size

        # Main hiding operations
        if is_random_hiding:
            # Pseudo-random Koch-Zhao method

            # Getting indexes sequence
            indexes = get_random_indexes(capacity, self.__seed, to_hide_size)

            # Hiding
            for i in range(len(indexes)):
                block_index, bit = indexes[i], bits_array[i]
                dct_blocks[block_index] = self.__block_hider(dct_blocks[block_index], bit, self.__threshold)

        else:
            # Linear Koch-Zhao method

            # Getting random start index for hiding
            if capacity > sdata_size:
                start_block = get_random_start(sdata_size, capacity)

            # Hiding
            block_index = start_block
            for bit in bits_array:
                dct_blocks[block_index] = self.__block_hider(dct_blocks[block_index], bit, self.__threshold)

                block_index += 1
                if block_index >= len(dct_blocks):
                    break

        # Converting DCT blocks to image array
        blocks = get_idct_blocks(dct_blocks)
        blocks = normalize_all_blocks(blocks, self.__block_size)
        imar = blocks_to_imar(imar, blocks, self.__block_size)

        # Definition name of result file (image file with hidden data)
        point_index = image_path.rfind('.')
        file_postfix = FILES_POSTFIX[1] if is_random_hiding else FILES_POSTFIX[0]
        new_path = image_path[:point_index] + file_postfix + image_path[point_index:]

        # Saving new image file
        img.set_array(imar)
        img.save(new_path)

        # Return meta-data of hiding
        return capacity, sdata_size, start_block

    # Hides data in one block
    def __block_hider(self, block, bit, threshold):
        bc = get_block_coeffs(block)  # Get block coefficients
        dif = get_moduluses_difference(bc[0], bc[1])  # Get coefficients difference
        mod = bc[0], bc[1]

        # Getting modified block coefficients: encoding bit into block
        if bit == 0 and dif <= threshold:
            mod = get_modified_coeffs(True, bc, threshold)
        elif bit == 1 and dif >= -threshold:
            mod = get_modified_coeffs(False, bc, -threshold)

        # Changing block coefficients values
        block[self.__coeffs[0][0]][self.__coeffs[0][1]] = mod[0]
        block[self.__coeffs[1][0]][self.__coeffs[1][1]] = mod[1]

        # Return modified block
        return block

    # Returns available data size for hiding (by container capacity and size of data for hiding)
    def __define_available_hiding_size(self, container_size, secret_size):
        if container_size > secret_size:
            return secret_size
        else:
            return container_size
