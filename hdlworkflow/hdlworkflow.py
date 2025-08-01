import argparse
import logging
import os
import sys
from typing import List, Set

from hdlworkflow.nvc import Nvc
from hdlworkflow.vivado import Vivado
from hdlworkflow.riviera import Riviera
from hdlworkflow.logging import set_log_level, LoggingLevel


logger = logging.getLogger(__name__)
supported_simulators: Set[str] = set(["nvc", "vivado", "riviera"])
supported_waveform_viewers: Set[str] = set(["gtkwave", "riviera"])


class HdlWorkflow:
    def __init__(
        self,
        simulator: str,
        top: str,
        path_to_compile_order: str,
        generic: List[str],
        cocotb: str,
        pwd: str,
        pythonpaths: str,
        wave: str,
        part: str,
        board: str,
    ):
        self.simulator = simulator
        self.top = top
        self.path_to_compile_order = path_to_compile_order
        self.generic = generic
        self.cocotb = cocotb
        self.pwd = pwd
        self.pythonpaths = pythonpaths
        self.wave = wave
        self.part = part
        self.board = board

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
                    self.pwd,
                    self.pythonpaths,
                )
                nvc.simulate()

            elif self.simulator == "vivado":
                if self.cocotb:
                    logger.error("Vivado is not compatible with cocotb simulations.")
                    sys.exit(1)
                if self.wave:
                    logger.warning(
                        "Vivado will use its native waveform viewer instead of third party waveform viewers. Ignoring."
                    )
                vivado = Vivado(self.top, self.path_to_compile_order, self.generic, self.pwd, self.part, self.board)
                vivado.start()

            elif self.simulator == "riviera":
                if self.wave and not self.is_supported_waveform_viewer(self.wave):
                    logger.error(
                        f"Unsupported waveform viewer: {self.wave}. Expecting: {' '.join(viewer for viewer in supported_waveform_viewers)}"
                    )
                    sys.exit(1)
                riviera = Riviera(
                    self.top,
                    self.path_to_compile_order,
                    self.generic,
                    self.cocotb,
                    self.wave,
                    self.pwd,
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
        help="Specified hardware part number for synthesis",
    )
    parser.add_argument(
        "--board",
        default="",
        type=str,
        metavar="BOARD",
        help="Specified hardware board for synthesis",
    )
    args = parser.parse_args()
    pwd = os.getcwd()

    pythonpaths: List[str] = [pwd]
    if args.pythonpath:
        pythonpaths += args.pythonpath

    if args.verbose:
        if args.verbose >= 0 and args.verbose <= 2:
            set_log_level(LoggingLevel(args.verbose))
        else:
            logger.error(f'Invalid verbose level. Got: {args.verbose}. Expecting: 0, 1, 2')
            sys.exit(1)

    workflow = HdlWorkflow(
        args.simulator,
        args.top,
        args.path_to_compile_order,
        args.generic,
        args.cocotb,
        pwd,
        pythonpaths,
        args.wave,
        args.part,
        args.board,
    )
    workflow.run()


if __name__ == "__main__":
    hdlworkflow()
