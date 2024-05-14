import sklearn.tree as tree
import numpy as np
import pandas as pd
from typing import Iterable, Callable

class RTreeOutlierCleaner:
    def __init__(self) -> None:
        self.__tree = tree.DecisionTreeRegressor(max_depth=4, min_samples_leaf=10)

    def __get_xmatr(self, x: Iterable[float]) -> np.ndarray:
        xmatr = list(zip(range(len(x)), x))

        return xmatr

    def __fit_tree(self, x: Iterable[float], y: Iterable[float]) -> None:
        xmatr = self.__get_xmatr(x)

        self.__tree.fit(xmatr, y)

    def __stddev(self, y: Iterable[float]) -> float:
        stddev = np.std(y)

        return stddev

    def __deltas(self, x_vals: Iterable[float], y_vals: Iterable[float]) -> Iterable[float]:
        xmatr = self.__get_xmatr(x_vals)

        y_calcs = self.__tree.predict(xmatr)
        for yv, yc in zip(y_vals, y_calcs):
            delta = abs(yv - yc)
            yield delta

    def __deltas_curve(self, deltas: Iterable[float], curv_f: Callable[[float], float]) -> Iterable[float]:
        curved = list(map(curv_f, deltas))

        return curved

    def __get_mask(self, deltas: Iterable[float], est: float) -> Iterable[bool]:
        mask = list(map(lambda s: s < est, deltas))

        return mask
    
    def clean(self, df: pd.DataFrame, x_col: str, y_col: str, est: float, log_data=False) -> pd.DataFrame:
        curve = lambda x: 1 - 1 / (x ** 2 + 1)

        x = df[x_col].to_list()
        y = df[y_col].to_list()

        if log_data:
            x = list(map(np.log10, x))
            y = list(map(np.log10, y))

        self.__fit_tree(x, y)
        
        dev = self.__deltas(x, y)
        cur_dev = self.__deltas_curve(dev, curve)
        mask = self.__get_mask(cur_dev, est)

        cl_df = df[mask]

        return cl_df