import sklearn.tree as tree
import numpy as np
import pandas as pd
from typing import Iterable

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
            delta = (yv - yc) ** 2
            yield delta

    def __get_mask(self, deltas: Iterable[float], est: float) -> Iterable[bool]:
        mask = list(map(lambda s: s < est, deltas))

        return mask
    
    def clean(self, df: pd.DataFrame, x_col: str, y_col: str, stdmul: float) -> pd.DataFrame:
        x = df[x_col].to_list()
        y = df[y_col].to_list()
        self.__fit_tree(x, y)
        
        dev = self.__deltas(x, y)
        std = self.__stddev(y)
        mask = self.__get_mask(dev, std * stdmul)

        cl_df = df[mask]

        return cl_df