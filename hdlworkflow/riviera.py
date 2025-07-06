import subprocess
from pathlib import Path
from importlib.metadata import version
from importlib.util import find_spec
import os
import sys
from shutil import which
from typing import List, Tuple

from . import utils


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

        self.__compile_order: str = path_to_compile_order
        self.__top: str = top
        self.__generics: List[str] = generics
        self.__cocotb_module: str = cocotb_module
        self.__waveform_viewer: str = waveform_viewer
        self.__waveform_file: str = self.__top + "".join(generic for generic in self.__generics) + ".fst"
        self.__pwd: str = path_to_working_directory
        self.__pythonpaths: List[str] = self.__prepend_pwd_if_relative(pythonpaths, path_to_working_directory)

        dependencies_met, missing = self.__check_dependencies()
        if not dependencies_met:
            print(
                f"{type(self).__name__}: Missing dependencies: {" ".join(str(dependency) for dependency in missing)}."
            )
            sys.exit(1)

        os.makedirs("riviera", exist_ok=True)
        os.chdir("riviera")

    def simulate(self) -> None:
        self.__flatten_compile_order()
        self.__compile()

        if self.__cocotb_module:
            major, minor, patch = utils.get_cocotb_version()
            self.__run_cocotb(major)
        else:
            self.__run()

        if self.__waveform_viewer:
            self.__waveform_viewer_obj.run()

    def __flatten_compile_order(self) -> None:
        self.__vhdl_files: List[str] = []
        self.__verilog_files: List[str] = []
        self.__sverilog_files: List[str] = []
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
                        self.__sverilog_files.append(hdl_file)

    def __compile(self) -> None:
        compiled = False
        if self.__vhdl_files and not self.__verilog_files and not self.__sverilog_files:
            command = ["acom", "-2008", "-incr", " ".join(vhdl_file for vhdl_file in self.__vhdl_files)]
        elif self.__verilog_files and not self.__vhdl_files and not self.__sverilog_files:
            command = ["alog", "-v2k5", "incr", " ".join(verilog_file for verilog_file in self.__verilog_files)]
        elif self.__sverilog_files and not self.__vhdl_files and not self.__verilog_files:
            command = ["alog", "-sv2k17", "incr", " ".join(sverilog_file for sverilog_file in self.__sverilog_files)]
        else:
            compiled = True
            for hdl_file in self.__hdl_files:
                ext = Path(hdl_file).suffix
                if ext:
                    if ext == ".vhd" or ext == ".vhdl":
                        command = ["acom", "-2008", "-incr", hdl_file]
                    elif ext == ".v":
                        command = ["alog", "-v2k5", "incr", hdl_file]
                    elif ext == ".sv":
                        command = ["alog", "-sv2k17", "incr", hdl_file]

                compile = subprocess.run(command)
                if compile.returncode != 0:
                    print(f"{type(self).__name__}: Error during analysis.")
                    sys.exit(1)

        if not compiled:
            compile = subprocess.run(command)
            if compile.returncode != 0:
                print(f"{type(self).__name__}: Error during analysis.")
                sys.exit(1)

    def __run_cocotb(self, major_ver: int) -> None:
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
        env["PYTHONPATH"] = f"{":".join(str(path) for path in self.__pythonpaths)}:" + env.get("PYTHONPATH", "")
        env["LIBPYTHON_LOC"] = libpython_loc
        env["GPI_EXTRA"] = gpi_extra
        if major_ver >= 2:
            pygpi_python_bin = subprocess.run(
                ["cocotb-config", "--python-bin"], capture_output=True, text=True
            ).stdout.strip()
            env["PYGPI_PYTHON_BIN"] = pygpi_python_bin
            env["COCOTB_TEST_MODULES"] = self.__cocotb_module
        else:
            env["MODULE"] = self.__cocotb_module

        generics = ["-g" + generic for generic in self.__generics]
        command = ["asim", "-ieee_nowarn"] + cocotb_vhpi + generics + self.__top
        cocotb = subprocess.run(command, env=env)
        if cocotb.returncode != 0:
            print(f"{type(self).__name__}: Error during cocotb simulation.")
            sys.exit(1)

    def __run(self) -> None:
        pass
