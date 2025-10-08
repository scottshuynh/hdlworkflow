import subprocess
import logging
import os
import sys
from shutil import which

from hdlworkflow import utils

logger = logging.getLogger(__name__)


class Vivado:
    """Run simulations or OOC synthesis using Vivado."""

    def __init__(
        self,
        top: str,
        compile_order: str,
        generics: list[str],
        path_to_working_directory: str,
        part_number: str,
        board_part: str,
        start_gui: bool,
        synth: bool,
        ooc: bool,
        clk_period_constraints: list[str],
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
        self.__pwd: str = path_to_working_directory
        self.__generics: list[str] = generics
        self.__part_number: str = part_number
        self.__board_part: str = board_part
        self.__start_gui: bool = start_gui
        self.__synth: bool = synth
        self.__ooc: bool = ooc
        self.__clk_period_constraints: list[str] = clk_period_constraints

        if not self.__check_dependencies():
            logger.error("Missing dependencies: vivado")
            logger.error("All dependencies must be found on PATH.")
            sys.exit(1)

        os.makedirs(f"{self.__pwd}/vivado", exist_ok=True)
        os.chdir(f"{self.__pwd}/vivado")

    def __check_dependencies(self) -> bool:
        logger.info("Checking dependencies...")
        if not which("vivado"):
            return False
        return True

    def start(self) -> None:
        self.__create_clock_constraint()
        self.__generate_setup_viv_prj()
        self.__start_vivado()

    def __create_clock_constraint(self):
        if self.__clk_period_constraints:
            with open("clock_constraint.xdc", "w") as f:
                for clk_period_constraint in self.__clk_period_constraints:
                    clk_port = clk_period_constraint.split("=")[0]
                    clk_period = clk_period_constraint.split("=")[1]
                    try:
                        float(clk_period)
                    except ValueError:
                        logger.error(f"Expecting float or integer for clock period constraint value. Got: {clk_period}")
                        sys.exit(1)

                    f.write(f"create_clock -period {clk_period} -name {clk_port} [get_ports {clk_port}]\n")

    def __generate_setup_viv_prj(self, target: str = "") -> None:
        logger.info("Generating setup script...")
        if not self.__part_number:
            part = "xc7a35ticsg324-1L"
        else:
            part = self.__part_number

        with open("setup_viv_prj.tcl", "w") as f:
            f.write(f"create_project -part {part} {self.__top} -force\n")
            f.write("set obj [current_project]\n")

            if self.__board_part:
                f.write(f'set_property -name "board_part" -value "{self.__board_part}" -objects $obj\n')

            f.write(f"set fp [open {self.__compile_order}]\n")
            f.write('set lines [split [read -nonewline $fp] "\\n"]\n')
            f.write("close $fp\n")
            f.write("add_files $lines\n")

            if self.__clk_period_constraints:
                f.write("add_files clock_constraint.xdc\n")

            f.write(f"set_property top {self.__top} [current_fileset]\n")
            f.write(f"set_property top {self.__top} [get_filesets sim_1]\n")
            f.write("set_property file_type {VHDL 2008} [get_files *.vhd]\n")

            if self.__generics:
                f.write("set_property -name {steps.synth_design.args.more options} -value {")
                if self.__ooc:
                    f.write("-mode out_of_context ")
                f.write(
                    f"{'-generic ' + ' -generic '.join(generic for generic in self.__generics)}}} -objects [get_runs synth_1]\n"
                )
                f.write(
                    f"set_property -name {{xsim.elaborate.xelab.more_options}} -value {{{'-generic_top ' + ' -generic_top '.join(generic for generic in self.__generics)}}} -objects [get_filesets sim_1]\n"
                )
            else:
                if self.__ooc:
                    f.write(
                        "set_property -append -name {steps.synth_design.args.more options} -value {-mode out_of_context} -objects [get_runs synth_1]\n"
                    )

            if self.__start_gui:
                f.write("start_gui\n")
            if self.__synth:
                f.write("reset_run synth_1\n")
                if not self.__start_gui:
                    f.write(f"launch_runs synth_1 -jobs {min(os.cpu_count() // 2, 8)}\n")
                    f.write("wait_on_run synth_1\n")
                    f.write('if {[get_property PROGRESS [get_runs synth_1]] != "100%"} {\n')
                    f.write('    error "ERROR: Synthesis failed."\n')
                    f.write("}\n")

                    f.write(f"launch_runs impl_1 -jobs {min(os.cpu_count() // 2, 8)}\n")
                    f.write("wait_on_run impl_1\n")
                    f.write('if {[get_property PROGRESS [get_runs impl_1]] != "100%"} {\n')
                    f.write('    error "ERROR: Implementation failed."\n')
                    f.write("}\n")

                    f.write("if {[get_property STATS.WNS [get_runs impl_1]] < 0} {\n")
                    f.write('    error "ERROR: Timing failed."\n')
                    f.write("}\n")
                else:
                    f.write(f"launch_runs impl_1 -jobs {min(os.cpu_count() // 2, 8)}\n")
            else:
                f.write("launch_simulation")

    def __start_vivado(self) -> None:
        logger.info("Starting Vivado...")
        command = [
            "vivado",
            "-mode",
            "batch",
            "-nolog",
            "-nojournal",
            "-notrace",
            "-quiet",
            "-source",
            "setup_viv_prj.tcl",
        ]
        logger.info("    " + " ".join(cmd for cmd in command))
        vivado = subprocess.run(command)
        if vivado.returncode != 0:
            logger.error("Error when running Vivado.")
            sys.exit(1)
