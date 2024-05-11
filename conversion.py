import pandas as pd
import measures as ms
from typing import Iterable, Callable

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
            col_vals = list(map(get_val, ms_vals))
            col_vals_df = pd.DataFrame({name: col_vals}, index=new_df.index)
            new_df.update(col_vals_df)

        if write_err:
            col_err_min = list(map(get_err_min, ms_vals))
            col_err_min_df = pd.DataFrame({err_min_col: col_err_min}, index=new_df.index)
            new_df.update(col_err_min_df)

            col_err_max = list(map(get_err_max, ms_vals))
            col_err_max_df = pd.DataFrame({err_max_col: col_err_max}, index=new_df.index)
            new_df.update(col_err_max_df)

        return new_df
    
    def write_if(self, name: str, ms_vals: list[ms.Measure], df: pd.DataFrame, cond: str,
              write_val=True, write_err=True) -> pd.DataFrame:
        new_df = df.copy()

        ms_vals_w = ms_vals
        slice_df = df.query(cond)
        
        slice_df_s =  len(slice_df)
        ms_vals_s = len(ms_vals_w)
        if slice_df_s > ms_vals_s:
            slice_df = slice_df.head(ms_vals_s)

        elif ms_vals_s > slice_df_s:
            ms_vals_w = ms_vals_w[:slice_df_s]

        new_slice_df = self.write(name, ms_vals, slice_df, write_val=write_val, write_err=write_err)
        new_df.update(new_slice_df)

        return new_df
    
    def write_val_if(self, name: str, ms_val: ms.Measure, df: pd.DataFrame, cond: str,
              write_val=True, write_err=True) -> pd.DataFrame:
        new_df = df.copy()

        slice_df = df.query(cond)
        slice_df_s = len(slice_df)

        ms_val_d = [ms_val for _ in range(slice_df_s)]

        new_slice_df = self.write(name, ms_val_d, slice_df, write_val=write_val, write_err=write_err)
        new_df.update(new_slice_df)

        return new_df
