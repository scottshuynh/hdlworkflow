import argparse
import logging
import os
import sys

from hdlworkflow.nvc import Nvc
from hdlworkflow.vivado import Vivado
from hdlworkflow.riviera import Riviera
from hdlworkflow.logging import set_log_level, LoggingLevel


logger = logging.getLogger(__name__)
supported_simulators: set[str] = set(["nvc", "vivado", "riviera"])
supported_waveform_viewers: set[str] = set(["gtkwave", "vivado", "riviera"])


class HdlWorkflow:
    def __init__(
        self,
        simulator: str,
        top: str,
        path_to_compile_order: str,
        path_to_working_directory: str,
        generic: list[str] = [],
        cocotb: str = "",
        pythonpaths: str = "",
        wave: str = "",
        part: str = "",
        board: str = "",
        synth: bool = False,
        clk_constraint: list[str] = []
    ):
        """Runs analyse, elaborate, simulate using the specified simulator.

        Args:
            simulator (str): Simulator of choice
            top (str): Name of top design
            path_to_compile_order (str): Path to a file listing HDL source files in compilation order for simulation
            path_to_working_directory (str): Path to directory for hdlworkflow to output artefacts
            generic (list[str], optional): Top will elaborate with specified generics. Must be in form: GENERIC=VALUE. Defaults to [].
            cocotb (str, optional): Name of cocotb test module. Defaults to "".
            pythonpaths (str, optional): PYTHONPATH environment variable. Defaults to "".
            wave (str, optional): Waveform viewer of choice. Defaults to "".
            part (str, optional): Vivado part number to set up Vivado project. Defaults to "".
            board (str, optional): Vivado board part to set up Vivado project. Defaults to "".
            synth (bool, optional): Vivado starts synthesis instead of simulation. Defaults to False.
            clk_constraint (list[str], optional): Vivado clock constraints. Must be in form: CLK_PORT=PERIOD_NS. Defaults to [].
        """
        self.simulator = simulator.lower()
        self.top = top
        self.path_to_compile_order = path_to_compile_order
        self.generic = generic
        self.cocotb = cocotb
        self.path_to_working_directory = path_to_working_directory
        self.pythonpaths = pythonpaths
        self.wave = wave.lower()
        self.part = part.lower()
        self.board = board.lower()
        self.synth = synth
        self.clk_constraint = clk_constraint

    def is_supported_simulator(self, simulator: str) -> bool:
        if simulator in supported_simulators:
            return True
        return False

    def is_supported_waveform_viewer(self, viewer: str) -> bool:
        if viewer in supported_waveform_viewers:
            return True
        return False

    def run(self):
        logger.info("Starting hdlworkflow...")
        if self.is_supported_simulator(self.simulator):
            if self.simulator == "nvc":
                if self.wave and not self.is_supported_waveform_viewer(self.wave):
                    logger.error(
                        f"Unsupported waveform viewer: {self.wave}. Expecting: {' '.join(viewer for viewer in supported_waveform_viewers)}"
                    )
                    sys.exit(1)
                nvc = Nvc(
                    self.top,
                    self.path_to_compile_order,
                    self.generic,
                    self.cocotb,
                    self.wave,
                    self.path_to_working_directory,
                    self.pythonpaths,
                )
                nvc.simulate()

            elif self.simulator == "vivado":
                if self.cocotb:
                    logger.error("Vivado is not compatible with cocotb simulations.")
                    sys.exit(1)

                if self.wave:
                    if self.wave != "vivado":
                        logger.warning(
                            f"Vivado will open it's GUI. Ignoring waveform viewer argument: {self.wave}."
                        )
                    else:
                        logger.info("Vivado will open it's GUI.")

                vivado = Vivado(
                    self.top,
                    self.path_to_compile_order,
                    self.generic,
                    self.path_to_working_directory,
                    self.part,
                    self.board,
                    bool(self.wave),
                    self.synth,
                    self.clk_constraint,
                )
                vivado.start()

            elif self.simulator == "riviera":
                if self.wave and not self.is_supported_waveform_viewer(self.wave):
                    logger.error(
                        f"Unsupported waveform viewer: {self.wave}. Expecting: {' '.join(viewer for viewer in supported_waveform_viewers)}."
                    )
                    sys.exit(1)
                riviera = Riviera(
                    self.top,
                    self.path_to_compile_order,
                    self.generic,
                    self.cocotb,
                    self.wave,
                    self.path_to_working_directory,
                    self.pythonpaths,
                )
                riviera.simulate()
        else:
            logger.error(
                f"Unsupported simulator. Got: {self.simulator}. Expecting: {' '.join(simulator for simulator in supported_simulators)}"
            )
            sys.exit(1)


def hdlworkflow():
    parser = argparse.ArgumentParser(
        "hdlworkflow",
        description="Streamline HDL simulations.",
    )
    parser.add_argument(
        "simulator",
        type=str,
        help=f"Specified HDL simulator to run. Supported simulators: {' '.join(simulator for simulator in supported_simulators)}.",
    )
    parser.add_argument(
        "top",
        type=str,
        help="Specified top design file to simulate.",
    )
    parser.add_argument(
        "path_to_compile_order",
        type=str,
        help="Specified path to a file containing a list of all files used to simulate the top design file.",
    )
    parser.add_argument(
        "--wave",
        default="",
        type=str,
        metavar="WAVEFORM_VIEWER",
        help=f"Specified waveform viewer to run at the end of the simulation. Supported waveform viewers: {' '.join(viewer for viewer in supported_waveform_viewers)}.",
    )
    parser.add_argument(
        "-g",
        "--generic",
        action="append",
        type=str,
        metavar="GENERIC=VALUE",
        help="Specified generics used to elaborate top design file. Must take the form: GENERIC=VALUE.",
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
        help="Specified cocotb test module to run during simulation.",
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
        help="Specified hardware part number for synthesis. Only for synthesis tools.",
    )
    parser.add_argument(
        "--board",
        default="",
        type=str,
        metavar="BOARD",
        help="Specified hardware board for synthesis. Only for synthesis tools.",
    )
    parser.add_argument(
        "--synth",
        action="store_true",
        help="Specifies tool to run synthesis instead of simulation. Only for synthesis tools."
    )
    parser.add_argument(
        "--clk-constraint",
        action="append",
        type=str,
        metavar="CLK_PORT=PERIOD_NS",
        help="Specified clock constraint for synthesis. Only for synthesis tools. Must take the form: CLK_PORT=PERIOD_NS.",
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
            logger.error(
                f"Invalid verbose level. Got: {args.verbose}. Expecting: 0, 1, 2"
            )
            sys.exit(1)

    workflow = HdlWorkflow(
        args.simulator,
        args.top,
        args.path_to_compile_order,
        path_to_working_directory,
        args.generic,
        args.cocotb,
        pythonpaths,
        args.wave,
        args.part,
        args.board,
        args.synth,
        args.clk_constraint
    )
    workflow.run()


if __name__ == "__main__":
    hdlworkflow()
