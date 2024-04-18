import pandas as pd
import measures as ms
from typing import Iterable

class MeasureConverter:
    def __init__(self) -> None:
        pass

    def __err_min_col(self, name: str) -> str:
        err_min_col = "{name}_error_min".format(name=name)
        return err_min_col
    
    def __err_max_col(self, name: str) -> str:
        err_max_col = "{name}_error_max".format(name=name)
        return err_max_col
        
    def read(self, name: str, ms_type: type, df: pd.DataFrame) -> Iterable[ms.Measure]:
        vals = df[name].to_list()

        err_min_col = self.__err_min_col(name)
        err_mins = df[err_min_col].to_list()

        err_max_col = self.__err_max_col(name)
        err_maxs = df[err_max_col].to_list()

        for val, err_min, err_max in zip(vals, err_mins, err_maxs):
            measure = ms_type(val, err_min, err_max)
            yield measure

    def write(self, name: str, ms_vals: Iterable[ms.Measure], df: pd.DataFrame,
              write_val=True, write_err=True) -> pd.DataFrame:
        def get_val(ms: ms.Measure):
            if ms:
                return ms.val
            
        def get_err_min(ms: ms.Measure):
            if ms:
                return ms.err_min
            
        def get_err_max(ms: ms.Measure):
            if ms:
                return ms.err_max

        new_df = df.copy()
        err_min_col = self.__err_min_col(name)
        err_max_col = self.__err_max_col(name)
        
        if write_val:
            col_vals = map(get_val, ms_vals)
            col_vals_s = pd.Series(col_vals, name=name)
            new_df.update(col_vals_s)

        if write_err:
            col_err_min = map(get_err_min, ms_vals)
            col_err_min_s = pd.Series(col_err_min, name=err_min_col)
            new_df.update(col_err_min_s)

            col_err_max = map(get_err_max, ms_vals)
            col_err_max_s = pd.Series(col_err_max, name=err_max_col)
            new_df.update(col_err_max_s)

        return new_df
    