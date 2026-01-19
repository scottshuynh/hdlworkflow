import json, logging, os, subprocess, sys
from importlib.util import find_spec
from pathlib import Path
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
        waveform_view_file: str,
        path_to_working_directory: str,
        pythonpaths: list[str],
        work: str,
    ):
        logger.info(f"Initialising {type(self).__name__}...")

        # Check if file type is supported
        if compile_order:
            if Path(compile_order).suffix == ".txt" or Path(compile_order).suffix == ".json":
                self._compile_order: Path = Path(compile_order)
            else:
                logger.error("Unsupported compile_order file extension. Expecting:, got:")
                sys.exit(1)

        self._top: str = top
        self._generics: list[str] = generics
        self._stop_time: str = stop_time
        self._cocotb_module: str = cocotb_module
        self._pwd: Path = Path(path_to_working_directory)
        self._pythonpaths: list[str] = utils.relative_to_absolute_paths(pythonpaths, path_to_working_directory)
        self._work: list[str] = []
        if work:
            self._work = [f"--work={work}"]

        self._waveform_viewer: str = ""
        if waveform_viewer:
            if waveform_viewer in supported_waveform_viewers:
                self._waveform_viewer: str = waveform_viewer
            else:
                logger.error(
                    f"Unsupported waveform viewer: {waveform_viewer}. Expecting: {' '.join(viewer for viewer in supported_waveform_viewers)}"
                )
                sys.exit(1)

        dependencies_met, missing = self._check_dependencies()
        if not dependencies_met:
            logger.error(f"Missing dependencies: {' '.join(str(dependency) for dependency in missing)}.")
            logger.error("All dependencies must be found on PATH.")
            sys.exit(1)

        self._waveform_view_file: str = waveform_view_file
        self._waveform_save_file: str = ""
        self._waveform_data: str = ""
        self._waveform_viewer_obj: object = None
        if self._waveform_viewer:
            if self._waveform_viewer == "gtkwave":
                waveform_data_stem: str = self._top
                if generics:
                    waveform_data_stem += "".join(generic for generic in generics)
                self._waveform_data = waveform_data_stem + ".fst"

                if waveform_view_file:
                    if Path(waveform_view_file).suffix == ".gtkw":
                        self._waveform_save_file = waveform_view_file
                    else:
                        logger.error(f"Expecting waveform view file with .gtkw extension. Got: {waveform_view_file}")
                        sys.exit(1)
                else:
                    self._waveform_save_file = waveform_data_stem + ".gtkw"

                self._waveform_viewer_obj = Gtkwave(self._waveform_data, self._waveform_save_file)

        os.makedirs(f"{self._pwd / 'nvc'}", exist_ok=True)
        os.chdir(f"{self._pwd / 'nvc'}")

    def _check_dependencies(self) -> tuple[bool, list[str]]:
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
            return tuple([False, missing])
        else:
            return tuple([True, None])

    def simulate(self) -> None:
        self._analyse()
        self._elaborate()
        self._run()

    def _analyse(self) -> None:
        logger.info("Analysing...")

        command = ["nvc", "-L", f"{str(Path.cwd())}"]
        if self._compile_order.suffix == ".txt":
            if self._work:
                command += self._work
            command += ["-a", "-f", f"{str(self._compile_order)}"]
            logger.info("    " + " ".join(cmd for cmd in command))
            analyse = subprocess.run(command)
            if analyse.returncode != 0:
                logger.error("Error during analysis.")
                sys.exit(1)
        elif self._compile_order.suffix == ".json":
            with self._compile_order.open(encoding="utf-8") as f:
                compile_order_dict = json.load(f)
                for entity in compile_order_dict["files"]:
                    if self._top in entity["path"]:
                        if not self._work:
                            self._work = [f"--work={entity['library']}"]
                    command = ["nvc", "-L", f"{str(Path.cwd())}"]
                    if entity["library"]:
                        command += [f"--work={entity['library']}"]

                    entity_path = Path(entity["path"])
                    if not entity_path.is_absolute():
                        entity_path = self._pwd / entity_path
                    command += ["-a", f"{str(entity_path)}"]
                    logger.info("    " + " ".join(cmd for cmd in command))
                    analyse = subprocess.run(command)
                    if analyse.returncode != 0:
                        logger.error("Error during analysis.")
                        sys.exit(1)

    def _elaborate(self) -> None:
        logger.info("Elaborating...")
        generics = []
        if self._generics:
            generics = ["-g" + generic for generic in self._generics]
        command = ["nvc", "-L", f"{str(Path.cwd())}"]
        if self._work:
            command += self._work
        command += ["-e", "-j"] + generics + [self._top]
        logger.info("    " + " ".join(cmd for cmd in command))
        elaborate = subprocess.run(command)
        if elaborate.returncode != 0:
            logger.error("Error during elaboration.")
            sys.exit(1)

    def _run(self) -> None:
        logger.info("Running sim...")
        env: dict[str, str] = dict()
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

            env["PYTHONPATH"] = f"{':'.join(str(path) for path in self._pythonpaths)}"
            env["LIBPYTHON_LOC"] = libpython_loc
            if major >= 2:
                pygpi_python_bin = subprocess.run(
                    ["cocotb-config", "--python-bin"], capture_output=True, text=True
                ).stdout.strip()
                env["PYGPI_PYTHON_BIN"] = pygpi_python_bin
                env["COCOTB_TEST_MODULES"] = self._cocotb_module
            else:
                env["MODULE"] = self._cocotb_module

            logger.info(f"Cocotb environment variables: {' '.join(f'{key}={val}' for key, val in env.items())}")

        env = os.environ.copy() | env

        command = ["nvc", "-L", f"{str(Path.cwd())}"]
        if self._work:
            command += self._work
        command += ["-r", f"{self._top}", "--ieee-warnings=off", "--dump-arrays"]
        if self._cocotb_module:
            command += ["--load", cocotb_vhpi]

        if self._stop_time:
            command.append(f"--stop-time={self._stop_time}")

        if self._waveform_viewer:
            waveform_options = ["--format", "fst", f"--wave={self._waveform_data}"]
            command += waveform_options

        if self._waveform_save_file:
            if not self._waveform_view_file:
                waveform_view_file_option = [f"--gtkw={self._waveform_save_file}"]
                command += waveform_view_file_option

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
