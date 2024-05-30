import sklearn.tree as tree
import sklearn.ensemble as ens
import sklearn.preprocessing as pre
import sklearn.cluster as clu
import numpy as np
import pandas as pd
from typing import Iterable, Callable
import consts as c

class MassRadiusOutlierCleaner:
    def __init__(self, depth: int, min_leaf: int, tree_count=1, seed=None) -> None:
        if tree_count == 1:
            self.__tree = tree.DecisionTreeRegressor(max_depth=depth, min_samples_leaf=min_leaf)

        else:
            self.__tree = ens.RandomForestRegressor(n_estimators=tree_count, max_depth=depth, 
                                                    min_samples_leaf=min_leaf, random_state=seed)

    def __get_xmatr(self, x: Iterable[float]) -> np.ndarray:
        xmatr = np.array(x).reshape(-1, 1)

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
    
    def clean(self, df: pd.DataFrame, est: float) -> pd.DataFrame:
        curve = lambda x: 1 - 1 / (x ** 2 + 1)

        mass = c.mass_log(df)
        radius = c.radius_log(df)

        self.__fit_tree(mass, radius)
        
        dev = self.__deltas(mass, radius)
        cur_dev = self.__deltas_curve(dev, curve)
        mask = self.__get_mask(cur_dev, est)

        cl_df = df[mask]

        return cl_df
    

class SPMassOutlierCleaner:
    def __init__(self) -> None:
        self.__rsclean = pre.StandardScaler()

    def clean(self, df: pd.DataFrame, stddev=3.0) -> pd.DataFrame:
        rsclean = self.__rsclean

        s_mass = df["star_mass"].to_numpy()
        p_mass = c.mass_log(df)

        m_stack = np.column_stack([s_mass, p_mass])
        m_trans = rsclean.fit_transform(m_stack)

        mask = m_trans < stddev
        mask_sum = mask.all(axis=1)
        mask_l = mask_sum.tolist()

        new_df = df[mask_l]

        return new_df
    

class LargePTeffRadiusCleaner:
    def __init__(self) -> None:
        self.__rsclean = clu.DBSCAN(eps=0.066, min_samples=10)

    def __norm(self, ar: np.ndarray) -> np.ndarray:
        amin = ar.min()
        amax = ar.max()
        ar_norm = (ar - amin) / (amax - amin)

        return ar_norm

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        rsclean = self.__rsclean

        rad = np.array(c.radius_log(df))
        teff = df["temp_calculated"].to_numpy()

        rad_norm = self.__norm(rad)
        teff_norm = self.__norm(teff)

        stack = np.column_stack([rad_norm, teff_norm])

        cllab = rsclean.fit_predict(stack)

        mask = list(map(lambda c: c != -1, cllab))

        new_df = df[mask]

        return new_df