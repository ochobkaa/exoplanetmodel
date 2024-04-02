import numpy as np

class ErrorGenerator:
    def __init__(self) -> None:
        pass

    def __get_min_ord(self, val: float) -> int:
        val_str = str(val)

        try:
            dot_pos = val_str.rindex('.')

        except ValueError:
            dot_pos = 0

        if dot_pos > 0:
            order = dot_pos - len(val_str) + 1
            return order
        
        try:
            last_zero_pos = val_str.rindex('0')

        except ValueError:
            last_zero_pos = 0

        if last_zero_pos != len(val_str) - 1:
            return 0
        
        for i in reversed(range(len(val_str))):
            if val_str != 0:
                order = len(val_str) - i
                return order
                
    def gen(self, val: float) -> float:
        order = self.__get_min_ord(val)

        err = 5 * 10 ** order
        return err
    

class Round:
    def __init__(self) -> None:
        pass

    def __order(self, val: float) -> int:
        order = int(np.log10(val))
        return order
    
    def __norm(self, val: float) -> float:
        norm = val / self.__order(val)
        return norm
    
    def __round(self, val: float, order: int) -> float:
        order = self.__order(val)
        norm = val / order

        norm_r = np.round(norm, order)
        val_r = norm_r * order

        return val_r
    
    def round_err(self, err: float) -> float:
        err_norm = self.__norm(err)
        err_max_d = int(err_norm)

        if err_max_d > 2:
            err_r = self.__round(err, 1)

        else:
            err_r = self.__round(err, 2)

        return err_r
    
    def round_val(self, val: float, err: float) -> float:
        err_ord = self.__order(err)

        val_r = np.round(val, err_ord)
        return val_r