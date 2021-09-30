# For creating Pair-of-Values arrays
RGB_COLOURS = 256
COLOURS_THRESHOLD = 256

# Block settings
USE_ONE_PERCENT_BLOCK_SIZE = False  # Enforce to use auto-calculated 1% (of image size) blocks
BLOCK_WIDTH = 0  # 0 means maximum width (whole line)
BLOCK_HEIGHT = 1

# Chi-Square configs
THRESHOLD = 0.95  # P-value threshold
UNIFY_CONST = 4  # Max count of colors in one category at which the category will be unite
COLOR_OFFSET = 100  # Chi-Square fullness visualization color offset

# Log settings
LOGFILE_NAME = "log_ChiSqrMethod.txt"
