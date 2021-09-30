import numpy as np
from enum import Enum

from PIL import Image


# Color channels for RGB-mode
class ImgChannel(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2


class ImageHandler:
    __errors_prefix = "ImageHandler Error"

    def __init__(self):
        self.__path = None
        self.__image = None
        self.__array = None
        self.__channel_arrays = {0: None, 1: None, 2: None}
        self.__lsb_inverted = None

    def load(self, path):
        self.__path = path
        self.__image = Image.open(path)
        self.__lsb_inverted = None
        self.__channel_arrays = {0: None, 1: None, 2: None}
        self.__array = None

        return self

    def __create_array(self, dtype=np.int32):
        if self.__image is None:
            return None

        try:
            arr = np.asarray(self.__image)
            old_sizes = arr.shape
        except Exception as ex:
            # AppLog().write_with_error(ex, prefix=self.__errors_prefix,
            #                           data="Возникла ошибка при создании массива пикселей для {0}".format(self.__path))
            return None

        new_sizes = (old_sizes[0], old_sizes[1], 3)
        new_arr = np.zeros(shape=new_sizes, dtype=dtype)

        for i in range(len(arr)):
            for j in range(len(arr[i])):
                new_arr[i][j] = arr[i][j][:3]

        self.__array = new_arr

    def get_array(self):
        if self.__array is None:
            self.__create_array()

        return self.__array

    def print_array(self):
        if self.__array is None:
            return

        for row in self.__array:
            for pixel in row:
                print("({0:0>3} {1:0>3} {2:0>3}) "
                      .format(pixel[0], pixel[1], pixel[2]), end='')
            print()

    def __save_to_img(self, array, name):
        try:
            img = Image.fromarray(array.astype(np.uint8))
            img.save(name)
        except Exception as ex:
            # AppLog().write_with_error(ex, prefix=self.__errors_prefix,
            #                           data="Возникла ошибка при сохранении изображения")
            pass

    def save(self, name):
        self.__save_to_img(self.__array, name)

    def get_channel_array(self, channel):
        if self.__channel_arrays[channel.value] is not None:
            return self.__channel_arrays[channel.value]

        if self.__array is None:
            self.__create_array()

        channel_array = np.zeros(shape=(self.__array.shape[0], self.__array.shape[1]))

        for i in range(len(self.__array)):
            for j in range(len(self.__array[i])):
                channel_array[i][j] = self.__array[i][j][channel.value]

        self.__channel_arrays[channel.value] = channel_array
        return channel_array

    def print_channel_array(self, channel):
        if self.__channel_arrays[channel.value] is not None:
            channel_array = self.__channel_arrays[channel.value]
        else:
            channel_array = self.get_channel_array(channel)

        for row in channel_array:
            for pixel in row:
                print("({0:0>3}) "
                      .format(pixel), end='')
            print()

    def get_red(self):
        return self.get_channel_array(ImgChannel.RED)

    def get_green(self):
        return self.get_channel_array(ImgChannel.GREEN)

    def get_blue(self):
        return self.get_channel_array(ImgChannel.BLUE)

    def set_array(self, new_array):
        self.__array = new_array
        self.__image = None
        self.__path = None
        self.__lsb_inverted = None
        self.__channel_arrays = {0: None, 1: None, 2: None}

    def save_channel(self, channel, name=""):
        if self.__channel_arrays[channel.value] is not None:
            channel_array = self.__channel_arrays[channel.value]
        else:
            channel_array = self.get_channel_array(channel)

        height = channel_array.shape[0]
        width = channel_array.shape[1]
        deep = 3

        np_c = np.zeros(shape=(height, width, deep))
        for i in range(height):
            for j in range(width):
                for k in range(deep):
                    if k != channel.value:
                        np_c[i][j][k] = 0
                    else:
                        np_c[i][j][k] = channel_array[i][j]

        name = name + "_" + channel.name + ".png"
        self.__save_to_img(np_c, name)

    def __invert(self, num):
        byte_str = bin(num)

        new_byte_str = byte_str[:-1]
        if byte_str[-1] == '1':
            new_byte_str += str(0)
        else:
            new_byte_str += str(1)

        return int(new_byte_str, 2)

    def invert_lsb(self):
        if self.__lsb_inverted is not None:
            return self.__lsb_inverted

        new_arr = np.zeros(self.__array.shape, dtype=self.__array.dtype)
        for i in range(new_arr.shape[0]):
            for j in range(new_arr.shape[1]):
                for k in range(new_arr.shape[2]):
                    new_arr[i][j][k] = self.__invert(self.__array[i][j][k])

        self.__lsb_inverted = new_arr
        return new_arr

    def get_size(self):
        if self.__image is not None:
            img_size = np.asarray(self.__image).shape
        elif self.__array is not None:
            img_size = self.__array.shape
        else:
            img_size = (0, 0)

        return img_size[1], img_size[0]

    def get_path(self):
        return self.__path
