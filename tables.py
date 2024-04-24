import measures as ms
import re
from abc import ABC, abstractmethod
from collections import namedtuple
from numpy import arange

_TableValue = namedtuple("TableValue", ["val", "err"], defaults=[0.0, 0.0])
_Interval = namedtuple("Interval", ["min", "max"], defaults=[0.0, 0.0])

class Table[TTableKey, TValIn](ABC):
    def __init__(self, table: dict[TTableKey, _TableValue], ms_type: type) -> None:
        self.__table = self.__sort_table(table)
        self.__ms_type = ms_type

    def __sort_table(self, table: dict[TTableKey, _TableValue]) -> dict[TTableKey, _TableValue]:
        new_table = dict(sorted(table.items(), key=lambda v: v[1].val))
        
        return new_table

    @property
    def table(self) -> dict[TTableKey, _TableValue]:
        return self.__table
    
    @abstractmethod
    def _get_table_value(self, val_in: TValIn) -> _TableValue:
        pass
    
    def get_ms(self, val_in: TValIn) -> ms.Measure:
        ms_type = self.__ms_type

        table_value = self._get_table_value(val_in)
        if table_value:
            val_out = table_value.val
            err_out = table_value.err

            ms_value = ms_type(val_out, err_out, err_out)

            return ms_value
    
    def get_err_by_val(self, val: float) -> float:
        t_vals = list(self.table.values())

        for i in range(len(t_vals)):
            if t_vals[i] > val and i > 0:
                return t_vals[i - 1].err
            
            
class StrTable(Table[str, str]):
    def __init__(self, table: dict[str, _TableValue], ms_type: type) -> None:
        super().__init__(table, ms_type)

    def _get_table_value(self, val_in: str) -> _TableValue:
        table_value = self.table[val_in]

        return table_value
    

class IntervalTable(Table[_Interval, float]):
    def __init__(self, table: dict[_Interval, _TableValue], ms_type: type) -> None:
        super().__init__(table, ms_type)
    
    def _get_table_value(self, val_in: float) -> _TableValue:
        for interval, tab_val in self.table.items():
            min_val = interval.min
            max_val = interval.max
            if min_val < val_in and val_in <= max_val:
                return tab_val
    

class SpClassTeffTable(StrTable):
    __ParsedSpClass = namedtuple("ParsedSpClass", ["letter", "number"], defaults=["", 0.0])

    def __init__(self, raw_table: dict[str, tuple[float, float]]) -> None:
        new_table = self.__build_table(raw_table)

        super().__init__(new_table, ms.StarTeff)

    def __build_table(self, raw_table: dict[str, tuple[float, float]]) -> dict[_Interval, _TableValue]:
        new_table = {}
        for cl_let, cl_intr in raw_table.items():
            key = "{cl}-1".format(cl=cl_let)

            err = cl_intr[1] - cl_intr[0]
            val = cl_intr[0] + err / 2

            new_table[key] = _TableValue(val=val, err=err)

            for sub in arange(0, 10, 0.5):
                key = "{cl}{sub}".format(cl=cl_let, sub=sub)

                sub_intr = (cl_intr[1] - cl_intr[0]) / 10
                err = sub_intr / 2
                val = cl_intr[0] + (9 - sub) * sub_intr + err

                new_table[key] = _TableValue(val=val, err=err)

        print(new_table)
        return new_table
                
    def __parse_sp_class(self, sp_class: str) -> __ParsedSpClass:
        sp_pattern1 = r"^[BAFGKM]\d(\.\d)?"
        sp_match1 = re.match(sp_pattern1, sp_class)
        if sp_match1:
            sp_cleared = sp_match1.group(0)
            
            letter = sp_cleared[0]
            number = float(sp_cleared[1:])
            parsed_sp = self.__ParsedSpClass(letter, number)
            
            return parsed_sp
        
        sp_pattern2 = r"^[BAFGKM]"
        sp_match2 = re.match(sp_pattern2, sp_class)
        if sp_match2:
            sp_cleared = sp_match2.group(0)
            
            letter = sp_cleared[0]
            number = -1
            parsed_sp = self.__ParsedSpClass(letter, number)
            
            return parsed_sp
        
    def __build_sp_class(self, parsed_sp: __ParsedSpClass) -> str:
        letter = parsed_sp.letter
        sub = parsed_sp.number
        sp_cl = "{let}{sub}".format(let=letter, sub=sub)

        return sp_cl

    def _get_table_value(self, val_in: str) -> _TableValue:
        parsed_sp = self.__parse_sp_class(val_in)
        if parsed_sp:
            sp_cl = self.__build_sp_class(parsed_sp)

            table_value = super()._get_table_value(sp_cl)

            return table_value