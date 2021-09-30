import datetime as _datetime
import os.path as _ospath
import os as _os


# Decode bits array (represented as list of integers) into string
def bits_array_to_str(bits_array):
    bytes_data = []

    for i in range(len(bits_array) // 8):
        byte = "0b"
        for j in range(8):
            byte += str(bits_array[i * 8 + j])

        byte = bytes([int(byte, 2)])
        bytes_data.append(byte)

    bytes_data = b''.join(bytes_data)
    res = bytes_data.decode("utf-8", errors='ignore').replace("\r\n", "\n").replace("\r", "")

    return res


# Write bits array (represented as list of integers) into file
def write_bits_array(bits_array, path):
    with open(path, 'wb') as secret_file:
        for i in range(len(bits_array) // 8):
            byte = "0b"
            for j in range(8):
                byte += str(bits_array[i * 8 + j])
            byte = bytes([int(byte, 2)])
            secret_file.write(byte)


# Convert string into bits array (into list of bit values)
def str_to_bits_array(s):
    s_bytes = bytearray(s, "utf-8")
    bits_array = []

    for byte in s_bytes:
        byte_str = bin(byte)[2:]
        byte_str = byte_str.zfill(8)
        for bit in byte_str:
            bits_array.append(int(bit))

    return bits_array


# Load data from file into bits array (represented as list of integers)
def read_bits_array(path):
    bits_array = []
    with open(path, 'rb') as secret_file:
        secret = secret_file.read()
        for byte in secret:
            byte_str = bin(byte)[2:]
            byte_str = byte_str.zfill(8)
            for bit in byte_str:
                bits_array.append(int(bit))

    return bits_array


# Specific function for saving string data into file with data marker
def write_extracted_data(ex_data, filename, ex_path="", write_time=True):
    datetime_mark = ""
    if write_time:
        now = _datetime.datetime.now()
        datetime_mark = "-{0}{1}{2}{3}{4}{5}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)

    if ex_data is None or ex_data == "":
        return

    filename = filename.split(".")[-2]
    if not _ospath.isdir(ex_path):
        _os.mkdir(ex_path)
    with open(ex_path + "\\" + filename + datetime_mark + ".txt", 'w', encoding="utf-8") as file:
        file.write(ex_data)
