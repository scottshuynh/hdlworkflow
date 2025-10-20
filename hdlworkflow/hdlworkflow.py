import argparse
import logging
import os
import sys

from hdlworkflow.nvc import Nvc
from hdlworkflow.vivado import Vivado
from hdlworkflow.riviera import Riviera
from hdlworkflow.logging import set_log_level, LoggingLevel


logger = logging.getLogger(__name__)
supported_eda_tools: set[str] = set(["nvc", "vivado", "riviera"])
supported_waveform_viewers: set[str] = set(["gtkwave"])


class HdlWorkflow:
    def __init__(
        self,
        eda_tool: str,
        top: str,
        path_to_compile_order: str,
        path_to_working_directory: str,
        generic: list[str] = [],
        cocotb: str = "",
        pythonpaths: str = "",
        gui: bool = False,
        wave: str = "gtkwave",
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
            path_to_working_directory (str): Path to hdlworkflow working directory. Any relative paths specified for
                any hdlworkflow argument will be relative to this directory.
            generic (list[str], optional): Top will elaborate with specified generics. Must be in form: GENERIC=VALUE.
                Defaults to [].
            cocotb (str, optional): Name of cocotb test module. Defaults to "".
            pythonpaths (str, optional): PYTHONPATH environment variable. Defaults to "".
            gui (bool, optional): Opens the EDA tool GUI, if supported. Defaults to False.
            wave (str, optional): Waveform viewer of choice. Defaults to "gtkwave".
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
        self.gui = gui
        self.wave = wave.lower()
        self.part = part.lower()
        self.board = board.lower()
        self.synth = synth
        self.impl = impl
        self.bitstream = bitstream
        self.ooc = ooc
        self.clk_period_constraint = clk_period_constraint

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
                    cocotb_module=self.cocotb,
                    waveform_viewer=wave,
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
                    path_to_working_directory=self.path_to_working_directory,
                    part_number=self.part,
                    board_part=self.board,
                    start_gui=self.gui,
                    synth=self.synth,
                    impl=self.impl,
                    bitstream=self.bitstream,
                    ooc=self.ooc,
                    clk_period_constraints=self.clk_period_constraint,
                )
                vivado.start()

            elif self.eda_tool == "riviera":
                if self.gui:
                    logger.info("Riviera-PRO will open the GUI.")

                riviera = Riviera(
                    top=self.top,
                    compile_order=self.path_to_compile_order,
                    generics=self.generic,
                    cocotb_module=self.cocotb,
                    gui=self.gui,
                    path_to_working_directory=self.path_to_working_directory,
                    pythonpaths=self.pythonpaths,
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
        "-g",
        "--generic",
        action="append",
        type=str,
        metavar="GENERIC=VALUE",
        help="Generics used to elaborate top design file. Must take the form: GENERIC=VALUE.",
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
    path_to_working_directory = os.getcwd()

    pythonpaths: list[str] = [path_to_working_directory]
    if args.pythonpath:
        pythonpaths += args.pythonpath

    if args.verbose:
        if args.verbose >= 0 and args.verbose <= 2:
            set_log_level(LoggingLevel(args.verbose))
        else:
            logger.error(f"Invalid verbose level. Got: {args.verbose}. Expecting: 0, 1, 2")
            sys.exit(1)

    workflow = HdlWorkflow(
        eda_tool=args.eda_tool,
        top=args.top,
        path_to_compile_order=args.path_to_compile_order,
        path_to_working_directory=path_to_working_directory,
        generic=args.generic,
        cocotb=args.cocotb,
        pythonpaths=pythonpaths,
        gui=args.gui,
        wave=args.wave,
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
