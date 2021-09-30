from sa_core.sa_math import DctMethod


BLOCK_SIZE = 8
DCT_COEFFICIENTS = ((3, 4), (4, 3))  # Coefficients for hiding and extracting data
DEFAULT_THRESHOLD = 90  # Threshold for hiding
DCT_METHOD = DctMethod.SCIPY  # Realization of DCT

FILES_POSTFIX = "_kz", "_kzr"  # Postfixes for filenames where data will be hidden
