import pandas as pd
import numpy as np

JUP_MASS_EARTH = 316.8
JUP_RAD_EARTH = 11.2

def mass_log(df: pd.DataFrame) -> list[float]:
    return df["mass"].apply(lambda x: np.log10(x * JUP_MASS_EARTH)).to_list()
    
def radius_log(df: pd.DataFrame) -> list[float]:
    return df["radius"].apply(lambda x: np.log10(x * JUP_RAD_EARTH)).to_list()