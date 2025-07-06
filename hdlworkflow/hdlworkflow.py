import argparse
import os
import sys
from typing import List, Set

from .nvc import Nvc
from .vivado import Vivado
from .riviera import Riviera

supported_simulators: Set[str] = set(["nvc", "vivado", "riviera"])
supported_waveform_viewers: Set[str] = set(["gtkwave", "riviera"])


def is_supported_simulator(simulator: str) -> bool:
    if simulator in supported_simulators:
        return True
    return False


def is_supported_waveform_viewer(viewer: str) -> bool:
    if viewer in supported_waveform_viewers:
        return True
    return False


def hdlworkflow():
    parser = argparse.ArgumentParser(
        "hdlworkflow",
        description="Streamline HDL simulations.",
    )
    parser.add_argument(
        "simulator",
        type=str,
        help=f"Specified HDL simulator to run. Supported simulators: {" ".join(simulator for simulator in supported_simulators)}.",
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
        help=f"Specified waveform viewer to run at the end of the simulation. Supported waveform viewers: {" ".join(viewer for viewer in supported_waveform_viewers)}.",
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

    if is_supported_simulator(args.simulator):
        if args.simulator == "nvc":
            if args.wave and not is_supported_waveform_viewer(args.wave):
                print(
                    f"Unsupported waveform viewer. Got: {args.wave}. Expecting: {" ".join(viewer for viewer in supported_waveform_viewers)}"
                )
                sys.exit(1)
            nvc = Nvc(args.top, args.path_to_compile_order, args.generic, args.cocotb, args.wave, pwd, pythonpaths)
            nvc.simulate()

        elif args.simulator == "vivado":
            if args.cocotb:
                print("Vivado is not compatible with cocotb simulations.")
                sys.exit(1)
            if args.wave:
                print("Vivado will use its native waveform viewer instead of third party waveform viewers. Ignoring.")
            vivado = Vivado(args.top, args.path_to_compile_order, args.generic, pwd, args.part, args.board)
            vivado.simulate()

        elif args.simulator == "riviera":
            if args.wave and not is_supported_waveform_viewer(args.wave):
                print(
                    f"Unsupported waveform viewer. Got: {args.wave}. Expecting: {" ".join(viewer for viewer in supported_waveform_viewers)}"
                )
                sys.exit(1)
            riviera = Riviera(
                args.top, args.path_to_compile_order, args.generic, args.cocotb, args.wave, pwd, pythonpaths
            )
            riviera.simulate()
    else:
        print(
            f"Unsupported simulator. Got: {args.simulator}. Expecting: {" ".join(simulator for simulator in supported_simulators)}"
        )
        sys.exit(1)


if __name__ == "__main__":
    hdlworkflow()
