import argparse, logging, sys
from pathlib import Path

from hdlworkflow.nvc import Nvc
from hdlworkflow.vivado import Vivado
from hdlworkflow.riviera import Riviera
from hdlworkflow.logging import set_log_level, LoggingLevel


logger = logging.getLogger(__name__)
supported_eda_tools: set[str] = set(["nvc", "vivado", "riviera"])
supported_waveform_viewers: set[str] = set(["gtkwave"])
supported_time_units: set[str] = set(["fs", "ps", "ns", "us", "ms", "s"])


class HdlWorkflow:
    def __init__(
        self,
        eda_tool: str,
        top: str,
        path_to_compile_order: str,
        path_to_working_directory: str,
        generic: list[str] = [],
        stop_time: tuple[int, str] = (),
        cocotb: str = "",
        pythonpaths: list[str] = [],
        path_to_libstdcpp: str = "",
        path_to_glbl: str = "",
        gui: bool = False,
        wave: str = "gtkwave",
        waveform_view_file: str = "",
        part: str = "",
        board: str = "",
        synth: bool = False,
        impl: bool = False,
        bitstream: bool = False,
        ooc: bool = False,
        clk_period_constraint: list[str] = [],
    ):
        """
        Runs a workflow for the specified EDA tool.
            Simulation tools run: analyse, elaborate, simulate.
            Synthesis tools run: synthesis, place and route, generate bitstream.

                Default behaviour is simulation. Running synthesis will require use of arguments - see below.

        Args:
            eda_tool (str): EDA tool of choice
            top (str): Name of top design
            path_to_compile_order (str): Path to a file listing HDL source files in compilation order for simulation.
            path_to_working_directory (str): Absolute path to hdlworkflow working directory. Any relative paths
                specified for any hdlworkflow argument will be relative to this directory.
            generic (list[str], optional): Top will elaborate with specified generics. Must be in form: GENERIC=VALUE.
                Defaults to [].
            stop_time (tuple[int, str]): Simulation stops after the specified period.
            cocotb (str, optional): Name of cocotb test module. Defaults to "".
            pythonpaths (list[str], optional): PYTHONPATH environment variable. Defaults to [].
            path_to_libstdcpp (str, optional): Path to libstdc++ shared object. Defaults to "".
            path_to_glbl (str, optional): Path to glbl.v. Defaults to "".
            gui (bool, optional): Opens the EDA tool GUI, if supported. Defaults to False.
            wave (str, optional): Waveform viewer of choice. Defaults to "gtkwave".
            waveform_view_file (str, optional): Waveform view file path.
            part (str, optional): Vivado part number to set up Vivado project. Defaults to "".
            board (str, optional): Vivado board part to set up Vivado project. Defaults to "".
            synth (bool, optional): Vivado starts synthesis instead of simulation. Defaults to False.
            impl (bool, optional): Vivado starts synthesis + implementation instead of simulation. Defaults to False.
            bitstream (bool, optional): Vivado starts synthesis + implementation + generate bitstream instead of
                simulation. Defaults to False.
            ooc (bool, optional): Vivado synthesis mode set to out-of-context. Defaults to False.
            clk_period_constraint (list[str], optional): Vivado clock period constraints.
                Must be in form: CLK_PORT=PERIOD_NS. Defaults to [].
        """
        self.eda_tool = eda_tool.lower()
        self.top = top
        self.path_to_compile_order = path_to_compile_order
        self.generic = generic
        self.cocotb = cocotb
        self.path_to_working_directory = path_to_working_directory
        self.pythonpaths = pythonpaths
        self.path_to_libstdcpp = path_to_libstdcpp
        self.path_to_glbl = path_to_glbl
        self.gui = gui
        self.wave = wave.lower()
        self.part = part.lower()
        self.board = board.lower()
        self.synth = synth
        self.impl = impl
        self.bitstream = bitstream
        self.ooc = ooc
        self.clk_period_constraint = clk_period_constraint

        self.path_to_compile_order = path_to_compile_order
        if Path(path_to_compile_order).is_absolute():
            if not Path(path_to_compile_order).is_file():
                logger.error(f"Path to compile order ({path_to_compile_order}) does not exist.")
                sys.exit(1)
        else:
            self.path_to_compile_order = str((Path(path_to_working_directory) / path_to_compile_order).resolve())
            if not Path(self.path_to_compile_order).is_file():
                logger.error(f"Path to compile order ({self.path_to_compile_order}) does not exist.")
                sys.exit(1)

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

    def is_supported_eda_tool(self, eda_tool: str) -> bool:
        if eda_tool in supported_eda_tools:
            return True
        return False

    def is_supported_waveform_viewer(self, viewer: str) -> bool:
        if viewer in supported_waveform_viewers:
            return True
        return False

    def run(self):
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
                    compile_order=self.path_to_compile_order,
                    generics=self.generic,
                    stop_time="".join(self.stop_time.split()),
                    cocotb_module=self.cocotb,
                    waveform_viewer=wave,
                    waveform_view_file=self.waveform_view_file,
                    path_to_working_directory=self.path_to_working_directory,
                    pythonpaths=self.pythonpaths,
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
                    compile_order=self.path_to_compile_order,
                    generics=self.generic,
                    stop_time="".join(self.stop_time.split()),
                    path_to_working_directory=self.path_to_working_directory,
                    part_number=self.part,
                    board_part=self.board,
                    gui=self.gui,
                    waveform_view_file=self.waveform_view_file,
                    synth=self.synth,
                    impl=self.impl,
                    bitstream=self.bitstream,
                    ooc=self.ooc,
                    clk_period_constraints=self.clk_period_constraint,
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
                    compile_order=self.path_to_compile_order,
                    generics=self.generic,
                    stop_time=self.stop_time,
                    cocotb_module=self.cocotb,
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


