import pandas as pd
import measures as ms
from typing import Iterable

class MeasureConverter:
    def __init__(self) -> None:
        pass

    def __err_min_col(name: str) -> str:
        err_min_col = "{name}_error_min".format(name=name)
        return err_min_col
    
    def __err_max_col(name: str) -> str:
        err_max_col = "{name}_error_max".format(name=name)
        return err_max_col
        
    def read(self, name: str, ms_type: type, df: pd.DataFrame) -> Iterable[ms.Measure]:
        vals = df.loc[name].to_list()

        err_min_col = self.__err_min_col(name)
        err_mins = df.loc[err_min_col].to_list()

        err_max_col = self.__err_max_col(name)
        err_maxs = df.loc[err_max_col].to_list()

        for val, err_min, err_max in zip(vals, err_mins, err_maxs):
            measure = ms_type(val, err_min, err_max)
            yield measure

    def write(self, name: str, ms_vals: Iterable[ms.Measure], df: pd.DataFrame) -> pd.DataFrame:
        new_df = df
        err_min_col = self.__err_min_col(name)
        err_max_col = self.__err_max_col(name)
        
        new_df[name] = df[name].apply(
            lambda r: next(map(lambda m: m.val, ms_vals)),
        )

        new_df[err_min_col] = df[err_min_col].apply(
            lambda r: next(map(lambda m: m.err_min, ms_vals)),
        )

        new_df[err_max_col] = df[err_max_col].apply(
            lambda r: next(map(lambda m: m.err_max, ms_vals)),
        )

        return new_df
    