import numpy as np
from abc import ABC, abstractmethod

class ErrorGenerator(ABC):
    @abstractmethod
    def gen(self, val: float):
        pass


class ErrorGeneratorByOrder(ErrorGenerator):
    def __init__(self) -> None:
        pass

    def __get_min_ord(self, val: float) -> int:
        val_str = str(val)

        try:
            dot_pos = val_str.rindex('.')
            has_point = True

        except ValueError:
            dot_pos = 0
            has_point = False

        if dot_pos > 0 and dot_pos != len(val_str) - 1 and val_str[len(val_str) - 1] != '0':
            order = dot_pos - len(val_str) + 1
            return order
        
        try:
            last_zero_pos = val_str.rindex('0')

        except ValueError:
            last_zero_pos = 0

        if last_zero_pos != len(val_str) - 1:
            return 0
        
        for i in reversed(range(len(val_str))):
            if val_str[i] != '0' and val_str[i] != '.':
                order = len(val_str) - i - 1

                if has_point:
                    order -= 2

                return order
                
    def gen(self, val: float) -> float:
        order = self.__get_min_ord(val)

        err = 5 * 10 ** order
        return err
    

class ErrorGeneratorStarTeff(ErrorGenerator):
    def gen(self, val: float) -> float:
        return 100
    

class Round:
    def __init__(self) -> None:
        pass

    def __order(self, val: float) -> int:
        abs_val = abs(val)
        if abs_val > 0:
            order = int(np.log10(abs_val))
            if abs_val < 1:
                order = order - 1

            return order
    
    def __norm(self, val: float, order: int = None) -> float:
        if order == None:
            new_order = self.__order(val)

        else:
            new_order = order

        if new_order == None:
            return
        
        norm = val * 10 ** (-new_order)
        return norm
    
    def __round(self, val: float, order: int) -> float:
        val_order = self.__order(val)
        if val_order == None:
            return

        norm = self.__norm(val, val_order)

        norm_r = round(norm, abs(order))

        val_r = norm_r * 10 ** val_order

        return val_r
    
    def round_err(self, err: float) -> float:
        err_norm = self.__norm(err)
        if not err_norm:
            return err

        err_max_d = int(err_norm)

        if err_max_d > 2:
            err_r = self.__round(err, 0)

        else:
            err_r = self.__round(err, 1)

        return err_r
    
    def round_val(self, val: float, err: float) -> float:
        err_ord = self.__order(err)
        if not err_ord:
            return val

        val_r = self.__round(val, err_ord)
        return val_r