def hdlworkflow():
    parser = argparse.ArgumentParser(
        "hdlworkflow",
        description="Streamlining FPGA EDA tool workflows.",
    )
    parser.add_argument(
        "eda_tool",
        type=str,
        help="EDA tool to run. Supported EDA tools: " + " ".join(eda_tool for eda_tool in supported_eda_tools),
    )
    parser.add_argument(
        "top",
        type=str,
        help="Top design file.",
    )
    parser.add_argument(
        "path_to_compile_order",
        type=str,
        help="Path to a file containing a list of all requisite files for the top design.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Opens the EDA tool GUI.",
    )
    parser.add_argument(
        "--wave",
        default="gtkwave",
        type=str,
        metavar="WAVEFORM_VIEWER",
        help=f"Waveform viewer for tools that do not have a native waveform viewer. Supported waveform viewers: "
        + " ".join(viewer for viewer in supported_waveform_viewers),
    )
    parser.add_argument(
        "--waveform-view-file",
        default="",
        type=str,
        metavar="WAVEFORM_VIEW_FILE",
        help="Waveform view file path.",
    )
    parser.add_argument(
        "-g",
        "--generic",
        action="append",
        type=str,
        metavar="GENERIC=VALUE",
        help="Generics used to elaborate top design file. Must take the form: GENERIC=VALUE.",
    )
    parser.add_argument(
        "--stop-time",
        nargs=2,
        metavar=("INTEGER_PERIOD", "TIME_UNITS"),
        type=str,
        help="Stop simulation after the specified period. Must take the form: INTEGER_PERIOD TIME_UNITS.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        type=int,
        metavar="VERBOSE_LEVEL",
        help="Level of verbosity. Valid verbose levels are: 0, 1, 2.",
    )
    parser.add_argument(
        "--cocotb",
        type=str,
        metavar="COCOTB_MODULE",
        help="Cocotb test module to run during simulation.",
    )
    parser.add_argument(
        "--pythonpath",
        action="append",
        type=str,
        metavar="PYTHONPATH",
        help="Paths to add to PYTHONPATH",
    )
    parser.add_argument(
        "--libstdcpp",
        type=str,
        metavar="LIBSTDC++",
        help="Path to libstdc++ shared object.",
    )
    parser.add_argument(
        "--glbl",
        type=str,
        metavar="GLBL.V",
        help="Path to glbl.v.",
    )
    parser.add_argument(
        "--part",
        default="",
        type=str,
        metavar="PART_NUMBER",
        help="Hardware part number for synthesis. Only for synthesis tools.",
    )
    parser.add_argument(
        "--board",
        default="",
        type=str,
        metavar="BOARD",
        help="Hardware board for synthesis. Only for synthesis tools.",
    )
    parser.add_argument(
        "--synth",
        action="store_true",
        help="Specifies EDA tool to run synthesis instead of simulation. Only for synthesis tools.",
    )
    parser.add_argument(
        "--impl",
        action="store_true",
        help="Specifies EDA tool to run implementation instead of simulation. Only for synthesis tools.",
    )
    parser.add_argument(
        "--bitstream",
        action="store_true",
        help="Specifies EDA tool to generate a bitfile instead of simulation. Only for synthesis tools.",
    )
    parser.add_argument(
        "--ooc",
        action="store_true",
        help="Specifies EDA tool to set synthesis mode to out-of-context. Only for synthesis tools.",
    )
    parser.add_argument(
        "--clk-period-constraint",
        action="append",
        type=str,
        metavar="CLK_PORT=PERIOD_NS",
        help="Clock period constraint for synthesis. Only for synthesis tools. Must take the form: "
        + "CLK_PORT=PERIOD_NS.",
    )
    args = parser.parse_args()
    path_to_working_directory = str(Path.cwd())

    pythonpaths: list[str] = [path_to_working_directory]
    if args.pythonpath:
        pythonpaths += args.pythonpath

    if args.verbose:
        if args.verbose >= 0 and args.verbose <= 2:
            set_log_level(LoggingLevel(args.verbose))
        else:
            logger.error(f"Invalid verbose level. Got: {args.verbose}. Expecting: 0, 1, 2")
            sys.exit(1)

    stop_time: tuple[int, str] = ()
    if args.stop_time:
        if args.stop_time[0].isdigit():
            stop_time = (int(args.stop_time[0]), args.stop_time[1])
        else:
            logger.error(f"--stop-time must be an integer. Got: {args.stop_time[0]}")
            sys.exit(1)

    workflow = HdlWorkflow(
        eda_tool=args.eda_tool,
        top=args.top,
        path_to_compile_order=args.path_to_compile_order,
        path_to_working_directory=path_to_working_directory,
        generic=args.generic,
        stop_time=stop_time,
        cocotb=args.cocotb,
        pythonpaths=pythonpaths,
        path_to_libstdcpp=args.libstdcpp,
        path_to_glbl=args.glbl,
        gui=args.gui,
        wave=args.wave,
        waveform_view_file=args.waveform_view_file,
        part=args.part,
        board=args.board,
        synth=args.synth,
        impl=args.impl,
        bitstream=args.bitstream,
        ooc=args.ooc,
        clk_period_constraint=args.clk_period_constraint,
    )
    workflow.run()


if __name__ == "__main__":
    hdlworkflow()
