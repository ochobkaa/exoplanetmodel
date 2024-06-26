import pandas as pd
import numpy as np
import measures as ms
import calculators as calc
import errors as err
import tables as tab
from conversion import MeasureConverter
from abc import ABC, abstractmethod
from typing import Iterable, Dict


class DFTransformer(ABC):
    def __init__(self, con: MeasureConverter) -> None:
        self.__con = con

    def _col_measures(self, df: pd.DataFrame, 
                      col: str, col_type: type) -> Iterable[ms.Measure]:
        con = self.__con
        measures = list(con.read(col, col_type, df))

        return measures

    def _col_vals[T](self, df: pd.DataFrame, col: str, val_type: type) -> Iterable[T]:
        vals = df.get(col).map(val_type).to_list()

        return vals
    
    def _write_measures(self, df: pd.DataFrame, vals: Iterable[ms.Measure], 
                        col: str) -> pd.DataFrame:
        con = self.__con

        vals_list = list(vals)
        new_df = con.write(col, vals_list, df)

        return new_df


class DFCalculation(DFTransformer):
    def __init__(self, 
                 con: MeasureConverter, cal: calc.Calculator, rou: err.Round,
                 col: str, col_type: type, args: Dict[str, type]
                ) -> None:
        super().__init__(con)
        self.__col = col
        self.__col_type = col_type
        self.__cal = cal
        self.__rou = rou
        self.__args = args

    def _args_measures(self, df: pd.DataFrame, 
                          args: Dict[str, type]) -> Dict[str, Iterable[ms.Measure]]:
        args_ms = {}
        for arg_col, arg_type in args.items():
            args_ms[arg_col] = self._col_measures(df, arg_col, arg_type)

        return args_ms

    def calc(self, df: pd.DataFrame) -> pd.DataFrame:
        def arg_isna(*args):
            isna = not all(map(lambda a: pd.notna(a.val), *args))
            return isna
        
        def calc_measures(cal: calc.Calculator, rou: err.Round, col_ms: Iterable[ms.Measure],
                          args_ms: Dict[str, Iterable[ms.Measure]]) -> Iterable[ms.Measure]:
            for ccol, cargs in zip(col_ms, zip(*args_ms.values())):
                if pd.notna(ccol.val):
                    yield ccol

                elif arg_isna(cargs):
                    yield None

                else:
                    kwcargs = dict(zip(args_ms.keys(), cargs))

                    calc_ms = cal.calc(**kwcargs)

                    rou_err = rou.round_err(calc_ms.err)
                    
                    rou_val = rou.round_val(calc_ms.val, rou_err)

                    ms_t = type(calc_ms)
                    calc_ms_rou = ms_t(rou_val, rou_err, rou_err)

                    yield calc_ms_rou

        cal = self.__cal
        rou = self.__rou
        col = self.__col
        col_type = self.__col_type
        args = self.__args

        col_ms = self._col_measures(df, col, col_type)
        args_ms = self._args_measures(df, args)
        calc_ms = calc_measures(cal, rou, col_ms, args_ms)
        new_df = self._write_measures(df, calc_ms, col)

        return new_df
    

class DFSemiMajorAxisCalc(DFCalculation):
    def __init__(self, con: MeasureConverter, 
                 cal: calc.SemiMajorAxisCalc, rou: err.Round) -> None:
        super().__init__(
            con, 
            cal,
            rou,
            "semi_major_axis",
            ms.SemiMajorAxis,
            {
                "star_mass": ms.StarMass,
                "orbital_period": ms.OrbitalPeriod
            }
        )


class DFPlanetTeffMeanCalc(DFCalculation):
    def __init__(self, con: MeasureConverter, 
                 cal: calc.PlanetTeffCalc, rou: err.Round) -> None:
        super().__init__(
            con, 
            cal, 
            rou,
            "temp_calculated",
            ms.TempCalculated,
            {
                "star_teff": ms.StarTeff,
                "star_radius": ms.StarRadius,
                "semi_major_axis": ms.SemiMajorAxis
            }
        )
    

