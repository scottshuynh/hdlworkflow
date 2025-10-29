import subprocess
from importlib.util import find_spec
import logging
import os
from pathlib import Path
import sys
from shutil import which

from hdlworkflow import utils
from hdlworkflow.gtkwave import Gtkwave

logger = logging.getLogger(__name__)
supported_waveform_viewers = ["gtkwave"]


class Nvc:
    """Run simulations using nvc."""

    def __init__(
        self,
        top: str,
        compile_order: str,
        generics: list[str],
        stop_time: str,
        cocotb_module: str,
        waveform_viewer: str,
        waveform_view_file_stem: str,
        path_to_working_directory: str,
        pythonpaths: list[str],
    ):
        logger.info(f"Initialising {type(self).__name__}...")
        path_to_compile_order = compile_order
        if Path(path_to_compile_order).is_absolute():
            if not Path(path_to_compile_order).is_file():
                logger.error(f"Path to compile order ({path_to_compile_order}) does not exist.")
                sys.exit(1)
        else:
            path_to_compile_order = Path(path_to_working_directory / Path(path_to_compile_order)).resolve()
            if not Path(path_to_compile_order).is_file():
                logger.error(f"Path to compile order ({path_to_compile_order}) does not exist.")
                sys.exit(1)

        self.__compile_order: str = path_to_compile_order
        self.__top: str = top
        self.__generics: list[str] = generics
        self.__stop_time: str = stop_time
        self.__cocotb_module: str = cocotb_module
        self.__pwd: str = path_to_working_directory
        self.__pythonpaths: list[str] = utils.relative_to_absolute_paths(pythonpaths, path_to_working_directory)

        self.__waveform_viewer: str = ""
        if waveform_viewer:
            if waveform_viewer in supported_waveform_viewers:
                self.__waveform_viewer: str = waveform_viewer
            else:
                logger.error(
                    f"Unsupported waveform viewer: {waveform_viewer}. Expecting: {' '.join(viewer for viewer in supported_waveform_viewers)}"
                )
                sys.exit(1)

        dependencies_met, missing = self.__check_dependencies()
        if not dependencies_met:
            logger.error(f"Missing dependencies: {' '.join(str(dependency) for dependency in missing)}.")
            logger.error("All dependencies must be found on PATH.")
            sys.exit(1)

        self.__waveform_view_file_stem: str = waveform_view_file_stem
        self.__waveform_save_file: str = ""
        self.__waveform_data: str = ""
        self.__waveform_viewer_obj: object = None
        if self.__waveform_viewer:
            waveform_data_stem: str = self.__top
            if generics:
                waveform_data_stem += "".join(generic for generic in generics)
            if self.__waveform_viewer == "gtkwave":
                self.__waveform_data = waveform_data_stem + ".fst"

                if waveform_view_file_stem:
                    self.__waveform_save_file = waveform_view_file_stem + ".gtkw"
                else:
                    self.__waveform_save_file = waveform_data_stem + ".gtkw"

            self.__waveform_viewer_obj = Gtkwave(self.__waveform_data, self.__waveform_save_file)

        os.makedirs(f"{self.__pwd}/nvc", exist_ok=True)
        os.chdir(f"{self.__pwd}/nvc")

    def __check_dependencies(self) -> tuple[bool, list[str]]:
        logger.info("Checking dependencies...")
        missing: list[str] = []
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
        self.__run()

    def __analyse(self) -> None:
        logger.info("Analysing...")
        command = ["nvc", "-a", "-f", f"{self.__compile_order}"]
        logger.info("    " + " ".join(cmd for cmd in command))
        analyse = subprocess.run(command)
        if analyse.returncode != 0:
            logger.error("Error during analysis.")
            sys.exit(1)

    def __elaborate(self) -> None:
        logger.info("Elaborating...")
        generics = []
        if self.__generics:
            generics = ["-g" + generic for generic in self.__generics]
        command = ["nvc", "-e", "-j"] + generics + [self.__top]
        logger.info("    " + " ".join(cmd for cmd in command))
        elaborate = subprocess.run(command)
        if elaborate.returncode != 0:
            logger.error("Error during elaboration.")
            sys.exit(1)

    def __run(self) -> None:
        logger.info("Running sim...")
        env: dict[str, str] = dict()
        if self.__cocotb_module:
            major, minor, patch = utils.get_cocotb_version()
            libpython_loc = subprocess.run(
                ["cocotb-config", "--libpython"], capture_output=True, text=True
            ).stdout.strip()
            cocotb_vhpi = subprocess.run(
                ["cocotb-config", "--lib-name-path", "vhpi", "nvc"],
                capture_output=True,
                text=True,
            ).stdout.strip()

            env["PYTHONPATH"] = f"{':'.join(str(path) for path in self.__pythonpaths)}"
            env["LIBPYTHON_LOC"] = libpython_loc
            if major >= 2:
                pygpi_python_bin = subprocess.run(
                    ["cocotb-config", "--python-bin"], capture_output=True, text=True
                ).stdout.strip()
                env["PYGPI_PYTHON_BIN"] = pygpi_python_bin
                env["COCOTB_TEST_MODULES"] = self.__cocotb_module
            else:
                env["MODULE"] = self.__cocotb_module

        logger.info(f"Cocotb environment variables: {' '.join(f'{key}={val}' for key, val in env.items())}")
        env = os.environ.copy() | env

        command = [
            "nvc",
            "-r",
            f"{self.__top}",
            "--ieee-warnings=off",
            "--dump-arrays",
        ]
        if self.__cocotb_module:
            command += ["--load", cocotb_vhpi]

        if self.__stop_time:
            command.append(f"--stop-time={self.__stop_time}")

        if self.__waveform_viewer:
            waveform_options = ["--format", "fst", f"--wave={self.__waveform_data}"]
            command += waveform_options

        if self.__waveform_save_file:
            if not self.__waveform_view_file_stem:
                waveform_view_file_option = [f"--gtkw={self.__waveform_save_file}"]
                command += waveform_view_file_option

        logger.info("    " + " ".join(cmd for cmd in command))
        nvc = subprocess.run(command, env=env)

        if self.__waveform_viewer_obj:
            self.__waveform_viewer_obj.run()

        if nvc.returncode != 0:
            logger.error("Error during simulation.")
            sys.exit(1)
        if self.__cocotb_module:
            if not utils.is_cocotb_test_pass("results.xml"):
                logger.error("Test failure during cocotb simulation.")
                sys.exit(1)
