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
        self._pwd: Path = Path(path_to_working_directory)
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

        os.makedirs(f"{self._pwd / 'vivado'}", exist_ok=True)
        os.chdir(f"{self._pwd / 'vivado'}")

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
            with open("clock_constraint.xdc", "w", encoding="utf-8") as f:
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

        tcl_lines = list()
        tcl_lines.extend(
            [
                f"create_project -part {part} {self._top} -force",
                "set obj [current_project]",
            ]
        )

        if self._board_part:
            tcl_lines.append(f'set_property -name "board_part" -value "{self._board_part}" -objects $obj')

        if self._compile_order.suffix == ".txt":
            tcl_lines.extend(
                [
                    f"set fp [open {str(self._compile_order)}]",
                    'set lines [split [read -nonewline $fp] "\\n"]',
                    "close $fp",
                    "add_files $lines",
                ]
            )
        elif self._compile_order.suffix == ".json":
            with self._compile_order.open(encoding="utf-8") as jf:
                compile_order_dict = json.load(jf)
                for entity in compile_order_dict["files"]:
                    if self._top in entity["path"]:
                        if not self._work:
                            self._work = f"{entity.get('library', 'work').lower()}"
                    entity_path = Path(entity["path"])
                    if not entity_path.is_absolute():
                        entity_path = self._pwd / entity_path
                    tcl_lines.append(f"add_files {str(entity_path)}")
                    if (
                        entity.get("type", "none").lower() == "vhdl"
                        or entity_path.suffix == ".vhd"
                        or entity_path.suffix == ".vhdl"
                    ):
                        tcl_lines.append(
                            f"set_property library {entity.get('library', self._work).lower()} [get_files {str(entity_path)}]"
                        )

        if self._clk_period_constraints:
            tcl_lines.append("add_files clock_constraint.xdc")

        if self._work:
            tcl_lines.append(f"set_property default_lib {self._work} [current_project]")

        tcl_lines.extend(
            [
                f"set_property top {self._top} [current_fileset]",
                f"set_property top {self._top} [get_filesets sim_1]",
                "set_property file_type {VHDL 2008} [get_files *.vhd]",
            ]
        )

        if self._generics:
            tcl_line: str = "set_property -name {steps.synth_design.args.more options} -value {"
            if self._ooc:
                tcl_line += "-mode out_of_context "
                tcl_line += f"{'-generic ' + ' -generic '.join(generic for generic in self._generics)}}} -objects [get_runs synth_1]"
                tcl_lines.append(tcl_line)

            tcl_lines.append(
                f"set_property -name {{xsim.elaborate.xelab.more_options}} -value {{{'-generic_top ' + ' -generic_top '.join(generic for generic in self._generics)}}} -objects [get_filesets sim_1]"
            )
        else:
            if self._ooc:
                tcl_lines.append(
                    "set_property -name {steps.synth_design.args.more options} -value {-mode out_of_context} -objects [get_runs synth_1]"
                )

        tcl_lines.append("set_property -name {xsim.simulate.runtime} -value 0 -objects [get_filesets sim_1]")

        if self._gui:
            tcl_lines.append("start_gui")
        if self._synth | self._impl | self._bitstream:
            tcl_lines.extend(
                [
                    "set_property steps.synth_design.args.assert true [get_runs synth_1]",
                    "reset_run synth_1",
                ]
            )
            if not self._gui:
                tcl_lines.extend(
                    [
                        f"launch_runs synth_1 -jobs {min(os.cpu_count() // 2, 8)}",
                        "wait_on_run synth_1",
                        'if {[get_property PROGRESS [get_runs synth_1]] != "100%"} {',
                        '    error "ERROR: Synthesis failed."',
                        "}",
                    ]
                )

                if self._impl | self._bitstream:
                    tcl_lines.extend(
                        [
                            f"launch_runs impl_1 -jobs {min(os.cpu_count() // 2, 8)}",
                            "wait_on_run impl_1",
                            'if {[get_property PROGRESS [get_runs impl_1]] != "100%"} {',
                            '    error "ERROR: Implementation failed."',
                            "}",
                            "if {[get_property STATS.WNS [get_runs impl_1]] < 0} {",
                            '    error "ERROR: Timing failed."',
                            "}",
                        ]
                    )
                if self._bitstream:
                    tcl_lines.extend(
                        [
                            "open_run impl_1",
                            f"write_bitstream -force {str(self._pwd / self._top + '.bit')}",
                        ]
                    )
            else:
                if self._bitstream:
                    tcl_lines.append(f"launch_runs impl_1 -to_step write_bitstream -jobs {min(os.cpu_count() // 2, 8)}")
                elif self._impl:
                    tcl_lines.append(f"launch_runs impl_1 -jobs {min(os.cpu_count() // 2, 8)}")
                elif self._synth:
                    tcl_lines.append(f"launch_runs synth_1 -jobs {min(os.cpu_count() // 2, 8)}")
        else:
            if self._gui:
                if self._waveform_view_file:
                    tcl_lines.extend(
                        [
                            f"add_files -fileset sim_1 -norecurse {self._waveform_file}",
                            f"set_property xsim.view {self._waveform_file} [get_filesets sim_1]",
                        ]
                    )

            tcl_lines.append("launch_simulation")
            if self._gui:
                if not self._waveform_view_file:
                    wave_filename = str(Path.cwd() / self._waveform_file)
                    tcl_lines.extend(
                        [
                            "foreach wave [get_waves *] {",
                            "    remove_wave $wave",
                            "}",
                            "foreach hier [get_scopes -r /*] {",
                            "    set objs [get_objects $hier/*]",
                            "    set num_objs [llength $objs]",
                            "    if {$num_objs > 0} {",
                            "        add_wave_divider $hier",
                            "        if {[catch {add_wave $hier}]} {",
                            "            remove_wave $hier",
                            "            continue",
                            "        }",
                            "    }",
                            "}",
                            f"save_wave_config {{{wave_filename}}}",
                            f"add_files -fileset sim_1 -norecurse {wave_filename}",
                            f"set_property xsim.view {wave_filename} [get_filesets sim_1]",
                        ]
                    )

            if self._stop_time:
                tcl_lines.append(f"run {self._stop_time}")
            else:
                tcl_lines.append("run -all")

        with open("setup_viv_prj.tcl", "w", encoding="utf-8") as f:
            for tcl_line in tcl_lines:
                f.write(f"{tcl_line}\n")

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
