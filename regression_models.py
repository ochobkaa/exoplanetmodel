from abc import ABC, abstractmethod
from typing import Iterable
import pandas as pd
import numpy as np
import sklearn.pipeline as pp
import sklearn.linear_model as lin
import sklearn.preprocessing as pre
from sklearn.model_selection import train_test_split

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
    
JUP_MASS_EARTH = 316.8
JUP_RAD_EARTH = 11.2

class MassRadiusLogRegression(Regression):
    def __init__(self) -> None:
        super().__init__()
        self.__reg = pp.make_pipeline(pre.SplineTransformer(n_knots=5, degree=3), lin.Ridge(alpha=0.05))
        self.__R2 = 0.0

    def __mass_log(self, df: pd.DataFrame) -> list[float]:
        return df["mass"].apply(lambda x: np.log10(x * JUP_MASS_EARTH)).to_list()
    
    def __radius_log(self, df: pd.DataFrame) -> list[float]:
        return df["radius"].apply(lambda x: np.log10(x * JUP_RAD_EARTH)).to_list()

    def _learn(self, df: pd.DataFrame) -> None:
        reg = self.__reg

        mass_log = self.__mass_log(df)
        radius_log = self.__radius_log(df)

        mass_logX = list(zip(range(len(mass_log)), mass_log))

        mlogX_train, mass_logX_test, rlog_train, rlog_test = train_test_split(
            mass_logX,
            radius_log,
            train_size=0.6,
            random_state=32
        )

        reg.fit(X=mlogX_train, y=rlog_train)

        self.__R2 = reg.score(X=mass_logX_test, y=rlog_test)
        

    def _calc(self, *args, **kwargs) -> Iterable[float]:
        reg = self.__reg

        mass = kwargs["mass"]
        mass_X = list(zip(range(len(mass)), mass))

        radius = reg.predict(mass_X).tolist()

        return radius

    @property
    def R2(self) -> float:
        return self.__R2