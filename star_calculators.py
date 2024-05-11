import pandas as pd
import numpy as np
from abc import ABC
from typing import Iterable
import calculators as calc
import measures as ms
import errors as err

class StarCalculator:
    def __init__(self, rou: err.Round, ms_type: type) -> None:
        self.__rou = rou
        self.__ms_type = ms_type

    def calc(self, p_ms: Iterable[ms.Measure]) -> ms.Measure:
        def calc_star_val(p_ms: Iterable[ms.Measure]) -> float:
            val = np.mean(list(map(lambda p: p.val, p_ms)))

            return val
        
        def calc_star_err_min(p_ms: Iterable[ms.Measure]) -> float:
            err_min = np.sqrt(sum(map(lambda p: p.err_min ** 2, p_ms))) / len(p_ms)

            return err_min
        
        def calc_star_err_max(p_ms: Iterable[ms.Measure]) -> float:
            err_max = np.sqrt(sum(map(lambda p: p.err_max ** 2, p_ms))) / len(p_ms)

            return err_max

        rou = self.__rou
        ms_type = self.__ms_type

        val = calc_star_val(p_ms)
        err_min = calc_star_err_min(p_ms)
        err_max = calc_star_err_max(p_ms)

        err_min_r = rou.round_err(err_min)
        err_max_r = rou.round_err(err_max)
        val_r = rou.round_val(val, err_min_r)

        val_ms = ms_type(val_r, err_min_r, err_max_r)
        
        return val_ms