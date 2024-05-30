from abc import ABC, abstractmethod
from typing import Iterable
import pandas as pd
import numpy as np
import sklearn.pipeline as pp
import sklearn.linear_model as lin
import sklearn.preprocessing as pre
import sklearn.ensemble as ens
from sklearn.model_selection import cross_validate, train_test_split, RepeatedKFold
import consts as c
from itertools import product

class NotLearnedError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Regression(ABC):
    def __init__(self) -> None:
        self.__learned = False

    @abstractmethod
    def _learn(self, df: pd.DataFrame) -> None:
        pass

    @abstractmethod
    def _calc(self, *args, **kwargs) -> float:
        return 0.0

    def learn(self, df: pd.DataFrame) -> None:
        self._learn(df)

        self.__learned = True

    def calc(self, *args, **kwargs) -> Iterable[float]:
        learned = self.__learned

        if not learned:
            cl_name = __class__.__name__()
            raise NotLearnedError("{0} is not learned".format(cl_name))

        val = self._calc(*args, **kwargs)
    
        return val
    
    @property
    def R2(self) -> float:
        return 0.0


class MassRadiusLogRegression(Regression):
    def __init__(self, it=10) -> None:
        super().__init__()
        self.__reg = None
        self.__R2 = 0.0
        self.__iter = it

    def _learn(self, df: pd.DataFrame) -> None:
        def cv_reg(
                x: Iterable[float], 
                y: Iterable[float], 
                knots: int,
                degree: int,
                alpha: float,
                it: int) -> tuple[lin.Ridge, float]:
            reg = pp.make_pipeline(pre.SplineTransformer(n_knots=knots, degree=degree), lin.Ridge(alpha=alpha))
            cv = RepeatedKFold(n_splits=10, n_repeats=it)
            
            valid = cross_validate(reg, x, y, cv=cv, n_jobs=4)

            r2 = np.mean(valid["test_score"])
            
            return reg, r2
        
        it = self.__iter

        mass_log = c.mass_log(df)
        radius_log = c.radius_log(df)

        mass_logX = np.array(mass_log).reshape(-1, 1)

        knots_vals = [3, 4, 5]
        degree_vals = [1, 2, 3, 4]
        alpha_vals = [0.05, 0.5, 1, 2, 10, 100]

        param_combs = product(knots_vals, degree_vals, alpha_vals)

        reg_ts = []
        for knots, degree, alpha in param_combs:
            reg_t = cv_reg(mass_logX, radius_log, knots, degree, alpha, it)

            reg_ts.append(reg_t)

        reg_t_best = max(reg_ts, key=lambda t: t[1])
        self.__reg = reg_t_best[0]
        self.__R2 = reg_t_best[1]

        self.__reg.fit(mass_logX, radius_log)
        

    def _calc(self, *args, **kwargs) -> Iterable[float]:
        reg = self.__reg

        mass = kwargs["mass"]
        mass_X = np.array(mass).reshape(-1, 1)

        radius = reg.predict(mass_X).tolist()

        return radius

    @property
    def R2(self) -> float:
        return self.__R2


class RadiusLogTeffRegression(Regression):
    def __init__(self, it=10, alpha_int=(0.0, 1.0), eps=0.01) -> None:
        super().__init__()
        self.__reg = None
        self.__R2 = 0.0
        self.__iter = it
        self.__alphint = alpha_int
        self.__eps = eps

    def _learn(self, df: pd.DataFrame) -> None:
        def int_len(inter: tuple[float, float]) -> float:
            return inter[1] - inter[0]
        
        def val_from_int(inter: tuple[float, float]) -> float:
            return inter[0] + int_len(inter) / 2
        
        def cv_reg(
                x: Iterable[float], 
                y: Iterable[float], 
                alpha: float,
                it: int) -> tuple[lin.Ridge, float]:
            reg = lin.Ridge(alpha=alpha)
            cv = RepeatedKFold(n_splits=10, n_repeats=it)
            
            valid = cross_validate(reg, x, y, cv=cv, n_jobs=4)

            r2 = np.mean(valid["test_score"])
            
            return reg, r2
            
        alpha_int = self.__alphint
        eps = self.__eps
        it = self.__iter

        radius_log = c.radius_log(df)
        teff = df["temp_calculated"].to_list()

        radius_log_X = np.reshape(radius_log, (-1, 1))

        aint_cur = alpha_int
        while int_len(aint_cur) > eps:
            part = val_from_int(aint_cur)
            
            aint_l = (aint_cur[0], part)
            aint_r = (part, aint_cur[1])

            val_l = val_from_int(aint_l)
            val_r = val_from_int(aint_r)

            comp_regs_l, comp_r2_l = cv_reg(radius_log_X, teff, val_l, it)
            comp_regs_r, comp_r2_r = cv_reg(radius_log_X, teff, val_r, it)

            if (comp_r2_l > comp_r2_r):
                aint_cur = aint_l
 
                self.__reg = comp_regs_l
                self.__R2 = comp_r2_l

            else:
                aint_cur = aint_r

                self.__reg = comp_regs_r
                self.__R2 = comp_r2_r

        self.__reg.fit(radius_log_X, teff)
        

    def _calc(self, *args, **kwargs) -> Iterable[float]:
        reg = self.__reg

        radius = kwargs["radius"]
        radius_X = np.reshape(radius, (-1, 1))

        teff = reg.predict(radius_X).tolist()

        return teff
    
    @property
    def R2(self) -> float:
        return self.__R2