class DFValFromTable[TTableKey, TValIn](DFTransformer):
    def __init__(self, con: MeasureConverter, table: tab.Table[TTableKey, TValIn],
                 col: str, col_type: type, col_arg: str, col_arg_type: type) -> None:
        super().__init__(con)
        self.__table = table
        self.__col = col
        self.__col_type = col_type
        self.__col_arg = col_arg
        self.__col_arg_type = col_arg_type

    def set_vals(self, df: pd.DataFrame) -> pd.DataFrame:
        def vals_from_table(table: tab.Table[TTableKey, TValIn],
                            col_vals: Iterable[ms.Measure],
                            cargs: Iterable[TValIn]) -> Iterable[ms.Measure]:
            for carg, col_val in zip(cargs, col_vals):
                if col_val and pd.notna(col_val.val):
                    yield col_val

                elif not carg:
                    yield None
                
                else:
                    new_ms = table.get_ms(carg)
                    yield new_ms
        
        table = self.__table
        col = self.__col
        col_type = self.__col_type
        col_arg = self.__col_arg
        col_arg_type = self.__col_arg_type

        col_ms = self._col_measures(df, col, col_type)
        col_args = self._col_vals(df, col_arg, col_arg_type)
        tvals_ms = vals_from_table(table, col_ms, col_args)
        new_df = self._write_measures(df, tvals_ms, col)
        
        return new_df
    

class DFStarTeffBySpClassCalc(DFValFromTable[str, float]):
    def __init__(self, con: MeasureConverter, table: tab.SpClassTeffTable) -> None:
        super().__init__(
            con,
            table,
            "star_teff",
            ms.StarTeff,
            "star_sp_type",
            str
        )


class DFErrorGen(DFTransformer):
    def __init__(self,
                 con: MeasureConverter,  err_gen: err.ErrorGenerator,
                 col: str, col_type: type) -> None:
        super().__init__(con)
        self.__err_gen = err_gen
        self.__col = col
        self.__col_type = col_type

    def gen(self, df: pd.DataFrame) -> pd.DataFrame:
        def gen_errs(measures: Iterable[ms.Measure], 
                     err_gen: err.ErrorGenerator, 
                     ms_type: type) -> Iterable[ms.Measure]:
            def is_nonset(val) -> bool:
                return not val or pd.isna(val)

            for ms in measures:
                if is_nonset(ms.val):
                    yield None

                elif is_nonset(ms.err_min) and is_nonset(ms.err_max):
                    err = err_gen.gen(ms.val)
                    new_ms = ms_type(ms.val, err, err)
                    yield new_ms

                elif is_nonset(ms.err_min):
                    new_ms = ms_type(ms.val, ms.err_max, ms.err_max)
                    yield new_ms

                elif is_nonset(ms.err_max):
                    new_ms = ms_type(ms.val, ms.err_min, ms.err_min)
                    yield new_ms

                else:
                    yield ms

        err_gen = self.__err_gen
        col = self.__col
        col_type = self.__col_type

        measures = self._col_measures(df, col, col_type)
        new_measures = gen_errs(measures, err_gen, col_type)
        new_df = self._write_measures(df, new_measures, col)

        return new_df
    

class DFStarCalculator(DFCalculation):
    def __init__(self, con: MeasureConverter, 
                 cal: calc.Calculator, rou: err.Round, star_calc_t: type,
                 col: str, col_type: type, args: Dict[str, type]) -> None:
        super().__init__(con, cal, rou, col, col_type, args)
        self.__con = con
        self.__col = col
        self.__col_type = col_type
        self.__star_calc = star_calc_t(rou, col_type)

    def calc(self, df: pd.DataFrame) -> pd.DataFrame:
        def get_stars(df: pd.DataFrame) -> Iterable[str]:
            col = self.__col
            col_nulls = df[pd.isna(df[col])]

            stars = list(set(col_nulls["star_name"].to_list()))

            return stars

        def select_star_planets(df: pd.DataFrame, star_name: str) -> pd.DataFrame:
            star_planets = df[df.star_name == star_name]

            return star_planets
        
        def write_star(df: pd.DataFrame, con: MeasureConverter, s_ms: ms.Measure, col: str, star_name: str) -> pd.DataFrame:
            cond = "star_name == \"{star_name}\"".format(star_name=star_name)
            new_df = con.write_val_if(col, s_ms, df, cond)

            return new_df

        con = self.__con
        col = self.__col
        col_type = self.__col_type
        star_calc = self.__star_calc        

        stars = get_stars(df)
        new_df = df
        for star in stars:
            star_planets = select_star_planets(df, star)
            p_vals = super().calc(star_planets)
            p_col_ms = self._col_measures(p_vals, col, col_type)

            s_ms = star_calc.calc(p_col_ms)
            
            new_df = write_star(new_df, con, s_ms, col, star)

        return new_df
    

class DFStarMassCalculator(DFStarCalculator):
    def __init__(self, con: MeasureConverter, cal: calc.StarMassCalc, rou: err.Round, star_calc_t: type) -> None:
        super().__init__(
            con, 
            cal, 
            rou, 
            star_calc_t, 
            "star_mass", 
            ms.StarMass, 
            {
                "semi_major_axis": ms.SemiMajorAxis,
                "orbital_period": ms.OrbitalPeriod
            }
        )