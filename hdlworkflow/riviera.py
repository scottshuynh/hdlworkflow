import json, logging, os, subprocess, sys
from importlib.util import find_spec
from pathlib import Path
from shutil import which

from hdlworkflow import utils

logger = logging.getLogger(__name__)


class Riviera:
    """Run simulations using Riviera-PRO."""

    def __init__(
        self,
        top: str,
        compile_order: str,
        work: str,
        generics: list[str],
        search_libraries: list[str],
        stop_time: str,
        cocotb_module: str,
        plusargs: list[str],
        gui: bool,
        waveform_view_file: str,
        path_to_working_directory: str,
        pythonpaths: list[str],
        path_to_libstdcpp: str,
        path_to_glbl: str,
    ):
        logger.info(f"Initialising {type(self).__name__}...")

        self._top: str = top
        # Check if file type is supported
        if compile_order:
            if Path(compile_order).suffix == ".txt" or Path(compile_order).suffix == ".json":
                self._compile_order: Path = Path(compile_order)
            else:
                logger.error("Unsupported compile_order file extension. Expecting:, got:")
                sys.exit(1)

        self._search_libraries: list[str] = search_libraries

        self._libraries: set[str] = set()
        if work:
            self._work: str = work.lower()
            self._libraries.add(work.lower())
        else:
            self._work = "work"

        self._generics: list[str] = generics
        self._stop_time: str = stop_time
        self._cocotb_module: str = cocotb_module
        self._plusargs: list[str] = plusargs
        self._pwd: Path = Path(path_to_working_directory)
        self._pythonpaths: list[str] = utils.relative_to_absolute_paths(pythonpaths, path_to_working_directory)
        self._path_to_glbl: str = path_to_glbl
        self._path_to_libstdcpp: str = ""
        if path_to_libstdcpp:
            if Path(path_to_libstdcpp).is_absolute():
                self._path_to_libstdcpp = path_to_libstdcpp
            else:
                self._path_to_libstdcpp = str((Path(path_to_working_directory) / path_to_libstdcpp).resolve())

        self._gui: bool = gui
        self._waveform_view_file: str = waveform_view_file
        self._waveform_file: str = ""
        if gui:
            if waveform_view_file:
                if Path(waveform_view_file).suffix == ".awc":
                    self._waveform_file = waveform_view_file
                else:
                    logger.error(f"Expecting waveform view file with .awc extension. Got: {waveform_view_file}")
                    sys.exit(1)
            else:
                self._waveform_file = self._top
                if generics:
                    self._waveform_file += "".join(generic for generic in self._generics) + ".awc"
                else:
                    self._waveform_file += ".awc"

        dependencies_met, missing = self._check_dependencies()
        if not dependencies_met:
            logger.error(f"Missing dependencies: {' '.join(str(dependency) for dependency in missing)}.")
            logger.error("All dependencies must be found on PATH.")
            sys.exit(1)

        os.makedirs(f"{self._pwd / 'riviera'}", exist_ok=True)
        os.chdir(f"{self._pwd / 'riviera'}")

    def _check_dependencies(self) -> tuple[bool, list[str]]:
        logger.info("Checking dependencies...")
        dependencies = ["vsim", "vsimsa"]
        missing: list[str] = []
        for dependency in dependencies:
            if not which(dependency):
                missing.append(dependency)
        if self._cocotb_module:
            if not find_spec("cocotb"):
                missing.append("cocotb")
        if missing:
            return tuple([False, missing])
        else:
            return tuple([True, None])

    def simulate(self) -> None:
        self._flatten_compile_order()

        major = 0
        if self._cocotb_module:
            major, minor, patch = utils.get_cocotb_version()

        self._batch_mode_run(major)

    def _flatten_compile_order(self) -> None:
        self._hdl_files: list[dict] = []

        if self._compile_order.suffix == ".txt":
            with self._compile_order.open(encoding="utf-8") as f:
                for line in f:
                    hdl_file: Path = Path(line.strip())
                    ext = hdl_file.suffix
                    entity = dict()
                    entity["library"] = self._work
                    if ext:
                        if ext == ".vhd" or ext == ".vhdl":
                            entity["type"] = "vhdl"
                            if self._top in line:
                                self._top_type = "vhdl"
                        elif ext == ".v" or ext == ".sv":
                            entity["type"] = "verilog"
                            if self._top in line:
                                self._top_type = "verilog"
                        else:
                            entity["type"] = "none"

                    if not hdl_file.is_absolute():
                        hdl_file = self._pwd / hdl_file
                    entity["path"] = str(hdl_file)

                    self._hdl_files.append(entity)

        elif self._compile_order.suffix == ".json":
            with self._compile_order.open(encoding="utf-8") as f:
                compile_order_dict = json.load(f)
                self._hdl_files = compile_order_dict["files"]
                for entity in self._hdl_files:
                    library = entity.get("library", "").lower()

                    if self._top in entity["path"].lower():
                        if entity.get("type", ""):
                            self._top_type = entity["type"].lower()
                        else:
                            top_suffix = Path(entity["path"].lower()).suffix
                            if top_suffix == ".vhd" or top_suffix == ".vhdl":
                                self._top_type = "vhdl"
                            elif top_suffix == ".v" or top_suffix == ".sv":
                                self._top_type = "verilog"
                        if self._work == "work" and library:
                            self._work = library
                    if library and library not in self._libraries:
                        self._libraries.add(library)
                    if not Path(entity["path"]).is_absolute():
                        entity["path"] = str(self._pwd / entity["path"])

    def _setup_cocotb_env(self, major_ver: int) -> dict[str, str]:
        libpython_loc = subprocess.run(["cocotb-config", "--libpython"], capture_output=True, text=True).stdout.strip()
        gpi_extra = self._setup_procedural_interface(True)
        env: dict[str, str] = dict()
        pathsep = os.pathsep
        env["PYTHONPATH"] = f"{pathsep.join(str(path) for path in self._pythonpaths)}"
        env["LIBPYTHON_LOC"] = libpython_loc
        env["GPI_EXTRA"] = gpi_extra

        if not self._gui:
            env["COCOTB_ANSI_OUTPUT"] = "1"
        if major_ver >= 2:
            pygpi_python_bin = subprocess.run(
                ["cocotb-config", "--python-bin"], capture_output=True, text=True
            ).stdout.strip()
            env["PYGPI_PYTHON_BIN"] = pygpi_python_bin
            env["COCOTB_TEST_MODULES"] = self._cocotb_module
            env["COCOTB_TOPLEVEL"] = self._top
        else:
            env["MODULE"] = self._cocotb_module
            env["TOPLEVEL"] = self._top

        logger.info(f"Cocotb environment variables: {' '.join(f'{key}={val}' for key, val in env.items())}")
        env = os.environ.copy() | env
        return env

    def _setup_procedural_interface(self, is_gpi_extra: bool = False) -> str:
        result: str = ""
        if is_gpi_extra:
            if self._top_type == "vhdl":
                result = (
                    subprocess.run(
                        ["cocotb-config", "--lib-name-path", "vpi", "riviera"],
                        capture_output=True,
                        text=True,
                    ).stdout.strip()
                    + ":cocotbvpi_entry_point"
                )
            elif self._top_type == "verilog":
                result = (
                    subprocess.run(
                        ["cocotb-config", "--lib-name-path", "vhpi", "riviera"],
                        capture_output=True,
                        text=True,
                    ).stdout.strip()
                    + ":cocotbvhpi_entry_point"
                )
        else:
            if self._top_type == "vhdl":
                result = (
                    subprocess.run(
                        ["cocotb-config", "--lib-name-path", "vhpi", "riviera"],
                        capture_output=True,
                        text=True,
                    ).stdout.strip()
                    + ":vhpi_startup_routines_bootstrap"
                )
            elif self._top_type == "verilog":
                result = subprocess.run(
                    ["cocotb-config", "--lib-name-path", "vpi", "riviera"],
                    capture_output=True,
                    text=True,
                ).stdout.strip()

        return result

    def _create_runsim(self) -> None:
        logger.info("Creating simulation script...")
        tcl_lines = list()
        tcl_lines.append("framework.documents.closeall")
        if self._libraries:
            for library in self._libraries:
                tcl_lines.append(f"alib {library}")
        else:
            tcl_lines.append(f"alib {self._work}")

        if self._path_to_glbl:
            tcl_lines.append(f"eval alog -work {self._work} -incr {self._path_to_glbl}")

        tcl_lines.append("set compile_returncode [catch {")
        for hdl_file in self._hdl_files:
            library = hdl_file.get("library", self._work).lower()
            hdl_filepath = Path(hdl_file["path"])

            if (
                hdl_file.get("type", "none").lower() == "vhdl"
                or hdl_filepath.suffix == ".vhd"
                or hdl_filepath.suffix == ".vhdl"
            ):
                tcl_lines.append(f"    eval acom -work {library} -2008 -incr {hdl_file['path']}")
            elif (
                hdl_file.get("type", "none").lower() == "verilog"
                or hdl_filepath.suffix == ".v"
                or hdl_filepath.suffix == ".sv"
            ):
                tcl_lines.append(f"    eval alog -work {library} -incr {hdl_file['path']}")
            else:
                logger.warning(f"Ignoring file: {hdl_file['path']}")

        tcl_lines.extend(
            [
                "} result]",
                "if {$compile_returncode != 0} {",
                '    puts "Error when compiling HDL"',
                "    quit -code 1",
                "}",
            ]
        )

        sim_cmd = "asim "
        vpi: str = ""
        if self._cocotb_module:
            vpi = self._setup_procedural_interface()
            sim_cmd += f"+access +w_nets "
            if self._top_type == "vhdl":
                sim_cmd += f"-loadvhpi {vpi} "
            elif self._top_type == "verilog":
                sim_cmd += f"-pli {vpi} "

            if self._gui:
                sim_cmd += "-interceptcoutput "

        for plusarg in self._plusargs:
            sim_smd += f"+{plusarg} "

        generics: str = ""
        if self._generics:
            generics = " ".join(f"-g{generic}" for generic in self._generics) + " "
            sim_cmd += generics

        if self._search_libraries:
            sim_cmd += "-L " + " -L ".join(self._search_libraries) + " "

        sim_cmd += f"-ieee_nowarn {self._work}.{self._top} "

        if self._path_to_glbl:
            sim_cmd += f"{self._work}.glbl"

        tcl_lines.extend(
            [
                f"if {{[catch {{{sim_cmd}}} result]}} {{",
                "    puts $result",
                '    puts "Error when running asim"',
                "    quit -code 1",
                "}",
                "log -rec *",
            ]
        )

        if self._gui:
            if self._waveform_view_file:
                tcl_lines.append(f"system.open -wave {self._waveform_file}")
            else:
                tcl_lines.extend(
                    [
                        "add wave -expand -vgroup [env] *",
                        "set instances [find hierarchy -list -component -rec *]",
                        "foreach inst $instances {",
                        "    add wave -expand -vgroup $inst $inst/*",
                        "}",
                        f"write awc {self._waveform_file}",
                    ]
                )

        if self._stop_time:
            tcl_lines.append(f"run {self._stop_time}")
        else:
            tcl_lines.append("run -all")

        if not self._gui:
            tcl_lines.extend(
                [
                    "endsim",
                    "exit",
                ]
            )

        with open("runsim.tcl", "w", encoding="utf-8") as f:
            for tcl_line in tcl_lines:
                f.write(f"{tcl_line}\n")

    def _batch_mode_run(self, cocotb_major_ver: int = 0) -> None:
        self._create_runsim()
        if self._cocotb_module:
            logger.info("Setting up cocotb environment variables...")
            env = self._setup_cocotb_env(cocotb_major_ver)
        else:
            env = env = os.environ.copy()

        if self._path_to_libstdcpp:
            cwd_libstdcpp = Path.cwd() / Path(self._path_to_libstdcpp).name
            if not (cwd_libstdcpp).exists():
                logger.info(f"Creating a symlink to libstdc++: {str(cwd_libstdcpp)}")
                os.symlink(self._path_to_libstdcpp, str(cwd_libstdcpp))

        if self._cocotb_module:
            results_xml = Path.cwd() / "results.xml"
            results_xml.unlink(missing_ok=True)

        logger.info("Starting Riviera-PRO...")
        if self._gui:
            command = ["vsim", "-do", "runsim.tcl"]
        else:
            command = ["vsimsa", "-do", "runsim.tcl"]

        logger.info("    " + " ".join(cmd for cmd in command))
        sim_batch_mode = subprocess.run(command, env=env)
        if sim_batch_mode.returncode != 0:
            logger.error("Error during Riviera-PRO batch mode simulation.")
            sys.exit(1)
        if self._cocotb_module:
            if not utils.is_cocotb_test_pass("results.xml"):
                logger.error("Test failure during cocotb simulation.")
                sys.exit(1)
