import subprocess
import logging
import os
import sys
from shutil import which
from typing import List

from hdlworkflow import utils

logger = logging.getLogger(__name__)


class Vivado:
    """Run simulations or OOC synthesis using Vivado."""

    def __init__(
        self,
        top: str,
        compile_order: str,
        generics: List[str],
        path_to_working_directory: str,
        part_number: str,
        board_part: str,
    ):
        logger.info(f"Initialising {type(self).__name__}...")
        path_to_compile_order = compile_order
        if os.path.isabs(path_to_compile_order):
            if not utils.is_file(path_to_compile_order):
                logger.error(f"Path to compile order ({path_to_compile_order}) does not exist.")
                sys.exit(1)
        else:
            path_to_compile_order = path_to_working_directory + f"/{compile_order}"
            if not utils.is_file(path_to_compile_order):
                logger.error(f"Path to compile order ({path_to_compile_order}) does not exist.")
                sys.exit(1)

        self.__top: str = top
        self.__compile_order: str = path_to_compile_order
        self.__generics: List[str] = generics
        self.__part_number: str = part_number
        self.__board_part: str = board_part

        if not self.__check_dependencies():
            logger.error("Missing dependencies: vivado")
            logger.error("All dependencies must be found on PATH.")
            sys.exit(1)

        os.makedirs("vivado", exist_ok=True)
        os.chdir("vivado")

    def __check_dependencies(self) -> bool:
        logger.info("Checking dependencies...")
        if not which("vivado"):
            return False
        return True

    def start(self) -> None:
        self.__create_clock_constraint()
        self.__generate_setup_viv_prj(self.__part_number)
        self.__start_vivado()

    def __create_clock_constraint(self):
        logger.info("Constraining clock port (clk_i) to 500 MHz...")
        with open("clock_constraint.xdc", "w") as f:
            f.write("create_clock -period 2.000 -name clk [get_ports clk_i]")

    def __generate_setup_viv_prj(self, target: str = "") -> None:
        logger.info("Generating setup script...")
        if not target:
            part = "xc7a35ticsg324-1L"
        else:
            part = target

        with open("setup_viv_prj.tcl", "w") as f:
            f.write(f"create_project -part {part} {self.__top} -force\n")
            f.write("set obj [current_project]\n")

            if self.__board_part:
                f.write(f'set_property -name "board_part" -value "{self.__board_part}" -objects $obj\n')

            f.write(f"set fp [open {self.__compile_order}]\n")
            f.write('set lines [split [read -nonewline $fp] "\\n"]\n')
            f.write("close $fp\n")
            f.write("add_files $lines\n")
            f.write("add_files -fileset constrs_1 clock_constraint.xdc\n")
            f.write(f"set_property top {self.__top} [current_fileset]\n")
            f.write("set_property file_type {VHDL 2008} [get_files *.vhd]\n")

            if self.__generics:
                f.write(
                    f"set_property -name {{steps.synth_design.args.more options}} -value {{-mode out_of_context {'-generic ' + ' -generic '.join(generic for generic in self.__generics)}}} -objects [get_runs synth_1]\n"
                )
                f.write(
                    f"set_property -name {{xsim.elaborate.xelab.more_options}} -value {{{'-generic_top ' + ' -generic_top '.join(generic for generic in self.__generics)}}} -objects [get_filesets sim_1]\n"
                )
            else:
                f.write(
                    "set_property -name {{steps.synth_design.args.more options}} -value {{-mode out_of_context}} -objects [get_runs synth_1]\n"
                )

            f.write("start_gui")

    def __start_vivado(self) -> None:
        logger.info("Starting Vivado...")
        vivado = subprocess.run(
            ["vivado", "-mode", "batch", "-nolog", "-nojournal", "-notrace", "-quiet", "-source", "setup_viv_prj.tcl"]
        )
        if vivado.returncode != 0:
            logger.error("Error during project initialisation.")
            sys.exit(1)
