from abc import ABC

class Measure(ABC):
    def __init__(self, val: float, err_min: float, err_max: float) -> None:
        self.__val = val
        self.__err_min = err_min
        self.__err_max = err_max

    @property
    def val(self)  -> float:
        return self.__val
    
    @property
    def err_min(self) -> float:
        return self.__err_min
    
    @property
    def err_max(self) -> float:
        return self.__err_max
    
    @property
    def err(self) -> float:
        err = (self.err_min + self.err_max) / 2

        return err
    
    @property
    def rerr_min(self) -> float:
        rerr = self.err_min / self.val

        return rerr
    
    @property
    def rerr_max(self) -> float:
        rerr_max = self.err_max / self.val

        return rerr_max
    
    @property
    def rerr(self) -> float:
        rerr = self.err / self.val

        return rerr
    
    def __str__(self) -> str:
        s = "{val} +/- {err}".format(val=self.val, err=self.err)

        return s
    

SOL_MASS_KG = 1.989e+30

class StarMass(Measure):
    def __init__(self, val: float, err_min: float, err_max: float) -> None:
        super().__init__(val, err_min, err_max)

    @staticmethod
    def __to_kg(x: float) -> float:
        x_kg = x * SOL_MASS_KG

        return x_kg

    @property
    def val_kg(self) -> float:
        return __class__.__to_kg(self.val)

    @property
    def err_min_kg(self) -> float:
        return __class__.__to_kg(self.err_min)

    @property
    def err_max_kg(self) -> float:
        return __class__.__to_kg(self.err_max)
    
    @property
    def err_kg(self) -> float:
        return __class__.__to_kg(self.err)


SOL_RAD_M =  6.957e+8

class StarRadius(Measure):
    def __init__(self, val: float, err_min: float, err_max: float) -> None:
        super().__init__(val, err_min, err_max)

    @staticmethod
    def __to_m(x: float) -> float:
        x_kg = x * SOL_RAD_M

        return x_kg

    @property
    def val_m(self) -> float:
        return __class__.__to_m(self.val)

    @property
    def err_min_m(self) -> float:
        return __class__.__to_m(self.err_min)

    @property
    def err_max_m(self) -> float:
        return __class__.__to_m(self.err_max)
    
    @property
    def err_m(self) -> float:
        return __class__.__to_m(self.err)
    

AU_M = 1.496e+11

class SemiMajorAxis(Measure):
    def __init__(self, val: float, err_min: float, err_max: float) -> None:
        super().__init__(val, err_min, err_max)

    @staticmethod
    def __to_m(x: float) -> float:
        x_kg = x * AU_M

        return x_kg

    @property
    def val_m(self) -> float:
        return __class__.__to_m(self.val)

    @property
    def err_min_m(self) -> float:
        return __class__.__to_m(self.err_min)

    @property
    def err_max_m(self) -> float:
        return __class__.__to_m(self.err_max)
    
    @property
    def err_m(self) -> float:
        return __class__.__to_m(self.err)


class Eccentricity(Measure):
    def __init__(self, val: float, err_min: float, err_max: float) -> None:
        super().__init__(val, err_min, err_max)


JUP_MASS_KG = 1.898e+27

class Mass(Measure):
    def __init__(self, val: float, err_min: float, err_max: float) -> None:
        super().__init__(val, err_min, err_max)

    @staticmethod
    def __to_kg(x: float) -> float:
        x_kg = x * JUP_MASS_KG

        return x_kg

    @property
    def val_kg(self) -> float:
        return __class__.__to_kg(self.val)

    @property
    def err_min_kg(self) -> float:
        return __class__.__to_kg(self.err_min)

    @property
    def err_max_kg(self) -> float:
        return __class__.__to_kg(self.err_max)
    
    @property
    def err_kg(self) -> float:
        return __class__.__to_kg(self.err)
    

JUP_RAD_M = 6.9911e+7

class Radius(Measure):
    def __init__(self, val: float, err_min: float, err_max: float) -> None:
        super().__init__(val, err_min, err_max)

    @staticmethod
    def __to_m(x: float) -> float:
        x_kg = x * JUP_RAD_M

        return x_kg

    @property
    def val_m(self) -> float:
        return __class__.__to_m(self.val)

    @property
    def err_min_m(self) -> float:
        return __class__.__to_m(self.err_min)

    @property
    def err_max_m(self) -> float:
        return __class__.__to_m(self.err_max)
    
    @property
    def err_m(self) -> float:
        return __class__.__to_m(self.err)
    

class OrbitalPeriod(Measure):
    def __init__(self, val: float, err_min: float, err_max: float) -> None:
        super().__init__(val, err_min, err_max)

    @staticmethod
    def __to_s(x):
        x_s = x * 24 * 60 * 60

        return x_s

    @property
    def val_s(self):
        return __class__.__to_s(self.val)
    
    @property
    def err_min_s(self) -> float:
        return __class__.__to_s(self.err_min)

    @property
    def err_max_s(self) -> float:
        return __class__.__to_s(self.err_max)
    
    @property
    def err_s(self) -> float:
        return __class__.__to_s(self.err)


class TempCalculated(Measure):
    def __init__(self, val: float, err_min: float, err_max: float) -> None:
        super().__init__(val, err_min, err_max)


class StarDistance(Measure):
    def __init__(self, val: float, err_min: float, err_max: float) -> None:
        super().__init__(val, err_min, err_max)


class StarMetalicity(Measure):
    def __init__(self, val: float, err_min: float, err_max: float) -> None:
        super().__init__(val, err_min, err_max)


class StarTeff(Measure):
    def __init__(self, val: float, err_min: float, err_max: float) -> None:
        super().__init__(val, err_min, err_max)