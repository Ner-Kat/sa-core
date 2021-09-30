from multiprocessing import Process, Queue

from .methods.lsb_method import LsbExtractor as LsbEx
from .methods.koch_zhao_method import KochZhaoExtractor as KzaEx

from ._stego_methods import StegoMethod


# Multiprocessing wrapper for Linear LSB extractor
def mp_ex_lsb(q, img, start_ind, length):
    ex_lsb = LsbEx(start_ind=start_ind, length=length)
    ex_data = ex_lsb.extract(img)
    q.put(ex_data)


# Multiprocessing wrapper for Pseudo-random LSB extractor
def mp_ex_lsbr(q, img, seed, length):
    ex_lsb = LsbEx(seed=seed, length=length)
    ex_data = ex_lsb.extract(img)
    q.put(ex_data)


# Multiprocessing wrapper for Linear Koch-Zhao extractor
def mp_ex_kz(q, img, threshold, coords):
    ex_kz = KzaEx(threshold=threshold)
    ex_data = ex_kz.extract(img, coords)
    q.put(ex_data)


# Multiprocessing wrapper for Pseudo-random Koch-Zhao extractor
def mp_ex_kzr(q, img, threshold, seed):
    ex_kz = KzaEx(threshold=threshold, seed=seed)
    ex_data = ex_kz.extract(img)
    q.put(ex_data)


# Extractor of hidden data
class ExtractorHandler:
    def __init__(self, method, img, params):
        self.__method = None
        self.__img = None
        self.__params = None
        self.set(method, img, params)

        self.__log = ""

    # Set all extractor parameters
    def set(self, method=None, img=None, params=None):
        if method is not None:
            self.__method = method
        if img is not None:
            self.__img = img
        if params is not None:
            self.__params = params

    def exec(self):
        # Clear log of last extraction
        self.__log = ""

        # Setting initial values
        ex = None
        q = Queue()
        extraction_process = None

        # Creating process of needed extraction method
        if self.__method == StegoMethod.LSB_LINEAR:
            extraction_process = Process(target=mp_ex_lsb, args=(q, self.__img, self.__params[1], self.__params[2],))
        elif self.__method == StegoMethod.LSB_RANDOM:
            extraction_process = Process(target=mp_ex_lsbr, args=(q, self.__img, self.__params[0], self.__params[2],))
        elif self.__method == StegoMethod.KZ_LINEAR:
            extraction_process = Process(target=mp_ex_kz, args=(q, self.__img, self.__params[1], self.__params[2],))
        elif self.__method == StegoMethod.KZ_RANDOM:
            extraction_process = Process(target=mp_ex_kzr, args=(q, self.__img, self.__params[1], self.__params[0],))

        if extraction_process is None:
            return None

        # Starting extraction
        try:
            extraction_process.start()
            ex = q.get()  # Getting extraction results
            extraction_process.join()
        except Exception as ex:
            self.__log += "Extraction error: {0}\n".format(repr(ex))
            return None

        # Return extraction result
        return ex
