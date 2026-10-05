import logging
import os
import subprocess
import sys
from importlib.util import find_spec
from pathlib import Path
from shutil import which

from . import utils
from .gtkwave import Gtkwave
from .surfer import Surfer

logger = logging.getLogger(__name__)
supported_waveform_viewers = ["gtkwave", "surfer"]


class Nvc:
    """Run simulations using nvc."""

    def __init__(
        self,
        top: str,
        compile_order: list[dict],
        generics: list[str],
        stop_time: str,
        cocotb_module: str,
        analyse_args: list[str],
        elaborate_args: list[str],
        run_args: list[str],
        extra_args: list[str],
        plusargs: list[str],
        waveform_viewer: str,
        waveform_view_file: Path | None,
        waveform_dump_file: Path | None,
        path_to_working_directory: Path,
        pythonpaths: list[str],
        work: str,
    ):
        logger.info(f"Initialising {type(self).__name__}...")

        self._compile_order = compile_order
        self._top = top
        self._generics = generics
        self._stop_time = stop_time
        self._cocotb_module = cocotb_module
        self._analyse_args = analyse_args
        self._elaborate_args = elaborate_args
        self._run_args = run_args
        self._extra_args = extra_args
        self._plusargs = plusargs
        self._waveform_viewer = waveform_viewer
        self._waveform_dump_file = waveform_dump_file
        self._waveform_view_file = waveform_view_file
        self._pwd = path_to_working_directory
        self._pythonpaths = utils.relative_to_absolute_paths(pythonpaths, path_to_working_directory)
        self._work = work
        self._valid_file_suffix = [".vhd", ".vhdl", ".v", ".sv"]

        self._waveform_viewer_obj = None
        if self._waveform_viewer:
            self._initialise_waveform_variables()

        dependencies_met, missing = self._check_dependencies()
        if not dependencies_met:
            assert missing
            logger.error(f"Missing dependencies: {' '.join(str(dependency) for dependency in missing)}.")
            logger.error("All dependencies must be found on PATH.")
            sys.exit(1)

        os.makedirs(f"{self._pwd / 'nvc'}", exist_ok=True)
        os.chdir(f"{self._pwd / 'nvc'}")

    def _initialise_waveform_variables(self) -> None:
        """Initialises view/dump files and waveform object"""
        if self._waveform_viewer not in supported_waveform_viewers:
            logger.error(
                f"Unsupported waveform viewer: {self._waveform_viewer}. Expecting: {' '.join(viewer for viewer in supported_waveform_viewers)}"
            )
            sys.exit(1)

        if self._waveform_dump_file:
            if self._waveform_dump_file.suffix != ".fst":
                logger.error(f"Expecting waveform dump file with .fst extension. Got: {self._waveform_dump_file}")
                sys.exit(1)
        if self._waveform_viewer == "gtkwave":
            if self._waveform_view_file:
                if self._waveform_view_file.suffix != ".gtkw":
                    logger.error(f"Expecting waveform view file with .gtkw extension. Got: {self._waveform_view_file}")
                    sys.exit(1)
        elif self._waveform_viewer == "surfer":
            if self._waveform_view_file:
                if self._waveform_view_file.suffix != ".ron":
                    logger.error(f"Expecting waveform view file with .ron extension. Got: {self._waveform_view_file}")
                    sys.exit(1)

        waveform_stem = ""
        if not self._waveform_view_file or not self._waveform_dump_file:
            waveform_stem: str = self._top
            if self._generics:
                waveform_stem += "".join(generic for generic in self._generics)

        waveform_stem = utils.truncate_filestem(utils.sanitise_filename(waveform_stem), "")
        if not self._waveform_dump_file:
            self._waveform_dump_file = utils.relative_to_absolute_path(waveform_stem + ".fst", self._pwd / "nvc")

        if self._waveform_viewer == "gtkwave":
            if not self._waveform_view_file:
                self._waveform_view_file = utils.relative_to_absolute_path(waveform_stem + ".gtkw", self._pwd / "nvc")
            self._waveform_viewer_obj = Gtkwave(self._waveform_dump_file, self._waveform_view_file)

        elif self._waveform_viewer == "surfer":
            overwrite = False
            if self._waveform_view_file:
                if not self._waveform_view_file.is_file():
                    overwrite = True

            elif not self._waveform_view_file:
                self._waveform_view_file = utils.relative_to_absolute_path(waveform_stem + ".ron", self._pwd / "nvc")
                overwrite = True

            self._waveform_viewer_obj = Surfer(self._top, self._waveform_dump_file, self._waveform_view_file, overwrite)

    def _check_dependencies(self) -> tuple[bool, list[str] | None]:
        logger.info("Checking dependencies...")
        missing: list[str] = []
        if not which("nvc"):
            missing.append("nvc")
        if self._cocotb_module:
            if not find_spec("cocotb"):
                missing.append("cocotb")
        if self._waveform_viewer:
            if not which(self._waveform_viewer):
                missing.append(self._waveform_viewer)
        if missing:
            return False, missing
        else:
            return True, None

    def simulate(self) -> None:
        self._analyse()
        self._elaborate()
        self._run()

    def _analyse(self) -> None:
        """Constructs then runs the nvc analyse command.
        - Explicit library to compile design into
        - Any other extra args
        """
        logger.info("Analysing...")

        for hdl in self._compile_order:
            command = ["nvc", "-L", f"{str(Path.cwd())}"]
            if self._extra_args:
                for arg in self._extra_args:
                    command += arg.split(" ")

            hdl_path = Path(hdl.get("path", ""))
            hdl_lib = hdl.get("library", self._work)

            if hdl_lib:
                command += [f"--work={hdl_lib}"]
            if hdl_path.suffix in self._valid_file_suffix:
                command += ["-a"]
                if self._analyse_args:
                    for arg in self._analyse_args:
                        command += arg.split(" ")
                command += [f"{str(hdl_path)}"]

                logger.info("    " + " ".join(cmd for cmd in command))
                analyse = subprocess.run(command)
                if analyse.returncode != 0:
                    logger.error("Error during analysis.")
                    sys.exit(1)
            else:
                logger.warning(f"Skipping non-HDL file: {hdl_path}")

    def _elaborate(self) -> None:
        logger.info("Elaborating...")

        command = ["nvc", "-L", f"{str(Path.cwd())}"]

        if self._extra_args:
            for arg in self._extra_args:
                command += arg.split(" ")

        generics = []
        if self._generics:
            generics = ["-g" + generic for generic in self._generics]

        if self._work:
            command += [f"--work={self._work}"]

        command += ["-e", "-j"] + generics

        if self._elaborate_args:
            for arg in self._elaborate_args:
                command += arg.split(" ")

        command += [self._top]

        logger.info("    " + " ".join(cmd for cmd in command))
        elaborate = subprocess.run(command)
        if elaborate.returncode != 0:
            logger.error("Error during elaboration.")
            sys.exit(1)

    def _run(self) -> None:
        logger.info("Running sim...")
        env: dict[str, str] = dict()
        command = ["nvc", "-L", f"{str(Path.cwd())}"]

        if self._cocotb_module:
            major, minor, patch = utils.get_cocotb_version()
            libpython_loc = subprocess.run(
                ["cocotb-config", "--libpython"], capture_output=True, text=True
            ).stdout.strip()
            cocotb_vhpi = subprocess.run(
                ["cocotb-config", "--lib-name-path", "vhpi", "nvc"],
                capture_output=True,
                text=True,
            ).stdout.strip()

            pathsep = os.pathsep
            env["PYTHONPATH"] = f"{pathsep.join(str(path) for path in self._pythonpaths)}"
            env["LIBPYTHON_LOC"] = libpython_loc
            if major >= 2:
                pygpi_python_bin = subprocess.run(
                    ["cocotb-config", "--python-bin"], capture_output=True, text=True
                ).stdout.strip()
                env["PYGPI_PYTHON_BIN"] = pygpi_python_bin
                env["COCOTB_TEST_MODULES"] = self._cocotb_module
            else:
                env["MODULE"] = self._cocotb_module

            command += ["--load", cocotb_vhpi]
            logger.info(f"Cocotb environment variables: {' '.join(f'{key}={val}' for key, val in env.items())}")

        env = os.environ.copy() | env

        if self._extra_args:
            for arg in self._extra_args:
                command += arg.split(" ")

        if self._work:
            command += [f"--work={self._work}"]

        command += ["-r"]

        if self._run_args:
            for arg in self._run_args:
                command += arg.split(" ")

        command += [f"{self._top}"]

        for plusarg in self._plusargs:
            command += [f"+{plusarg}"]

        if self._stop_time:
            command.append(f"--stop-time={self._stop_time}")

        if self._waveform_viewer:
            waveform_options = ["--dump-arrays", "--format", "fst", f"--wave={self._waveform_dump_file}"]
            command += waveform_options

            if self._waveform_viewer == "gtkwave":
                if not Path(self._waveform_view_file).is_file():
                    command.append(f"--gtkw={self._waveform_view_file}")

        if self._cocotb_module:
            results_xml = Path.cwd() / "results.xml"
            results_xml.unlink(missing_ok=True)

        logger.info("    " + " ".join(cmd for cmd in command))
        nvc = subprocess.run(command, env=env)

        if self._waveform_viewer_obj:
            self._waveform_viewer_obj.run()

        if nvc.returncode != 0:
            logger.error("Error during simulation.")
            sys.exit(1)
        if self._cocotb_module:
            if not utils.is_cocotb_test_pass("results.xml"):
                logger.error("Test failure during cocotb simulation.")
                sys.exit(1)
