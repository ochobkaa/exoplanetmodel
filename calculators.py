from numpy import power, sqrt, pi
from abc import ABC, abstractmethod
import measures as ms

G = 6.6743e-11
G_RERR = 5e-5

class Calculator(ABC):
    def __init__(self, ms_type: type) -> None:
        self.__ms_type = ms_type

    @abstractmethod
    def fval(self, *args, **kwargs) -> float:
        return 0.0

    @abstractmethod
    def ferr_min(self, val: float, *args, **kwargs) -> float:
        return 0.0
    
    @abstractmethod
    def ferr_max(self, val: float, *args, **kwargs) -> float:
        return 0.0

    def calc(self, *args, **kwargs):
        val = self.fval(*args, **kwargs)
        err_min = self.ferr_min(val, *args, **kwargs)
        err_max = self.ferr_max(val, *args, **kwargs)

        ms = self.__ms_type(val, err_min, err_max)
        return ms
    

class SemiMajorAxisCalc(Calculator):
    def __init__(self) -> None:
        super().__init__(ms.SemiMajorAxis)

    def fval(self, *args, **kwargs) -> float:
        star_m = kwargs["star_mass"].val_kg
        period = kwargs["orbital_period"].val_s

        sm_axis_m = power((G * star_m * period ** 2) / (4 * pi ** 2), 1 / 3)
        sm_axis = sm_axis_m / ms.AU_M

        return sm_axis

    def __ferr(self, val: float, star_m_rerr: float, period_rerr: float) -> float:
        rerr = (G_RERR + star_m_rerr + 2 * period_rerr) / 3
        err = rerr * val

        return err
    
    def ferr_min(self, val: float, *args, **kwargs):
        star_m_rerr_min = kwargs["star_mass"].rerr_min
        period_rerr_min = kwargs["orbital_period"].rerr_min

        err_min = self.__ferr(val, star_m_rerr_min, period_rerr_min)

        return err_min
    
    def ferr_max(self, val: float, *args, **kwargs):
        star_m_rerr_max = kwargs["star_mass"].rerr_max
        period_rerr_max = kwargs["orbital_period"].rerr_max

        err_max = self.__ferr(val, star_m_rerr_max, period_rerr_max)

        return err_max
    

class PlanetTeffCalc(Calculator):
    def __init__(self) -> None:
        super().__init__(ms.TempCalculated)

    def fval(self, *args, **kwargs) -> float:
        star_t = kwargs["star_teff"].val
        star_r = kwargs["star_radius"].val_m
        sm_axis = kwargs["semi_major_axis"].val_m

        alb = kwargs.get("alb").val if kwargs.get("alb") is not None else 0
        ecc = kwargs.get("eccentricity").val if kwargs.get("eccentricity") is not None else 0

        ttype = kwargs.get("ttype", "mean")

        if ttype == "mean":
            dist = sm_axis

        elif ttype == "min":
            dist = sm_axis * (1 - ecc)

        elif ttype == "max":
            dist = sm_axis * (1 + ecc)

        else:
            raise ValueError("ttype argument can only has either \"min\", \"mean\", \"max\" values, not \"{ttype}\"".format(ttype=ttype))

        teff = star_t * sqrt(star_r / (2 * dist)) * power(1 - alb, 1 / 4)

        return teff
    
    def __ferr(self, val: float, star_t_rerr: float, star_r_rerr: float, sm_axis_rerr: float, 
               alb_rerr: float, ecc: float, ecc_err: float, ttype: str):
        if ttype == "mean":
            dist_err = sm_axis_rerr

        elif ttype == "min":
            dist_err = sm_axis_rerr + ecc_err / (1 - ecc)

        elif ttype == "max":
            dist_err = sm_axis_rerr + ecc_err / (1 + ecc)

        else:
            raise ValueError("ttype argument can only has either \"min\", \"mean\", \"max\" values, not \"{ttype}\"".format(ttype=ttype))

        teff_rerr = star_t_rerr + (star_r_rerr + dist_err) / 2 + alb_rerr / 4
        teff_err = val * teff_rerr

        return teff_err
    
    def ferr_min(self, val: float, *args, **kwargs):
        star_t_rerr_min = kwargs["star_teff"].rerr_min
        star_r_rerr_min = kwargs["star_radius"].rerr_min
        sm_axis_rerr_min = kwargs["semi_major_axis"].rerr_min

        alb_rerr_min = kwargs.get("alb", 0).rerr_min if kwargs.get("alb") is not None else 0
        ecc = kwargs.get("eccentricity", 0).val if kwargs.get("eccentricity") is not None else 0
        ecc_err_min = kwargs.get("eccentricity", 0).err_min if kwargs.get("eccentricity") is not None else 0

        ttype = kwargs.get("ttype", "mean")

        teff_err_min = self.__ferr(val, star_t_rerr_min, star_r_rerr_min, sm_axis_rerr_min,
                                   alb_rerr_min, ecc, ecc_err_min, ttype)
        
        return teff_err_min
    
    def ferr_max(self, val: float, *args, **kwargs):
        star_t_rerr_max = kwargs["star_teff"].rerr_max
        star_r_rerr_max = kwargs["star_radius"].rerr_max
        sm_axis_rerr_max = kwargs["semi_major_axis"].rerr_max

        alb_rerr_max = kwargs.get("alb", 0).rerr_max if kwargs.get("alb") is not None else 0
        ecc = kwargs.get("eccentricity", 0).val if kwargs.get("eccentricity") is not None else 0
        ecc_err_max = kwargs.get("eccentricity", 0).err_max if kwargs.get("eccentricity") is not None else 0

        ttype = kwargs.get("ttype", "mean")

        teff_err_max = self.__ferr(val, star_t_rerr_max, star_r_rerr_max, sm_axis_rerr_max,
                                   alb_rerr_max, ecc, ecc_err_max, ttype)
        
        return teff_err_max
