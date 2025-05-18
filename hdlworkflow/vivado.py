import subprocess
from pathlib import Path
import os
import sys
from shutil import which
from typing import List


class Vivado:
    """Run simulations using Vivado."""

    def __init__(
        self,
        top: str,
        compile_order: str,
        generics: List[str],
        path_to_working_directory: str,
        is_prj_mode: bool = True,
    ):
        path_to_compile_order = compile_order
        if os.path.isabs(path_to_compile_order):
            if not self.__is_file(path_to_compile_order):
                print(f"{type(self).__name__}: {path_to_compile_order} does not exist.")
                sys.exit(1)
        else:
            path_to_compile_order = path_to_working_directory + f"/{compile_order}"
            if not self.__is_file(path_to_compile_order):
                print(f"{type(self).__name__}: {path_to_compile_order} does not exist.")
                sys.exit(1)

        self.__top: str = top
        self.__compile_order: str = path_to_compile_order
        self.__generics: List[str] = generics
        self.__is_prj_mode: bool = is_prj_mode

        if not self.__check_dependencies():
            print(f"{type(self).__name__}: Missing dependencies: vivado")
            sys.exit(1)

        os.makedirs("vivado", exist_ok=True)
        os.chdir("vivado")

    def __is_file(self, file: str) -> bool:
        filepath = Path(file)
        return filepath.is_file()

    def __check_dependencies(self) -> bool:
        if not which("vivado"):
            return False
        return True

    def simulate(self) -> None:
        if self.__is_prj_mode:
            self.__create_clock_constraint()
            self.__generate_setup_viv_prj()
            self.__start_vivado()

    def __create_clock_constraint(self):
        with open("clock_constraint.xdc", "w") as f:
            f.write("create_clock -period 4.000 -name clk [get_ports clk_i]")

    def __generate_setup_viv_prj(self, target: str = "") -> None:
        if not target:
            part = "xc7a35ticsg324-1L"
        else:
            part = target
        with open("setup_viv_prj.tcl", "w") as f:
            f.write(
                f"""create_project -part {part} {self.__top} -force
set fp [open {self.__compile_order}]
set lines [split [read -nonewline $fp] "\\n"]
close $fp
add_files $lines
add_files -fileset constrs_1 clock_constraint.xdc
set_property top {self.__top} [current_fileset]
set_property file_type {{VHDL 2008}} [get_files *.vhd]
set_property -name {{steps.synth_design.args.more options}} -value {{-mode out_of_context {"-generic " + " -generic ".join(generic for generic in self.__generics)}}} -objects [get_runs synth_1]
set_property -name {{xsim.elaborate.xelab.more_options}} -value {{{"-generic_top " + " -generic_top ".join(generic for generic in self.__generics)}}} -objects [get_filesets sim_1]
start_gui"""
            )

    def __start_vivado(self) -> None:
        vivado = subprocess.run(["vivado", "-mode", "batch", "-source", "setup_viv_prj.tcl"])
        if vivado.returncode != 0:
            print(f"{type(self).__name__}: Error during project initialisation.")
            sys.exit(1)
