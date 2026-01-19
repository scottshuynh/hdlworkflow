import json, logging, os, subprocess, sys
from pathlib import Path
from shutil import which

logger = logging.getLogger(__name__)


class Vivado:
    """Run simulations or synthesis using Vivado."""

    def __init__(
        self,
        top: str,
        compile_order: str,
        work: str,
        generics: list[str],
        stop_time: str,
        path_to_working_directory: str,
        part_number: str,
        board_part: str,
        gui: bool,
        waveform_view_file: str,
        synth: bool,
        impl: bool,
        bitstream: bool,
        ooc: bool,
        clk_period_constraints: list[str],
    ):
        logger.info(f"Initialising {type(self).__name__}...")

        self._top: str = top
        self._compile_order: Path = Path(compile_order)
        self._work: str = work
        self._pwd: str = path_to_working_directory
        self._generics: list[str] = generics
        self._stop_time: str = stop_time
        self._part_number: str = part_number
        self._board_part: str = board_part
        self._gui: bool = gui
        self._waveform_view_file: str = waveform_view_file
        self._synth: bool = synth
        self._impl: bool = impl
        self._bitstream: bool = bitstream
        self._ooc: bool = ooc
        self._clk_period_constraints: list[str] = clk_period_constraints

        self._waveform_file: str = ""
        if gui:
            if waveform_view_file:
                if Path(waveform_view_file).suffix == ".wcfg":
                    self._waveform_file = waveform_view_file
                else:
                    logger.error(f"Expecting waveform view file with .wcfg extension. Got: {waveform_view_file}")
                    sys.exit(1)
            else:
                self._waveform_file = self._top
                if generics:
                    self._waveform_file += "".join(generic for generic in self._generics) + ".wcfg"
                else:
                    self._waveform_file += ".wcfg"

        if not self._check_dependencies():
            logger.error("Missing dependencies: vivado")
            logger.error("All dependencies must be found on PATH.")
            sys.exit(1)

        os.makedirs(f"{self._pwd}/vivado", exist_ok=True)
        os.chdir(f"{self._pwd}/vivado")

    def _check_dependencies(self) -> bool:
        logger.info("Checking dependencies...")
        if not which("vivado"):
            return False
        return True

    def start(self) -> None:
        self._create_clock_constraint()
        self._generate_setup_viv_prj()
        self._start_vivado()

    def _create_clock_constraint(self):
        if self._clk_period_constraints:
            with open("clock_constraint.xdc", "w") as f:
                for clk_period_constraint in self._clk_period_constraints:
                    clk_port = clk_period_constraint.split("=")[0]
                    clk_period = clk_period_constraint.split("=")[1]
                    try:
                        float(clk_period)
                    except ValueError:
                        logger.error(f"Expecting float or integer for clock period constraint value. Got: {clk_period}")
                        sys.exit(1)

                    f.write(f"create_clock -period {clk_period} -name {clk_port} [get_ports {clk_port}]\n")

    def _generate_setup_viv_prj(self, target: str = "") -> None:
        logger.info("Generating setup script...")
        if not self._part_number:
            part = "xc7a35ticsg324-1L"
        else:
            part = self._part_number

        with open("setup_viv_prj.tcl", "w") as f:
            f.write(f"create_project -part {part} {self._top} -force\n")
            f.write("set obj [current_project]\n")

            if self._board_part:
                f.write(f'set_property -name "board_part" -value "{self._board_part}" -objects $obj\n')

            if self._compile_order.suffix == ".txt":
                f.write(f"set fp [open {str(self._compile_order)}]\n")
                f.write('set lines [split [read -nonewline $fp] "\\n"]\n')
                f.write("close $fp\n")
                f.write("add_files $lines\n")
            elif self._compile_order.suffix == ".json":
                with self._compile_order.open(encoding="utf-8") as f:
                    compile_order_dict = json.load(f)
                    for entity in compile_order_dict["files"]:
                        if self._top in entity["path"]:
                            if not self._work:
                                self._work = [f"{entity['library'].lower()}"]
                        f.write(f"add_files {entity['path']}\n")
                        if entity["type"].lower() == "vhdl":
                            f.write(f"set_property library {entity['library'].lower()} [get_files {entity['path']}]\n")

            if self._clk_period_constraints:
                f.write("add_files clock_constraint.xdc\n")

            if self._work:
                f.write(f"set_property default_lib {self._work} [current_project]\n")

            f.write(f"set_property top {self._top} [current_fileset]\n")
            f.write(f"set_property top {self._top} [get_filesets sim_1]\n")
            f.write("set_property file_type {VHDL 2008} [get_files *.vhd]\n")

            if self._generics:
                f.write("set_property -name {steps.synth_design.args.more options} -value {")
                if self._ooc:
                    f.write("-mode out_of_context ")
                f.write(
                    f"{'-generic ' + ' -generic '.join(generic for generic in self._generics)}}} -objects [get_runs synth_1]\n"
                )
                f.write(
                    f"set_property -name {{xsim.elaborate.xelab.more_options}} -value {{{'-generic_top ' + ' -generic_top '.join(generic for generic in self._generics)}}} -objects [get_filesets sim_1]\n"
                )
            else:
                if self._ooc:
                    f.write(
                        "set_property -name {steps.synth_design.args.more options} -value {-mode out_of_context} -objects [get_runs synth_1]\n"
                    )

            f.write("set_property -name {xsim.simulate.runtime} -value 0 -objects [get_filesets sim_1]\n")

            if self._gui:
                f.write("start_gui\n")
            if self._synth | self._impl | self._bitstream:
                f.write("reset_run synth_1\n")
                if not self._gui:
                    f.write(f"launch_runs synth_1 -jobs {min(os.cpu_count() // 2, 8)}\n")
                    f.write("wait_on_run synth_1\n")
                    f.write('if {[get_property PROGRESS [get_runs synth_1]] != "100%"} {\n')
                    f.write('    error "ERROR: Synthesis failed."\n')
                    f.write("}\n")

                    if self._impl | self._bitstream:
                        f.write(f"launch_runs impl_1 -jobs {min(os.cpu_count() // 2, 8)}\n")
                        f.write("wait_on_run impl_1\n")
                        f.write('if {[get_property PROGRESS [get_runs impl_1]] != "100%"} {\n')
                        f.write('    error "ERROR: Implementation failed."\n')
                        f.write("}\n")

                        f.write("if {[get_property STATS.WNS [get_runs impl_1]] < 0} {\n")
                        f.write('    error "ERROR: Timing failed."\n')
                        f.write("}\n")
                    if self._bitstream:
                        f.write("open_run impl_1\n")
                        f.write(f"write_bitstream -force {self._pwd}/{self._top}.bit")
                else:
                    if self._bitstream:
                        f.write(f"launch_runs impl_1 -to_step write_bitstream -jobs {min(os.cpu_count() // 2, 8)}\n")
                    elif self._impl:
                        f.write(f"launch_runs impl_1 -jobs {min(os.cpu_count() // 2, 8)}\n")
                    elif self._synth:
                        f.write(f"launch_runs synth_1 -jobs {min(os.cpu_count() // 2, 8)}\n")
            else:
                if self._gui:
                    if self._waveform_view_file:
                        f.write(f"add_files -fileset sim_1 -norecurse {self._waveform_file}\n")
                        f.write(f"set_property xsim.view {self._waveform_file} [get_filesets sim_1]\n")

                f.write("launch_simulation\n")
                if self._gui:
                    if not self._waveform_view_file:
                        wave_filename = str(Path.cwd() / self._waveform_file)
                        f.write("foreach wave [get_waves *] {\n")
                        f.write("    remove_wave $wave\n")
                        f.write("}\n")
                        f.write("foreach hier [get_scopes -r /*] {\n")
                        f.write("    set objs [get_objects $hier/*]\n")
                        f.write("    set num_objs [llength $objs]\n")
                        f.write("    if {$num_objs > 0} {\n")
                        f.write("        add_wave_divider $hier\n")
                        f.write("        if {[catch {add_wave $hier}]} {\n")
                        f.write("            remove_wave $hier\n")
                        f.write("            continue\n")
                        f.write("        }\n")
                        f.write("    }\n")
                        f.write("}\n")
                        f.write(f"save_wave_config {{{wave_filename}}}\n")
                        f.write(f"add_files -fileset sim_1 -norecurse {wave_filename}\n")
                        f.write(f"set_property xsim.view {wave_filename} [get_filesets sim_1]\n")

                if self._stop_time:
                    f.write(f"run {self._stop_time}\n")
                else:
                    f.write("run -all\n")

    def _start_vivado(self) -> None:
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
