import subprocess
from pathlib import Path
from importlib.metadata import version
from importlib.util import find_spec
import os
import sys
from shutil import which
from typing import List, Tuple

from . import utils
from .gtkwave import Gtkwave


class Nvc:
    """Run simulations using nvc."""

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
            if not utils.is_file(path_to_compile_order):
                print(f"{type(self).__name__}: {path_to_compile_order} does not exist.")
                sys.exit(1)
        else:
            path_to_compile_order = path_to_working_directory + f"/{compile_order}"
            if not utils.is_file(path_to_compile_order):
                print(f"{type(self).__name__}: {path_to_compile_order} does not exist.")
                sys.exit(1)

        self.__compile_order: str = path_to_compile_order
        self.__top: str = top
        self.__generics: List[str] = generics
        self.__cocotb_module: str = cocotb_module
        self.__pwd: str = path_to_working_directory
        self.__pythonpaths: List[str] = utils.prepend_pwd_if_relative(pythonpaths, path_to_working_directory)

        self.__waveform_viewer: str = waveform_viewer

        dependencies_met, missing = self.__check_dependencies()
        if not dependencies_met:
            print(
                f"{type(self).__name__}: Missing dependencies: {" ".join(str(dependency) for dependency in missing)}."
            )
            sys.exit(1)

        if self.__waveform_viewer:
            if self.__waveform_viewer == "gtkwave":
                self.__waveform_file: str = self.__top
                if self.__generics:
                    self.__waveform_file += "".join(generic for generic in self.__generics) + ".fst"
                else:
                    self.__waveform_file += ".fst"

                self.__waveform_viewer_obj = Gtkwave(self.__waveform_file)
            else:
                print(f"{type(self).__name__}: {self.__waveform_viewer} not supported in nvc workflow")
                sys.exit(1)

        os.makedirs("nvc", exist_ok=True)
        os.chdir("nvc")

    def __check_dependencies(self) -> Tuple[bool, List[str]]:
        missing: List[str] = []
        if not which("nvc"):
            missing.append("nvc")
        if self.__cocotb_module:
            if not find_spec("cocotb"):
                missing.append("cocotb")
        if self.__waveform_viewer:
            if not which(self.__waveform_viewer):
                missing.append(self.__waveform_viewer)
        if missing:
            return tuple([False, missing])
        else:
            return tuple([True, None])

    def simulate(self) -> None:
        self.__analyse()
        self.__elaborate()

        if self.__cocotb_module:
            major, minor, patch = utils.get_cocotb_version()
            self.__run_cocotb(major)
        else:
            self.__run()

        if self.__waveform_viewer:
            self.__waveform_viewer_obj.run()

    def __analyse(self) -> None:
        command = ["nvc", "-a", "-f", f"{self.__compile_order}"]
        analyse = subprocess.run(command)
        if analyse.returncode != 0:
            print(f"{type(self).__name__}: Error during analysis.")
            sys.exit(1)

    def __elaborate(self) -> None:
        generics = []
        if self.__generics:
            generics = ["-g" + generic for generic in self.__generics]
        command = ["nvc", "-e", "-j"] + generics + [self.__top]
        elaborate = subprocess.run(command)
        if elaborate.returncode != 0:
            print(f"{type(self).__name__}: Error during elaboration.")
            sys.exit(1)

    def __run(self) -> None:
        command = [
            "nvc",
            "-r",
            f"{self.__top}",
            "--ieee-warnings=off",
            "--dump-arrays",
        ]
        if self.__waveform_viewer:
            waveform_options = ["--format", "fst", f"--wave={self.__waveform_file}"]
            command += waveform_options

        nvc = subprocess.run(command)
        if nvc.returncode != 0:
            print(f"{type(self).__name__}: Error during cocotb simulation.")
            sys.exit(1)

    def __run_cocotb(self, major_ver: int) -> None:
        libpython_loc = subprocess.run(["cocotb-config", "--libpython"], capture_output=True, text=True).stdout.strip()
        cocotb_vhpi = subprocess.run(
            ["cocotb-config", "--lib-name-path", "vhpi", "nvc"], capture_output=True, text=True
        ).stdout.strip()

        env = os.environ.copy()
        env["PYTHONPATH"] = f"{":".join(str(path) for path in self.__pythonpaths)}:" + env.get("PYTHONPATH", "")
        env["LIBPYTHON_LOC"] = libpython_loc
        if major_ver >= 2:
            pygpi_python_bin = subprocess.run(
                ["cocotb-config", "--python-bin"], capture_output=True, text=True
            ).stdout.strip()
            env["PYGPI_PYTHON_BIN"] = pygpi_python_bin
            env["COCOTB_TEST_MODULES"] = self.__cocotb_module
        else:
            env["MODULE"] = self.__cocotb_module

        command = ["nvc", "-r", f"{self.__top}", "--ieee-warnings", "off", "--dump-arrays", "--load", f"{cocotb_vhpi}"]
        if self.__waveform_viewer:
            waveform_options = ["--format", "fst", f"--wave={self.__waveform_file}"]
            command += waveform_options
        cocotb = subprocess.run(command, env=env)
        if cocotb.returncode != 0:
            print(f"{type(self).__name__}: Error during cocotb simulation.")
            sys.exit(1)
