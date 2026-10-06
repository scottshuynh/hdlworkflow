import logging
import os
import subprocess
import sys
from importlib.util import find_spec
from pathlib import Path
from shutil import which

from . import utils

logger = logging.getLogger(__name__)


class Riviera:
    """Run simulations using Riviera-PRO."""

    def __init__(
        self,
        top: str,
        compile_order: list[dict],
        work: str,
        generics: list[str],
        search_libraries: list[str],
        stop_time: str,
        cocotb_module: str,
        analyse_args: list[str],
        elaborate_args: list[str],
        run_args: list[str],
        extra_args: list[str],
        plusargs: list[str],
        gui: bool,
        waveform_view_file: Path | None,
        waveform_dump_file: Path | None,
        path_to_working_directory: Path,
        pythonpaths: list[str],
        path_to_libstdcpp: str,
        path_to_glbl: str,
    ):
        logger.info(f"Initialising {type(self).__name__}...")

        self._hdl_files = compile_order
        self._top = top
        self._top_type = self._get_top_type()
        self._search_libraries = search_libraries

        self._libraries = list()
        self._work = "work"
        if work:
            self._work = work
            self._libraries.append(work)

        self._generics = generics
        self._stop_time = stop_time
        self._cocotb_module = cocotb_module
        self._analyse_args = analyse_args
        self._elaborate_args = elaborate_args
        self._run_args = run_args
        self._extra_args = extra_args
        self._plusargs = plusargs
        self._pwd = Path(path_to_working_directory)
        self._pythonpaths = utils.relative_to_absolute_paths(pythonpaths, path_to_working_directory)
        self._path_to_glbl = path_to_glbl
        self._path_to_libstdcpp = ""

        if path_to_libstdcpp:
            if Path(path_to_libstdcpp).is_absolute():
                self._path_to_libstdcpp = path_to_libstdcpp
            else:
                self._path_to_libstdcpp = str((Path(path_to_working_directory) / path_to_libstdcpp).resolve())

        self._gui = gui
        self._waveform_view_file = waveform_view_file
        self._waveform_dump_file = waveform_dump_file
        self._default_asdb = True

        if self._gui:
            self._initialise_waveform_variables()

        dependencies_met, missing = self._check_dependencies()
        if not dependencies_met:
            logger.error(f"Missing dependencies: {' '.join(str(dependency) for dependency in missing)}.")
            logger.error("All dependencies must be found on PATH.")
            sys.exit(1)

        self.cocotb_semver = None
        if self._cocotb_module:
            self.cocotb_semver = utils.get_cocotb_version()

        os.makedirs(f"{self._pwd / 'riviera'}", exist_ok=True)
        os.chdir(f"{self._pwd / 'riviera'}")

    def _initialise_waveform_variables(self) -> None:
        """Initialises view/dump files"""
        if self._waveform_view_file:
            if not Path(self._waveform_view_file).suffix == ".awc":
                logger.error(f"Expecting waveform view file with .wcfg extension. Got: {self._waveform_view_file}")
                sys.exit(1)

        if self._waveform_dump_file:
            self._default_asdb = False
            if not Path(self._waveform_dump_file).suffix == ".asdb":
                logger.error(f"Expecting waveform dump file with .wdb extension. Got: {self._waveform_dump_file}")
                sys.exit(1)

        waveform_stem = ""
        if not self._waveform_view_file or not self._waveform_dump_file:
            waveform_stem: str = self._top
            if self._generics:
                waveform_stem += "".join(generic for generic in self._generics)

        waveform_stem = utils.truncate_filestem(utils.sanitise_filename(waveform_stem), "")
        if self._waveform_dump_file:
            self._waveform_dump_file = utils.relative_to_absolute_path(self._waveform_dump_file, self._pwd)

        if not self._waveform_view_file:
            self._waveform_view_file = utils.relative_to_absolute_path(waveform_stem + ".awc", self._pwd / "riviera")
        else:
            self._waveform_view_file = utils.relative_to_absolute_path(self._waveform_view_file, self._pwd)

    def _check_dependencies(self) -> tuple[bool, list[str] | None]:
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
            return False, missing
        else:
            return True, None

    def _get_top_type(self) -> str:
        top_type = ""
        for hdl in self._hdl_files:
            hdl_path = Path(hdl.get("path", ""))
            if self._top in str(hdl_path):
                if hdl_path.suffix == ".vhd" or hdl_path.suffix == ".vhdl":
                    top_type = "vhdl"
                elif hdl_path.suffix == ".v" or hdl_path.suffix == ".sv":
                    top_type = "verilog"
                break

        return top_type

    def simulate(self) -> None:
        self._create_runsim()
        self._batch_mode_run()

    def _setup_cocotb_env(self) -> dict[str, str]:
        assert self.cocotb_semver
        libpython_loc = subprocess.run(["cocotb-config", "--libpython"], capture_output=True, text=True).stdout.strip()
        gpi_extra = self._setup_procedural_interface(True)
        env: dict[str, str] = dict()
        pathsep = os.pathsep
        env["PYTHONPATH"] = f"{pathsep.join(str(path) for path in self._pythonpaths)}"
        env["LIBPYTHON_LOC"] = libpython_loc
        env["GPI_EXTRA"] = gpi_extra

        if not self._gui:
            env["COCOTB_ANSI_OUTPUT"] = "1"
        if self.cocotb_semver[0] >= 2:
            pygpi_python_bin = subprocess.run(
                ["cocotb-config", "--python-bin"], capture_output=True, text=True
            ).stdout.strip()
            if self.cocotb_semver[1] == 1:
                pygpi_entry_point = subprocess.run(
                    ["cocotb-config", "--pygpi-entry-point"], capture_output=True, text=True
                ).stdout.strip()
                env["GPI_USERS"] = libpython_loc + ";" + pygpi_entry_point
                del env["LIBPYTHON_LOC"]
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
            assert self.cocotb_semver
            if self._top_type == "vhdl":
                if self.cocotb_semver[0] == 2 and self.cocotb_semver[1] == 1:
                    result = subprocess.run(
                        ["cocotb-config", "--lib-entry", "vhpi", "riviera"],
                        capture_output=True,
                        text=True,
                    ).stdout.strip()
                else:
                    result = (
                        subprocess.run(
                            ["cocotb-config", "--lib-name-path", "vhpi", "riviera"],
                            capture_output=True,
                            text=True,
                        ).stdout.strip()
                        + ":vhpi_startup_routines_bootstrap"
                    )
            elif self._top_type == "verilog":
                if self.cocotb_semver[0] == 2 and self.cocotb_semver[1] == 1:
                    result = subprocess.run(
                        ["cocotb-config", "--lib-entry", "vpi", "riviera"],
                        capture_output=True,
                        text=True,
                    ).stdout.strip()
                else:
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
            tcl_lines.append(
                f"eval alog -work {self._work} -incr "
                + " ".join(arg for arg in self._analyse_args)
                + f" {' '.join(arg for arg in self._extra_args)} {self._path_to_glbl}",
            )

        tcl_lines.append("set compile_returncode [catch {")
        for hdl_file in self._hdl_files:
            library = hdl_file.get("library", self._work).lower()
            if library not in self._libraries:
                self._libraries.append(library)
                tcl_lines.append(f"alib {library}")

            hdl_filepath = Path(hdl_file["path"])

            if (
                hdl_file.get("type", "none").lower() == "vhdl"
                or hdl_filepath.suffix == ".vhd"
                or hdl_filepath.suffix == ".vhdl"
            ):
                tcl_lines.append(
                    f"    eval acom -work {library} -2008 -incr "
                    + " ".join(arg for arg in self._analyse_args)
                    + f"{' '.join(arg for arg in self._extra_args)} {hdl_file['path']}",
                )
            elif (
                hdl_file.get("type", "none").lower() == "verilog"
                or hdl_filepath.suffix == ".v"
                or hdl_filepath.suffix == ".sv"
            ):
                tcl_lines.append(
                    f"    eval alog -work {library} -incr "
                    + " ".join(arg for arg in self._analyse_args)
                    + f" {' '.join(arg for arg in self._extra_args)} {hdl_file['path']}",
                )
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
            sim_cmd += f"+{plusarg} "

        generics: str = ""
        if self._generics:
            generics = " ".join(f"-g{generic}" for generic in self._generics) + " "
            sim_cmd += generics

        if self._search_libraries:
            sim_cmd += "-L " + " -L ".join(self._search_libraries) + " "

        sim_cmd += "-ieee_nowarn "
        if self._elaborate_args:
            sim_cmd += f"{' '.join(arg for arg in self._elaborate_args)} "

        if self._gui:
            if not self._default_asdb:
                sim_cmd += f"-asdb {self._waveform_dump_file} "

        sim_cmd += f"{' '.join(arg for arg in self._extra_args)} {self._work}.{self._top} "

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
                if self._waveform_view_file.is_file():
                    tcl_lines.append(f"system.open -wave {str(self._waveform_view_file)}")
                else:
                    tcl_lines.extend(
                        [
                            "add wave -expand -vgroup [env] *",
                            "set instances [find hierarchy -list -component -rec *]",
                            "foreach inst $instances {",
                            "    add wave -expand -vgroup $inst $inst/*",
                            "}",
                            f"write awc {str(self._waveform_view_file)}",
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

    def _batch_mode_run(self) -> None:
        if self._cocotb_module:
            logger.info("Setting up cocotb environment variables...")
            env = self._setup_cocotb_env()
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

        if self._run_args:
            for arg in self._run_args:
                command += arg.split(" ")

        logger.info("    " + " ".join(cmd for cmd in command))
        sim_batch_mode = subprocess.run(command, env=env)
        if sim_batch_mode.returncode != 0:
            logger.error("Error during Riviera-PRO batch mode simulation.")
            sys.exit(1)
        if self._cocotb_module:
            if not utils.is_cocotb_test_pass("results.xml"):
                logger.error("Test failure during cocotb simulation.")
                sys.exit(1)
