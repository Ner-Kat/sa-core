from sa_core.image_handler import *
from sa_core.sa_lib import str_to_bits_array

from .lsb_config import *
from .lsb_common import *


# Hide data in image by the LSB steganography method
class LsbHider:
    __default_seed = 0

    def __init__(self, seed=__default_seed):
        self.__seed = seed

    # Set hider parameters
    def set_params(self, seed=None):
        if seed is not None:
            self.__seed = seed

    # Reset parameters to default
    def reset_params(self):
        self.__seed = self.__default_seed

    def hide(self, img, data: str):
        if isinstance(img, str):
            img = ImageHandler().load(img)
        elif not isinstance(img, ImageHandler):
            raise ValueError("'img' must be ImageHandler instance or string img path")

        image_path = img.get_path()
        is_random_hiding = self.__seed is not None and self.__seed > 0

        # Loading bits array of secret data
        bits_array = str_to_bits_array(data)

        # Compare of image capacity and secret data size (all in bits)
        capacity = self.__calc_capacity(img.get_array())
        sdata_size = len(bits_array)
        to_hide_size, relative_volume = self.__define_available_hiding_size(capacity, sdata_size)

        # Main hiding operations
        if is_random_hiding:
            imar = self.__lsb_random(img, bits_array, to_hide_size)
        else:
            imar = self.__lsb_linear(img, bits_array)

        # Definition name of result file (image file with hidden data)
        point_index = image_path.rfind('.')
        file_postfix = FILES_POSTFIX[1] if is_random_hiding else FILES_POSTFIX[0]
        new_path = image_path[:point_index] + file_postfix + image_path[point_index:]

        # Saving new image file
        img.set_array(imar)
        img.save(new_path)

        # Return meta-data of hiding
        return capacity, sdata_size, relative_volume

    # Hides data into image array linearly
    def __lsb_linear(self, img: ImageHandler, bits_array):
        # Getting array and sizes
        imar = img.get_array()
        height, width, deep = imar.shape

        # Converting image array to linear array
        linear_imar = imar_to_linear(imar)

        # Hiding
        k = 0
        for i in range(len(linear_imar)):
            linear_imar[i] = self.__insert_bit(linear_imar[i], bits_array[k])
            k += 1

            if k >= len(bits_array):
                break

        # Converting linear array to image array
        imar = linear_imar_to_imar(linear_imar, (height, width, deep))

        # Return image array contains hidden data
        return imar

    # Hides data into image array pseudo-randomly
    def __lsb_random(self, img: ImageHandler, bits_array, sdata_size):
        # Getting array and sizes
        imar = img.get_array()
        height, width, deep = imar.shape

        # Converting image array to linear array
        linear_imar = imar_to_linear(imar)

        # Generating pseudo-random indexes for hiding
        inds = generate_indexes_for_linear_array(len(linear_imar), self.__seed, sdata_size)

        # Hiding
        k = 0
        for ind in inds:
            linear_imar[ind] = self.__insert_bit(linear_imar[ind], bits_array[k])
            k += 1

        # Converting linear array to image array
        imar = linear_imar_to_imar(linear_imar, (height, width, deep))

        # Return image array contains hidden data
        return imar

    # Returns available capacity of container (image array) in bits
    def __calc_capacity(self, img_array):
        pixels = img_array.shape[0] * img_array.shape[1]
        bits_num = pixels * 3

        return bits_num

    # Returns available data size for hiding (by container capacity and size of data for hiding)
    # and relative volume of secret data
    def __define_available_hiding_size(self, container_size, secret_size):
        if container_size > secret_size:
            available_size = secret_size
            relative_sdata_volume = secret_size / container_size
        else:
            available_size = container_size
            relative_sdata_volume = 1

        return available_size, relative_sdata_volume

    # Change least significant bit in byte
    def __insert_bit(self, byte, bit_to_hide):
        img_byte_str = bin(byte)[2:]
        img_byte_str = img_byte_str.zfill(8)

        new_img_byte_str = img_byte_str[:-1]
        new_img_byte_str += str(bit_to_hide)

        new_img_byte = int("0b" + new_img_byte_str, 2)
        return new_img_byte
