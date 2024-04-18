import pandas as pd
import measures as ms
import calculators as calc
import errors as err
from conversion import MeasureConverter
from abc import ABC, abstractmethod
from typing import Iterable, Dict

class DFCalculation(ABC):
    def __init__(self, 
                 con: MeasureConverter, cal: calc.Calculator, rou: err.Round,
                 col_calc: str, col_type: type, args: Dict[str, type]
                ) -> None:
        self.__con = con
        self.__cal = cal
        self.__rou = rou
        self.__col_calc = col_calc
        self.__col_type = col_type
        self.__args = args

    def calc(self, df: pd.DataFrame) -> pd.DataFrame:
        def args_measures(con: MeasureConverter, 
                          args: Dict[str, type], 
                          df: pd.DataFrame) -> Dict[str, Iterable[ms.Measure]]:
            args_ms = {}
            for arg_col, arg_type in args.items():
                args_ms[arg_col] = list(con.read(arg_col, arg_type, df))

            return args_ms
        
        def arg_isna(*args):
            isna = not all(map(lambda a: pd.notna(a.val), *args))
            return isna
        
        def col_measures(con: MeasureConverter,
                         col_calc: str,
                         col_type: type,
                         df: pd.DataFrame) -> Iterable[ms.Measure]:
            measures = list(con.read(col_calc, col_type, df))

            return measures
        
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
                

        def write_measures(con: MeasureConverter, 
                           col: str, 
                           vals: Iterable[ms.Measure], 
                           df: pd.DataFrame) -> pd.DataFrame:
            vals_list = list(vals)
            new_df = con.write(col, vals_list, df)

            return new_df

        con = self.__con
        cal = self.__cal
        rou = self.__rou
        col_calc = self.__col_calc
        col_type = self.__col_type
        args = self.__args

        col_ms = col_measures(con, col_calc, col_type, df)
        args_ms = args_measures(con, args, df)
        calc_ms = calc_measures(cal, rou, col_ms, args_ms)
        new_df = write_measures(con, col_calc, calc_ms, df)

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


class DFStarTeffBySpClassCalc(DFCalculation):
    def __init__(self, con: MeasureConverter, cal: calc.StarTeffBySpCalc) -> None:
        self.__con = con
        self.__teff_calc = cal

    def calc(self, df: pd.DataFrame) -> pd.DataFrame:
        def read_sp_types(df: pd.DataFrame) -> Iterable[str]:
            sp_types = df.get("star_sp_type").map(str).to_list()

            return sp_types
        
        def read_star_teff(con: MeasureConverter, df: pd.DataFrame) -> Iterable[ms.StarTeff]:
            star_teff_ms = list(con.read("star_teff", ms.StarTeff, df))

            return star_teff_ms
        
        def calc_steff(cal: calc.StarTeffBySpCalc, sp_types: Iterable[str], star_teff: Iterable[ms.StarTeff]) -> Iterable[ms.StarTeff]:
            for sp_type, steff_ms in zip(sp_types, star_teff):
                if steff_ms and pd.notna(steff_ms.val):
                    yield steff_ms

                elif not sp_type:
                    yield None
                
                else:
                    t_value = cal.calc(sp_type)
                    if t_value:
                        new_ms = ms.StarTeff(t_value.teff, t_value.err, t_value.err)

                        yield new_ms

                    else:
                        yield None

        def write_measures(con: MeasureConverter, 
                           col: str, 
                           vals: Iterable[ms.Measure], 
                           df: pd.DataFrame) -> pd.DataFrame:
            vals_list = list(vals)
            new_df = con.write(col, vals_list, df)

            return new_df
        
        con = self.__con
        cal = self.__teff_calc

        sp_types = read_sp_types(df)
        steff_ms = read_star_teff(con, df)
        steff_ms_calc = calc_steff(cal, sp_types, steff_ms)
        new_df = write_measures(con, "star_teff", steff_ms_calc, df)

        return new_df


class DFErrorGen:
    def __init__(self,
                 con: MeasureConverter,  err_gen: err.ErrorGenerator,
                 col_gen: str, col_type: type) -> None:
        self.__con = con
        self.__err_gen = err_gen
        self.__col_gen = col_gen
        self.__col_type = col_type

    def gen(self, df: pd.DataFrame) -> pd.DataFrame:
        def col_measures(con: MeasureConverter,
                         col_gen: str,
                         col_type: type, 
                         df: pd.DataFrame) -> Iterable[ms.Measure]:
            measures = list(con.read(col_gen, col_type, df))

            return measures

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

        def write_measures(con: MeasureConverter, 
                           col: str, 
                           vals: Iterable[ms.Measure], 
                           df: pd.DataFrame) -> pd.DataFrame:
            vals_list = list(vals)
            new_df = con.write(col, vals_list, df, write_val=False)

            return new_df

        con = self.__con
        err_gen = self.__err_gen
        col_gen = self.__col_gen
        col_type = self.__col_type

        measures = col_measures(con, col_gen, col_type, df)
        new_measures = gen_errs(measures, err_gen, col_type)
        new_df = write_measures(con, col_gen, new_measures, df)

        return new_df