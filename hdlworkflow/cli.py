from .core import HdlWorkflow, supported_eda_tools, supported_waveform_viewers
from .logging import set_log_level, LoggingLevel
import argparse, logging, sys
from pathlib import Path

logger = logging.getLogger(__name__)


def main(argv=None):
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
        default=[],
        type=str,
        metavar="GENERIC=VALUE",
        help="Generics used to elaborate top design file. Must take the form: GENERIC=VALUE.",
    )
    parser.add_argument(
        "-l",
        "--libraries",
        action="append",
        default=[],
        type=str,
        metavar="LIBRARY_NAME",
        help="Libraries searched during top level design instantiation in simulation.",
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
        default=[],
        type=str,
        metavar="PYTHONPATH",
        help="Paths to add to PYTHONPATH",
    )
    parser.add_argument(
        "--plusargs",
        action="append",
        default=[],
        type=str,
        metavar="PLUSARG",
        help="Simulation plusargs",
    )
    parser.add_argument(
        "--libstdcpp",
        default="",
        type=str,
        metavar="LIBSTDC++",
        help="Path to libstdc++ shared object.",
    )
    parser.add_argument(
        "--glbl",
        default="",
        type=str,
        metavar="GLBL.V",
        help="Path to glbl.v.",
    )
    parser.add_argument(
        "--work",
        default="",
        type=str,
        metavar="DEFAULT_LIB",
        help="Name of default library.",
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
        default=[],
        type=str,
        metavar="CLK_PORT=PERIOD_NS",
        help="Clock period constraint for synthesis. Only for synthesis tools. Must take the form: "
        + "CLK_PORT=PERIOD_NS.",
    )
    args = parser.parse_args(argv)
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
        libraries=args.libraries,
        stop_time=stop_time,
        cocotb=args.cocotb,
        pythonpaths=pythonpaths,
        plusargs=args.plusargs,
        path_to_libstdcpp=args.libstdcpp,
        path_to_glbl=args.glbl,
        work=args.work,
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
