from enum import Enum


# Steganography methods
class StegoMethod(Enum):
    LSB_LINEAR = 1
    LSB_RANDOM = 2
    KZ_LINEAR = 3
    KZ_RANDOM = 4
