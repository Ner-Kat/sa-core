from dataclasses import dataclass
from multiprocessing import Process, Queue

from .methods import ChiSquareMethod as ChiSqrMethod, RegularSingularMethod as RsMethod, \
    KochZhaoAnalysisMethod as KzaMethod
from .methods import ChiSqrRes, RsRes, KzaRes
from ._analyzer_params import AnalyzerParams
from sa_core.sa_lib.timer import Timer


# Can contains results of all methods
@dataclass
class MethodsResult:
    ChiSqrResult: ChiSqrRes
    RsResult: RsRes
    KzaResult: KzaRes


# Chi Square method multiprocessing wrapper
def mp_chisqr(q, img, chisqr_visualize):
    chisqr = ChiSqrMethod(img)
    chisqr_res = chisqr.execute(visualize=chisqr_visualize)
    q.put(chisqr_res)
    q.put(chisqr.get_log())


# Regular-Singular method multiprocessing wrapper
def mp_rs(q, img):
    rs = RsMethod(img)
    rs_res = rs.execute()
    q.put(rs_res)
    q.put(rs.get_log())


# Koch-Zhao analysis method multiprocessing wrapper
def mp_kza(q, img, kza_extract):
    kza = KzaMethod(img)
    kza_res = kza.execute(try_extract=kza_extract)
    q.put(kza_res)
    q.put(kza.get_log())


# Steganalysis executor that union all analysis methods
class SaMethodsHandler:
    def __init__(self, img_path=None, do_chisqr=True, do_rs=True, do_kza=True, chisqr_visualize=True, kza_extract=True):
        self.__img_path = self.__do_chisqr = self.__do_rs = self.__do_kza = None
        self.__chisqr_visualize = self.__kza_extract = None
        self.__global_out = False
        self.__chisqr_res = __rs_res = __kza_res = None
        self.set_params(img_path, do_chisqr, do_rs, do_kza, chisqr_visualize, kza_extract)

        self.__log = ""
        self.__all_logs = self.__get_empty_logs()  # Contains this handler log and all methods logs
        self.__duration = 0.0  # Elapsed time for all operations
        self.__chisqr_res = self.__rs_res = self.__kza_res = None

    # Returns log of last analysis
    def get_log(self):
        return self.__log

    # Set all analyzer parameters via AnalyzerParams structure
    def set(self, params: AnalyzerParams):
        self.set_params(params.img, params.do_chisqr, params.do_rs, params.do_kza,
                        params.chisqr_visualize, params.kza_extract)

    # Set any analyzer parameters
    def set_params(self, img_path=None, do_chisqr=None, do_rs=None, do_kza=None, chisqr_visualize=None, kza_extract=None):
        if img_path is not None:
            self.__img_path = img_path
        if do_chisqr is not None:
            self.__do_chisqr = do_chisqr
        if do_rs is not None:
            self.__do_rs = do_rs
        if do_kza is not None:
            self.__do_kza = do_kza
        if chisqr_visualize is not None:
            self.__chisqr_visualize = chisqr_visualize
        if kza_extract is not None:
            self.__kza_extract = kza_extract

    def exec(self):
        if self.__img_path is None:
            raise ValueError("img_path must be correct string path to an image file")

        # Clear last analysis data
        self.__clear_results()
        self.__duration = 0.0
        self.__all_logs = self.__get_empty_logs()

        # Starting log
        self.__log = ("For {0} steganalysis operations was launched\n"
                      .format(self.__img_path))

        # Starting timer
        timer = Timer()
        timer.start()

        # Analysis operations
        try:
            result = self.__analyze()
        except Exception as ex:
            self.__log += "X\tCritical error: {0}\n".format(repr(ex))
            return None

        # Stopping timer and writing logs
        timer.stop()
        self.__duration = timer.get_time_count()

        self.__log += ("For {0} steganalysis operations was done in {1:.3f} s\n"
                       .format(self.__img_path, self.__duration))
        self.__all_logs["handler"] = self.__log

        # Return result
        return result

    # Returns duration of analysis
    def get_duration(self):
        return self.__duration

    # Returns dict with all methods logs
    def get_all_logs(self):
        return self.__all_logs

    # Main operations of analysis
    def __analyze(self):
        if self.__img_path is None:
            return None

        # Creating and launching all steganalysis methods processes
        processes = []
        if self.__do_chisqr:  # Chi Square method analysis
            chisqr_q = Queue()
            chisqr_proc = Process(target=mp_chisqr,
                                  args=(chisqr_q, self.__img_path, self.__chisqr_visualize,))
            processes.append(chisqr_proc)
            chisqr_proc.start()

        if self.__do_rs:  # Regular-Singular method analysis
            rs_q = Queue()
            rs_proc = Process(target=mp_rs, args=(rs_q, self.__img_path,))
            processes.append(rs_proc)
            rs_proc.start()

        if self.__do_kza:  # Koch-Zhao analysis method
            kza_q = Queue()
            kza_proc = Process(target=mp_kza, args=(kza_q, self.__img_path, self.__kza_extract,))
            processes.append(kza_proc)
            kza_proc.start()

        # Getting results of work of all methods
        if self.__do_chisqr:
            self.__chisqr_res = chisqr_q.get()
            self.__all_logs["chi_sqr"] = chisqr_q.get()
        if self.__do_rs:
            self.__rs_res = rs_q.get()
            self.__all_logs["rs"] = rs_q.get()
        if self.__do_kza:
            self.__kza_res = kza_q.get()
            self.__all_logs["kza"] = kza_q.get()

        # Waiting for ending of work of all methods
        for proc in processes:
            proc.join()

        # Return results
        return self.get_results()

    # Returns results of last stanalysis operations
    def get_results(self):
        result = MethodsResult(self.__chisqr_res, self.__rs_res, self.__kza_res)
        return result

    # Cleans up all results
    def __clear_results(self):
        self.__chisqr_res = None
        self.__rs_res = None
        self.__kza_res = None

    # Returns empty logs dict
    def __get_empty_logs(self):
        return {"chi_sqr": None, "rs": None, "kza": None, "handler": None}
