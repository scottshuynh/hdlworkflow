import subprocess
import logging
from pathlib import Path
from importlib.metadata import version
from importlib.util import find_spec
import os
import sys
from shutil import which
from typing import List, Tuple, Dict

from hdlworkflow import utils

logger = logging.getLogger(__name__)


class Riviera:
    """Run simulations using Rivera-PRO"""

    def __init__(
        self,
        top: str,
        compile_order: str,
        generics: List[str],
        cocotb_module: str,
        waveform_viewer: str,
        path_to_working_directory: str,
        pythonpaths: List[str],
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

        self.__compile_order: str = path_to_compile_order
        self.__top: str = top
        self.__generics: List[str] = generics
        self.__cocotb_module: str = cocotb_module
        self.__pwd: str = path_to_working_directory
        self.__pythonpaths: List[str] = utils.prepend_pwd_if_relative(pythonpaths, path_to_working_directory)

        self.__waveform_viewer: str = waveform_viewer
        self.__waveform_file: str = self.__top
        if generics:
            self.__waveform_file += ''.join(generic for generic in self.__generics) + ".awc"
        else:
            self.__waveform_file += ".awc"

        dependencies_met, missing = self.__check_dependencies()
        if not dependencies_met:
            logger.error(f"Missing dependencies: {' '.join(str(dependency) for dependency in missing)}.")
            logger.error(f"All dependencies must be found on PATH.")
            sys.exit(1)

        os.makedirs("riviera", exist_ok=True)
        os.chdir("riviera")

    def __check_dependencies(self) -> Tuple[bool, List[str]]:
        logger.info("Checking dependencies...")
        dependencies = ["vsim", "vsimsa"]
        missing: List[str] = []
        for dependency in dependencies:
            if not which(dependency):
                missing.append(dependency)
        if self.__cocotb_module:
            if not find_spec("cocotb"):
                missing.append("cocotb")
        if missing:
            return tuple([False, missing])
        else:
            return tuple([True, None])

    def simulate(self) -> None:
        self.__flatten_compile_order()
        self.__check_mixed_hdl()

        major = 0
        if self.__cocotb_module:
            major, minor, patch = utils.get_cocotb_version()

        self.__batch_mode_run(major)
        # TODO: CLI mode.
        # self.__initialise_work_lib()
        # self.__compile()
        # self.__run_cocotb(major)
        # else:
        # self.__run()

    def __flatten_compile_order(self) -> None:
        self.__vhdl_files: List[str] = []
        self.__verilog_files: List[str] = []
        self.__sysverilog_files: List[str] = []
        self.__hdl_files: List[str] = []

        with open(self.__compile_order) as f:
            for line in f:
                hdl_file: str = line.strip()
                self.__hdl_files.append(hdl_file)
                ext = Path(hdl_file).suffix
                if ext:
                    if ext == ".vhd" or ext == ".vhdl":
                        if self.__top in line:
                            self.__top_type = "vhdl"
                        self.__vhdl_files.append(hdl_file)
                    elif ext == ".v":
                        if self.__top in line:
                            self.__top_type = "verilog"
                        self.__verilog_files.append(hdl_file)
                    elif ext == ".sv":
                        if self.__top in line:
                            self.__top_type = "verilog"
                        self.__sysverilog_files.append(hdl_file)

    def __check_mixed_hdl(self) -> None:
        self.__all_vhdl: bool = False
        self.__all_verilog: bool = False
        self.__all_sysverilog: bool = False
        if self.__vhdl_files and not self.__verilog_files and not self.__sysverilog_files:
            self.__all_vhdl = True
        elif self.__verilog_files and not self.__vhdl_files and not self.__sysverilog_files:
            self.__all_verilog = True
        elif self.__sysverilog_files and not self.__vhdl_files and not self.__verilog_files:
            self.__all_sysverilog = True

    def __initialise_work_lib(self) -> None:
        """Deprecated."""
        command = ["vlib", "work"]
        vlib = subprocess.run(command)
        if vlib.returncode != 0:
            logger.error("Error during vlib setup.")
            sys.exit(1)

    def __compile(self) -> None:
        """Deprecated."""
        compiled = False
        if self.__all_vhdl:
            command = ["vcom", "-work", "work", "-2008", "-incr"]
            for vhdl_file in self.__vhdl_files:
                command.append(vhdl_file)
        elif self.__all_verilog:
            command = ["vlog", "-work", "work", "-v2k5", "incr"]
            for verilog_file in self.__verilog_files:
                command.append(verilog_file)
        elif self.__all_sysverilog:
            command = ["vlog", "-work", "work", "-sv2k17", "incr"]
            for sysverilog_file in self.__sysverilog_files:
                command.append(sysverilog_file)
        else:
            compiled = True
            for hdl_file in self.__hdl_files:
                ext = Path(hdl_file).suffix
                if ext:
                    if ext == ".vhd" or ext == ".vhdl":
                        command = ["vcom", "-work", "work", "-2008", "-incr", hdl_file]
                    elif ext == ".v":
                        command = ["vlog", "-work", "work", "-v2k5", "-incr", hdl_file]
                    elif ext == ".sv":
                        command = ["vlog", "-work", "work", "-sv2k17", "-incr", hdl_file]

                compile = subprocess.run(command)
                if compile.returncode != 0:
                    logger.error("Error during analysis.")
                    sys.exit(1)

        if not compiled:
            compile = subprocess.run(command)
            if compile.returncode != 0:
                logger.error("Error during analysis.")
                sys.exit(1)

    def __setup_cocotb_env(self, major_ver: int) -> Dict[str, str]:
        libpython_loc = subprocess.run(["cocotb-config", "--libpython"], capture_output=True, text=True).stdout.strip()
        if self.__top_type == "vhdl":
            cocotb_vhpi = (
                subprocess.run(
                    ["cocotb-config", "--lib-name-path", "vhpi", "riviera"], capture_output=True, text=True
                ).stdout.strip()
                + ":vhpi_startup_routines_bootstrap"
            )
            gpi_extra = (
                subprocess.run(
                    ["cocotb-config", "--lib-name-path", "vpi", "riviera"], capture_output=True, text=True
                ).stdout.strip()
                + ":cocotbvpi_entry_point"
            )
        elif self.__top_type == "verilog":
            cocotb_vhpi = subprocess.run(
                ["cocotb-config", "--lib-name-path", "vpi", "riviera"], capture_output=True, text=True
            ).stdout.strip()
            gpi_extra = (
                subprocess.run(
                    ["cocotb-config", "--lib-name-path", "vhpi", "riviera"], capture_output=True, text=True
                ).stdout.strip()
                + ":cocotbvhpi_entry_point"
            )

        env = os.environ.copy()
        env["PYTHONPATH"] = f"{':'.join(str(path) for path in self.__pythonpaths)}:" + env.get("PYTHONPATH", "")
        env["LIBPYTHON_LOC"] = libpython_loc
        env["GPI_EXTRA"] = gpi_extra
        env["TOPLEVEL"] = self.__top
        if not self.__waveform_viewer:
            env["COCOTB_ANSI_OUTPUT"] = "1"
        if major_ver >= 2:
            pygpi_python_bin = subprocess.run(
                ["cocotb-config", "--python-bin"], capture_output=True, text=True
            ).stdout.strip()
            env["PYGPI_PYTHON_BIN"] = pygpi_python_bin
            env["COCOTB_TEST_MODULES"] = self.__cocotb_module
        else:
            env["MODULE"] = self.__cocotb_module

        return env

    def __setup_procedural_interface(self) -> str:
        result: str = ""
        if self.__top_type == "vhdl":
            result = (
                subprocess.run(
                    ["cocotb-config", "--lib-name-path", "vhpi", "riviera"], capture_output=True, text=True
                ).stdout.strip()
                + ":vhpi_startup_routines_bootstrap"
            )
        elif self.__top_type == "verilog":
            result = subprocess.run(
                ["cocotb-config", "--lib-name-path", "vpi", "riviera"], capture_output=True, text=True
            ).stdout.strip()

        return result

    def __run_cocotb(self, major_ver: int) -> None:
        """Deprecated."""
        env = self.__setup_cocotb_env(major_ver)
        vpi = self.__setup_procedural_interface()
        generics: List[str] = []
        if self.__generics:
            generics = ["-g" + generic for generic in self.__generics]
        if self.__waveform_viewer:
            command = (
                ["vsim", "+access", "+w_nets", "-ieee_nowarn", "-load_vhpi", vpi] + generics + ["work." + self.__top]
            )
        else:
            command = (
                ["vsimsa", "+access", "+w_nets", "-ieee_nowarn", "-load_vhpi", vpi] + generics + ["work." + self.__top]
            )
        cocotb = subprocess.run(command, env=env)
        if cocotb.returncode != 0:
            logger.error("Error during cocotb simulation.")
            sys.exit(1)

    def __run(self) -> None:
        """Deprecated."""
        generics: List[str] = []
        if self.__generics:
            generics = ["-g" + generic for generic in self.__generics]
        if self.__waveform_viewer:
            command = ["vsim", "-ieee_nowarn"] + generics + [self.__top]
        else:
            command = ["vsim", "-batch", "-ieee_nowarn"] + generics + [self.__top]
        cocotb = subprocess.run(command)
        if cocotb.returncode != 0:
            logger.error("Error during cocotb simulation.")
            sys.exit(1)

    def __create_runsim(self) -> None:
        logger.info("Creating simulation script...")
        with open("runsim.tcl", "w") as f:
            f.write("framework.documents.closeall\n")
            f.write("alib work\n")
            if self.__all_vhdl:
                f.write(f"eval acom -work work -2008 -incr {' '.join(self.__vhdl_files)}\n")
            elif self.__all_verilog:
                f.write(f"eval alog -work work -v2k5 -incr {' '.join(self.__verilog_files)}\n")
            elif self.__all_verilog:
                f.write(f"eval alog -work work -sv2k17 -incr {' '.join(self.__sysverilog_files)}\n")
            else:
                for hdl_file in self.__hdl_files:
                    ext = Path(hdl_file).suffix
                    if ext:
                        if ext == ".vhd" or ext == ".vhdl":
                            f.write(f"eval acom -work work -2008 -incr {hdl_file}\n")
                        elif ext == ".v":
                            f.write(f"eval alog -work work -v2k5 -incr {hdl_file}\n")
                        elif ext == ".sv":
                            f.write(f"eval alog -work work -sv2k17 -incr {hdl_file}\n")

            sim_cmd = "asim "

            vpi: str = ""
            if self.__cocotb_module:
                vpi = self.__setup_procedural_interface()
                sim_cmd += f"+access +w_nets -loadvhpi {vpi} "

                if self.__waveform_viewer:
                    sim_cmd += "-interceptcoutput "

            generics: str = ""
            if self.__generics:
                generics = ' '.join(f"-g{generic}" for generic in self.__generics) + " "
                sim_cmd += generics

            sim_cmd += f"-ieee_nowarn work.{self.__top}"
            f.write(sim_cmd + "\n")

            f.write("log -rec *\n")
            f.write(f'set waveformfile "{self.__waveform_file}"\n')
            f.write("if {[file exists $waveformfile]} {\n")
            f.write(f"    system.open -wave {self.__waveform_file}\n")
            f.write("} else {\n")
            f.write("    add wave *\n")
            f.write(f"    write awc {self.__waveform_file}\n")
            f.write("}\n")
            f.write("run -all\n")

            if not self.__waveform_viewer:
                f.write("endsim\n")
                f.write("exit\n")

    def __batch_mode_run(self, major_ver: int) -> None:
        self.__create_runsim()
        if self.__cocotb_module:
            logger.info("Setting up cocotb environment variables...")
            env = self.__setup_cocotb_env(major_ver)
        else:
            env = env = os.environ.copy()

        logger.info("Starting Riviera-PRO...")
        if self.__waveform_viewer:
            command = ["vsim", "-do", "runsim.tcl"]
        else:
            command = ["vsimsa", "-do", "runsim.tcl"]

        sim_batch_mode = subprocess.run(command, env=env)
        if sim_batch_mode.returncode != 0:
            logger.error("Error during Riviera-PRO batch mode simulation.")
            sys.exit(1)
