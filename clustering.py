import sklearn.mixture as mx
import sklearn.cluster as clu
import numpy as np
from sklearn.model_selection import train_test_split
import pandas as pd
from abc import ABC, abstractmethod
from typing import Iterable
import consts as c

class MassRadiusClusterer:
    def __init__(self, n_components: int) -> None:
        self.__clstrr = mx.GaussianMixture(n_components=n_components)

    def learn(self, df: pd.DataFrame) -> Iterable[pd.DataFrame]:
        clstrr = self.__clstrr

        mlog = c.mass_log(df)
        rlog = c.radius_log(df)

        mr_stack = np.column_stack((mlog, rlog))
        cllab = clstrr.fit_predict(mr_stack)

        cls = list(set(cllab.tolist()))

        dfs_list = []
        for cl in cls:
            mask = list(map(lambda x: x == cl, cllab))

            cl_df = df[mask]
            dfs_list.append(cl_df)

        return dfs_list