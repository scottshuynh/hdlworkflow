import json, logging, sys
from pathlib import Path

from hdlworkflow.nvc import Nvc
from hdlworkflow.vivado import Vivado
from hdlworkflow.riviera import Riviera
import warnings

logger = logging.getLogger(__name__)
supported_eda_tools: list[str] = ["nvc", "vivado", "riviera"]
supported_waveform_viewers: list[str] = ["gtkwave", "surfer"]
supported_time_units: list[str] = ["fs", "ps", "ns", "us", "ms", "s"]


class HdlWorkflow:
    def __init__(
        self,
        eda_tool: str,
        top: str,
        path_to_working_directory: str | Path,
        compile_order: str | Path | list[dict] = "",
        generics: list[str] = [],
        libraries: list[str] = [],
        stop_time: tuple[int, str] = (),
        cocotb: str = "",
        pythonpaths: list[str] = [],
        extra_args: list[str] = [],
        plusargs: list[str] = [],
        path_to_libstdcpp: str = "",
        path_to_glbl: str = "",
        work: str = "",
        gui: bool = False,
        wave: str = "gtkwave",
        waveform_view_file: str = "",
        part: str = "",
        board: str = "",
        synth: bool = False,
        impl: bool = False,
        bitstream: bool = False,
        ooc: bool = False,
        clk_period_constraints: list[str] = [],
        path_to_compile_order="",
        generic=[],
        clk_period_constraint: list[str] = [],
    ):
        """
        Runs a workflow for the specified EDA tool.

        Simulation tools run: analyse, elaborate, simulate.
        Synthesis tools run: synthesis, place and route, generate bitstream.

        Default behaviour is simulation. Running synthesis will require use of arguments - see below.

        :param eda_tool: EDA tool of choice
        :type eda_tool: str
        :param top: Name of top design
        :type top: str
        :param path_to_working_directory: Absolute path to hdlworkflow working directory. Any relative paths
            soecified for any hdlworkflow argument will be relative to this directory
        :type path_to_working_directory: str | Path
        :param compile_order: Path to a file, or list of dictionaries containing HDL source files in compilation order
        :type compile_order: str | Path | list[dict]
        :param generics: Elaborate top design with specified generics. Elements in list must be a string in the form: GENERIC=VALUE, defaults to []
        :type generics: list[str], optional
        :param libraries: Libraries searched during top level design instantiation in simulation, defaults to []
        :type libraries: list[str], optional
        :param stop_time: Simulation stops after the specified period, defaults to ()
        :type stop_time: tuple[int, str], optional
        :param cocotb: Name of cocotb test module, defaults to ""
        :type cocotb: str, optional
        :param pythonpaths: PYTHONPATH environment variables, defaults to []
        :type pythonpaths: list[str], optional
        :param extra_args: Extra arguments for EDA tools, defaults to []
        :type extra_args: list[str], optional
        :param plusargs: Plusargs for EDA tools, defaults to []
        :type plusargs: list[str], optional
        :param path_to_libstdcpp: Path to libstdc++ shared object, defaults to ""
        :type path_to_libstdcpp: str, optional
        :param path_to_glbl: Path to AMD/Xilinx glbl.v, defaults to ""
        :type path_to_glbl: str, optional
        :param work: Name of default library, defaults to ""
        :type work: str, optional
        :param gui: Opens the EDA tool GUI, defaults to False
        :type gui: bool, optional
        :param wave: Waveform viewer of choice for EDA tools with no native GUI, defaults to "gtkwave"
        :type wave: str, optional
        :param waveform_view_file: Waveform view configuration file, defaults to ""
        :type waveform_view_file: str, optional
        :param part: Vivado part number to set up Vivado project, defaults to ""
        :type part: str, optional
        :param board: Vivado board part to set up Vivado project, defaults to ""
        :type board: str, optional
        :param synth: Vivado starts synthesis instead of simulation, defaults to False
        :type synth: bool, optional
        :param impl: Vivado starts synthesis + implementation instead of simulation, defaults to False
        :type impl: bool, optional
        :param bitstream: Vivado starts synthesis + implementation + generate bitstream instead of
            simulation, defaults to False
        :type bitstream: bool, optional
        :param ooc: Vivado synthesis mode set to out-of-context, defaults to False
        :type ooc: bool, optional
        :param clk_period_constraints: Vivado clock period constraints. Elements in list must be a string in the form:
            CLK_PORT=PERIOD_NS, defaults to []
        :type clk_period_constraints: list[str], optional
        """
        self.eda_tool = eda_tool.lower()
        self.top = top
        self.libraries = libraries
        self.cocotb = cocotb
        self.path_to_working_directory = Path(path_to_working_directory)
        self.pythonpaths = pythonpaths
        self.extra_args = extra_args
        self.plusargs = plusargs
        self.path_to_libstdcpp = path_to_libstdcpp
        self.path_to_glbl = path_to_glbl
        self.work = work.lower()
        self.gui = gui
        self.wave = wave.lower()
        self.part = part.lower()
        self.board = board.lower()
        self.synth = synth
        self.impl = impl
        self.bitstream = bitstream
        self.ooc = ooc

        self.compile_order = []
        if path_to_compile_order:
            warnings.warn("HdlWorkflow argument 'path_to_compile_order' is deprecated. Use 'compile_order' instead")
            self.compile_order = self._parse_compile_order(path_to_compile_order)
        else:
            self.compile_order = self._parse_compile_order(compile_order)

        self.generics = []
        if generic:
            warnings.warn("HdlWorkflow argument 'generic' is deprecated. Use 'generics' instead")
            self.generics = generic
        else:
            self.generics = generics

        self.clk_period_constraints = []
        if clk_period_constraint:
            warnings.warn(
                "HdlWorkflow argument 'clk_period_constraint' is deprecated. Use 'clk_period_constraints' instead"
            )
            self.clk_period_constraints = clk_period_constraint
        else:
            self.clk_period_constraints = clk_period_constraints

        self.waveform_view_file = ""
        if waveform_view_file:
            wfm_view_file_path = Path(waveform_view_file)
            if not wfm_view_file_path.is_absolute():
                wfm_view_file_path = (Path(path_to_working_directory) / wfm_view_file_path).resolve()

            if not wfm_view_file_path.is_file():
                logger.error(f"No such waveform view file. ({wfm_view_file_path})")
                sys.exit(1)

            self.waveform_view_file = str(wfm_view_file_path)

        self.stop_time = ""
        if stop_time:
            if isinstance(stop_time[0], int):
                if stop_time[1] in supported_time_units:
                    self.stop_time = " ".join(str(elem) for elem in stop_time)
                else:
                    logger.error(
                        f"Unsupported time units for stop time. Expecting"
                        + " ".join(time_unit for time_unit in supported_time_units)
                        + f", got: {stop_time[1]}"
                    )
                    sys.exit(1)
            else:
                logger.error(f"--stop-time must be an integer. Got {stop_time[0]}")
                sys.exit(1)

    def _parse_compile_order(self, compile_order: str | Path | list[dict]) -> list[dict]:
        if isinstance(compile_order, str):
            return self._parse_compile_order_file(Path(compile_order))
        elif isinstance(compile_order, Path):
            return self._parse_compile_order_file(compile_order)
        elif isinstance(compile_order, list):
            if isinstance(compile_order[0], dict):
                return self._parse_compile_order_list_of_dicts(compile_order)
            else:
                raise TypeError(
                    f"Expecting the compile order list to have dict elements. Got a list of {type(compile_order[0])}"
                )
        else:
            raise TypeError(f"Expecting compile order to be a str, Path, or list of dicts. Got {type(compile_order)}")

    def _parse_compile_order_file(self, compile_order: Path) -> list[dict]:
        resolved_compile_order = compile_order
        if resolved_compile_order.is_absolute():
            if not compile_order.is_file():
                logger.error(f"Path to compile order ({compile_order}) does not exist.")
                sys.exit(1)
        else:
            resolved_compile_order = (self.path_to_working_directory / compile_order).resolve()
            if not resolved_compile_order.is_file():
                logger.error(f"Path to compile order ({resolved_compile_order}) does not exist.")
                sys.exit(1)

        if resolved_compile_order.suffix == ".txt":
            return self._parse_compile_order_txt(resolved_compile_order)
        elif resolved_compile_order.suffix == ".json":
            return self._parse_compile_order_json(resolved_compile_order)
        else:
            logger.info(f"Expecting compile order file to be .txt or .json. Got {resolved_compile_order.suffix} ")
            sys.exit(1)

    def _parse_compile_order_txt(self, compile_order: Path) -> list[dict]:
        compile_order_list = list()
        with compile_order.open("r", encoding="utf-8") as f:
            for line in f:
                elem = dict()

                # Check file exists
                file = Path(line.strip())
                if not file.is_absolute():
                    file = (self.path_to_working_directory / file).resolve()
                if not file.is_file():
                    logger.error(f"File not found: {file}")
                    sys.exit(1)
                elem["path"] = str(file)

                # Check file type
                if file.suffix == ".vhd" or file.suffix == ".vhdl":
                    elem["type"] = "vhdl"
                elif file.suffix == ".v" or file.suffix == ".sv":
                    elem["type"] = "verilog"

                # Add library
                if self.work:
                    elem["library"] = self.work
                else:
                    if self.eda_tool == "vivado":
                        elem["library"] = "xil_defaultlib"
                    else:
                        elem["library"] = "work"

                compile_order_list.append(elem)

        return compile_order_list

    def _parse_compile_order_json(self, compile_order: Path) -> list[dict]:
        with compile_order.open("r", encoding="utf-8") as f:
            compile_order_dict: dict = json.load(f)
            files = compile_order_dict.get("files")
            if files:
                if isinstance(files, list) and isinstance(files[0], dict):
                    return self._parse_compile_order_list_of_dicts(files)
                else:
                    logger.error("JSON schema mismatch! Please check JSON schema then try again.")
                    sys.exit(1)
            else:
                logger.error("JSON schema mismatch! Please check JSON schema then try again.")
                sys.exit(1)

    def _parse_compile_order_list_of_dicts(self, compile_order: list[dict]):
        for elem in compile_order:
            elem_path = Path(elem.get("path", ""))
            if not elem_path:
                logger.error("JSON schema mismatch! Please check JSON schema then try again.")
                sys.exit(1)
            else:
                if not elem_path.is_absolute():
                    elem_path = (self.path_to_working_directory / elem_path).resolve()
                if elem_path.is_file():
                    elem["path"] = str(elem_path)
                else:
                    logger.error(f"File not found: {elem_path}")
                    sys.exit(1)

        return compile_order

    def is_supported_eda_tool(self, eda_tool: str) -> bool:
        if eda_tool in supported_eda_tools:
            return True
        return False

    def is_supported_waveform_viewer(self, viewer: str) -> bool:
        if viewer in supported_waveform_viewers:
            return True
        return False

    def run(self):
        """Runs the selected EDA tool with the current hdlworkflow configuration."""
        logger.info("Starting hdlworkflow...")
        if self.is_supported_eda_tool(self.eda_tool):
            wave = ""
            if self.eda_tool == "nvc":
                if self.synth | self.impl | self.bitstream:
                    logger.error(f"Synthesis options unsupported in {self.eda_tool}.")
                    sys.exit(1)

                if self.gui and not self.is_supported_waveform_viewer(self.wave):
                    logger.error(
                        f"Unsupported waveform viewer: {self.wave}. Expecting: "
                        + " ".join(viewer for viewer in supported_waveform_viewers)
                    )
                    sys.exit(1)
                elif self.gui:
                    wave = self.wave

                nvc = Nvc(
                    top=self.top,
                    compile_order=self.compile_order,
                    generics=self.generics,
                    stop_time="".join(self.stop_time.split()),
                    cocotb_module=self.cocotb,
                    extra_args=self.extra_args,
                    plusargs=self.plusargs,
                    waveform_viewer=wave,
                    waveform_view_file=self.waveform_view_file,
                    path_to_working_directory=self.path_to_working_directory,
                    pythonpaths=self.pythonpaths,
                    work=self.work,
                )
                nvc.simulate()

            elif self.eda_tool == "vivado":
                if self.cocotb:
                    logger.error("Vivado is not compatible with cocotb simulations.")
                    sys.exit(1)

                if self.gui:
                    logger.info("Vivado will open the GUI.")

                vivado = Vivado(
                    top=self.top,
                    compile_order=self.compile_order,
                    work=self.work,
                    generics=self.generics,
                    stop_time="".join(self.stop_time.split()),
                    path_to_working_directory=self.path_to_working_directory,
                    extra_args=self.extra_args,
                    plusargs=self.plusargs,
                    part_number=self.part,
                    board_part=self.board,
                    gui=self.gui,
                    waveform_view_file=self.waveform_view_file,
                    synth=self.synth,
                    impl=self.impl,
                    bitstream=self.bitstream,
                    ooc=self.ooc,
                    clk_period_constraints=self.clk_period_constraints,
                )
                vivado.start()

            elif self.eda_tool == "riviera":
                if self.synth | self.impl | self.bitstream:
                    logger.error(f"Synthesis options unsupported in {self.eda_tool}.")
                    sys.exit(1)

                if self.gui:
                    logger.info("Riviera-PRO will open the GUI.")

                riviera = Riviera(
                    top=self.top,
                    compile_order=self.compile_order,
                    work=self.work,
                    generics=self.generics,
                    search_libraries=self.libraries,
                    stop_time=self.stop_time,
                    cocotb_module=self.cocotb,
                    extra_args=self.extra_args,
                    plusargs=self.plusargs,
                    gui=self.gui,
                    waveform_view_file=self.waveform_view_file,
                    path_to_working_directory=self.path_to_working_directory,
                    pythonpaths=self.pythonpaths,
                    path_to_libstdcpp=self.path_to_libstdcpp,
                    path_to_glbl=self.path_to_glbl,
                )
                riviera.simulate()
        else:
            logger.error(
                f"Unsupported eda_tool. Got: {self.eda_tool}. Expecting: "
                + " ".join(eda_tool for eda_tool in supported_eda_tools)
            )
            sys.exit(1)
