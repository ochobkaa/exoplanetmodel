import pandas as pd
import measures as ms
import calculators as calc
import errors as err
from conversion import MeasureConverter
from abc import ABC, abstractmethod
from typing import Iterable, Dict

class DFCalculation(ABC):
    def __init__(self, 
                 conv: MeasureConverter, cal: calc.Calculator,
                 col_calc: str, args: Dict[str, type]
                ) -> None:
        self.__conv = conv
        self.__cal = cal
        self.__col_calc = col_calc
        self.__args = args

    def calc(self, df: pd.DataFrame) -> pd.DataFrame:
        def args_measures(conv: MeasureConverter, 
                          args: Dict[str, type], 
                          df: pd.DataFrame) -> Dict[str, Iterable[ms.Measure]]:
            args_ms = {}
            for arg_col, arg_type in args.items():
                args_ms[arg_col] = conv.read(arg_col, arg_type, df)

            return args_ms
        
        def val_isna(*args):
            isna = not all(map(lambda a: pd.notna(a.val), args))
            return isna
        
        def calc_measures(cal: calc.Calculator, 
                          args_ms: Dict[str, Iterable[ms.Measure]]) -> Iterable[ms.Measure]:
            for cargs in zip(*args_ms.values()):
                if val_isna(cargs):
                    yield None

                kwcargs = dict(zip(args_ms.keys(), cargs))

                calc_ms = cal.calc(**kwcargs)
                yield calc_ms

        def write_measures(conv: MeasureConverter, 
                           col: str, 
                           vals: Iterable[ms.Measure], 
                           df: pd.DataFrame) -> pd.DataFrame:
            new_df = conv.write(col, vals, df)

            return new_df

        conv = self.__conv
        cal = self.__cal
        col_calc = self.__col_calc
        args = self.__args

        args_ms = args_measures(conv, args, df)
        calc_ms = calc_measures(cal, args_ms)
        new_df = write_measures(conv, col_calc, calc_ms, df)

        return new_df


class DFErrorGen:
    def __init__(self,
                 conv: MeasureConverter,  err_gen: err.ErrorGenerator,
                 col_gen: str, col_type: type) -> None:
        self.__conv = conv
        self.__err_gen = err_gen
        self.__col_gen = col_gen
        self.__col_type = col_type

    def gen(self, df: pd.DataFrame) -> pd.DataFrame:
        def col_measures(conv: MeasureConverter,
                         col_gen: str,
                         col_type: type) -> Iterable[ms.Measure]:
            measures = conv.read(col_gen, col_type, df)

            return measures

        def gen_errs(measures: Iterable[ms.Measure], 
                     err_gen: err.ErrorGenerator, 
                     ms_type: type) -> Iterable[ms.Measure]:
            for ms in measures:
                if pd.isna(ms.err_min) and pd.isna(ms.err_max):
                    err_min = err_gen.gen(ms.val)
                    err_max = err_min
                    new_ms = ms_type(ms.val, err_min, err_max)
                    yield new_ms

                elif pd.isna(ms.err_min):
                    err_min = ms.err_max
                    new_ms = ms_type(ms.val, err_min, ms.err_max)
                    yield new_ms

                elif pd.isna(ms.err_max):
                    err_max = ms.err_min
                    new_ms = ms_type(ms.val, ms.err_min, err_max)
                    yield new_ms

                else:
                    yield ms

        def write_measures(conv: MeasureConverter, 
                           col: str, 
                           vals: Iterable[ms.Measure], 
                           df: pd.DataFrame) -> pd.DataFrame:
            new_df = conv.write(col, vals, df)

            return new_df

        conv = self.__conv
        err_gen = self.__err_gen
        col_gen = self.__col_gen
        col_type = self.__col_type

        measures = col_measures(conv, col_gen, col_type)
        new_measures = gen_errs(measures, err_gen, col_type)
        new_df = write_measures(conv, col_gen, new_measures, df)

        return new_df