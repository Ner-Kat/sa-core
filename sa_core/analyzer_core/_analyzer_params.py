from dataclasses import dataclass


# Struct for storage parameters for SaMethodsHandler
@dataclass
class AnalyzerParams:
    img: str
    do_chisqr: bool
    do_rs: bool
    do_kza: bool
    chisqr_visualize: bool
    kza_extract: bool
