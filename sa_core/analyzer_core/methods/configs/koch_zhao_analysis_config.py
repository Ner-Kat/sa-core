from sa_core.sa_math import DctMethod

# Koch-Zhao settings
THRESHOLD = 20  # Crossing this threshold is signaling about detecting of hidden information
CUT_COEFF = 0.2  # Cutoff threshold for difference-between-dct-coeefs values array

# Frequency representation settings
DCT_METHOD = DctMethod.SCIPY  # Method of dct and idct calculation
BLOCK_SIZE = 8

DCT_COEFFICIENTS = ((3, 4), (4, 3))  # Coefficients for extracting

# Log settings
LOGFILE_NAME = "log_KzaMethod.txt"
