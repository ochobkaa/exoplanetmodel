import pandas as pd
import measures as ms
from typing import Iterable

class MeasureConverter:
    def __init__(self, df: pd.DataFrame) -> None:
        self.__df = df

    def measures(self, name: str, ms_type: type) -> Iterable[ms.Measure]:
        vals = self.__df.loc[name].to_list()

        err_min_col = "{name}_error_min".format(name=name)
        err_mins = self.__df.loc[err_min_col].to_list()

        err_max_col = "{name}_error_max".format(name=name)
        err_maxs = self.__df.loc[err_max_col].to_list()

        for val, err_min, err_max in zip(vals, err_mins, err_maxs):
            measure = ms_type(val, err_min, err_max)
            yield measure