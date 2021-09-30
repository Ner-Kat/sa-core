from sa_core.image_handler import *
from ..configs.regular_singular_config import *
from .rs_group_type import RsGroupType


# RsCalc multiprocessing wrapper
def rs_calc_mp(q, img_array, channel):
    rs_calc = RsCalc(img_array, channel)
    res = rs_calc.exec()
    q.put(res)


# Execute calculation of values counts in RS groups for one pixels array
class RsCalc:
    def __init__(self, img_array, channel):
        self.__img_array = img_array
        self.__channel = channel

    def exec(self):
        return self.__do_one_rs()

    # Main RS groups calculation method
    def __do_one_rs(self):
        img_array = self.__img_array
        channel = self.__channel

        local_img = ImageHandler()
        local_img.set_array(img_array)

        channel_array = local_img.get_channel_array(channel)
        regulars = singulars = inv_regulars = inv_singulars = 0

        groups = self.__get_groups(channel_array)
        mask_funcs = self.__get_mask_funcs(FLIPPING_MASK)
        inv_mask_funcs = self.__get_mask_funcs(self.__invert_mask(FLIPPING_MASK))

        for group in groups:
            v = self.__get_func_values(group, mask_funcs)
            group_type = self.__get_group_type(v[0], v[1])
            if group_type == RsGroupType.REGULAR:
                regulars += 1
            elif group_type == RsGroupType.SINGULAR:
                singulars += 1

            v = self.__get_func_values(group, inv_mask_funcs)
            group_type = self.__get_group_type(v[0], v[1])
            if group_type == RsGroupType.REGULAR:
                inv_regulars += 1
            elif group_type == RsGroupType.SINGULAR:
                inv_singulars += 1

        return regulars, singulars, inv_regulars, inv_singulars

    # Split all pixels into groups
    def __get_groups(self, channel_array):
        groups = []
        excess = []

        ln = channel_array.shape[1]
        for str in channel_array:
            for i in [i * PIXELS_IN_GROUP for i in range(ln // PIXELS_IN_GROUP)]:
                group = []
                for j in range(PIXELS_IN_GROUP):
                    group.append(str[i + j])
                groups.append(group)

            for i in range((ln // PIXELS_IN_GROUP) * PIXELS_IN_GROUP, ln):
                excess.append(str[i])
            if len(excess) >= PIXELS_IN_GROUP:
                groups.append(excess[:PIXELS_IN_GROUP])
                excess = excess[PIXELS_IN_GROUP:]

        return groups

    # Regularity (smooth) function
    def __regularity_func(self, nums):
        sum = 0
        for i in range(len(nums) - 1):
            sum += abs(nums[i + 1] - nums[i])
        return sum

    # Function of direct flipping
    def __flip_direct(self, val):
        val = int(val)
        if val & 1:
            return val - 1
        return val + 1

    # Function of back flipping
    def __flip_back(self, val):
        val = int(val)
        if val & 1:
            return val + 1
        return val - 1

    # Function of null flipping
    def __flip_null(self, val):
        val = int(val)
        return val

    # Composes list of flipping functions by the chosen mask
    def __get_mask_funcs(self, mask=FLIPPING_MASK):
        f_mask = []
        for e in mask:
            if e == 1:
                f_mask.append(self.__flip_direct)
            elif e == 0:
                f_mask.append(self.__flip_null)
            elif e == -1:
                f_mask.append(self.__flip_back)

        return f_mask

    # Applying flipping functions to one group
    def __group_flipping(self, group, mask_funcs):
        flipped = []
        for i in range(PIXELS_IN_GROUP):
            flipped.append(mask_funcs[i](group[i]))

        return flipped

    # Definition of group type
    def __get_group_type(self, func, flipped_func):
        if flipped_func > func:
            return RsGroupType.REGULAR
        if flipped_func < func:
            return RsGroupType.SINGULAR
        if flipped_func == func:
            return RsGroupType.UNUSABLE

    # Inverts mask
    def __invert_mask(self, mask=FLIPPING_MASK):
        return [e * -1 for e in mask]

    # Calc regularity function values for original and flipped groups
    def __get_func_values(self, group, mask_funcs):
        flipped_group = self.__group_flipping(group, mask_funcs)
        group_func = self.__regularity_func(group)
        flipped_group_func = self.__regularity_func(flipped_group)

        return group_func, flipped_group_func
