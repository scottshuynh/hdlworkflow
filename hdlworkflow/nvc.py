import subprocess
from pathlib import Path
from importlib.metadata import version
from importlib.util import find_spec
import os
import sys
from shutil import which
from typing import List, Tuple

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
            if not self.__is_file(path_to_compile_order):
                print(f"{path_to_compile_order} does not exist.")
                sys.exit(1)
        else:
            path_to_compile_order = path_to_working_directory + f"/{compile_order}"
            if not self.__is_file(path_to_compile_order):
                print(f"{path_to_compile_order} does not exist.")
                sys.exit(1)

        self.__compile_order: str = path_to_compile_order
        self.__top: str = top
        self.__generics: List[str] = generics
        self.__cocotb_module: str = cocotb_module
        self.__waveform_viewer: str = waveform_viewer
        self.__waveform_file: str = self.__top + "".join(generic for generic in self.__generics) + ".fst"
        self.__pwd: str = path_to_working_directory
        self.__pythonpaths: List[str] = pythonpaths

        dependencies_met, missing = self.__check_dependencies()
        if not dependencies_met:
            print(f"Missing dependencies: {" ".join(str(dependency) for dependency in missing)}.")
            sys.exit(1)

        if self.__waveform_viewer == "gtkwave":
            self.__waveform_viewer_obj = Gtkwave(self.__waveform_file)

        os.makedirs("nvc", exist_ok=True)
        os.chdir("nvc")

    def __is_file(self, file: str) -> bool:
        filepath = Path(file)
        return filepath.is_file()

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
            major, minor, patch = self.__get_cocotb_version()
            self.__run_cocotb(major)
        else:
            self.__run()

        if self.__waveform_viewer:
            self.__waveform_viewer_obj.run()

    def __analyse(self) -> None:
        analyse = subprocess.run(
            ["nvc", "-a", "-f", f"{self.__compile_order}"],
            capture_output=True,
            text=True,
        )
        if analyse.returncode != 0:
            print("Error during analysis.")
            sys.exit(1)

    def __elaborate(self) -> None:
        generics = ["-g" + generic for generic in self.__generics]
        command = ["nvc", "-e", "-j"] + generics + [self.__top]
        elaborate = subprocess.run(command)
        if elaborate.returncode != 0:
            print("Error during elaboration.")
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
            waveform_options = [
                "--format=fst",
                f"--wave={self.__top + "".join(generic for generic in self.__generics)}",
            ]
            command += waveform_options
            nvc = subprocess.run(command)
        if nvc.returncode != 0:
            print("Error during cocotb simulation.")
            sys.exit(1)

    def __get_semantic_version(self, ver: str) -> Tuple[int, int, int]:
        v = ver.split(".")
        if len(v) < 3:
            print(f"Expecting MAJOR.MINOR.PATCH. Got: {".".join(str(num) for num in v)}")
            sys.exit(2)
        return tuple([int(num) for num in v[0:3]])

    def __get_cocotb_version(self) -> Tuple[int, int, int]:
        return self.__get_semantic_version(version("cocotb"))

    def __run_cocotb(self, major_ver: int) -> None:
        libpython_loc = subprocess.run(["cocotb-config", "--libpython"], capture_output=True, text=True).stdout.strip()
        cocotb_vhpi = subprocess.run(
            ["cocotb-config", "--lib-name-path", "vhpi", "nvc"], capture_output=True, text=True
        ).stdout.strip()

        env = os.environ.copy()
        env["PYTHONPATH"] = f"{":".join(str(path) for path in self.__pythonpaths)}:" + env.get("PYTHONPATH", "")
        env["LIBPYTHON_LOC"] = libpython_loc
        if major_ver >= 2:
            env["COCOTB_TEST_MODULES"] = self.__cocotb_module
        else:
            env["MODULE"] = self.__cocotb_module

        command = ["nvc", "-r", f"{self.__top}", "--ieee-warnings", "off", "--dump-arrays", "--load", f"{cocotb_vhpi}"]
        if self.__waveform_viewer:
            waveform_options = ["--format", "fst", f"--wave={self.__waveform_file}"]
            command += waveform_options
        cocotb = subprocess.run(command, env=env)
        if cocotb.returncode != 0:
            print("Error during cocotb simulation.")
            sys.exit(1)
