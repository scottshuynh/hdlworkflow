import argparse
import os
import sys
from typing import List, Set

from .nvc import Nvc

supported_simulators: Set[str] = set(["nvc"])
supported_waveform_viewers: Set[str] = set(["gtkwave"])


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
        "-w",
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
        "-c",
        "--cocotb",
        type=str,
        metavar="COCOTB_MODULE",
        help="Specified cocotb test module to run during simulation.",
    )
    parser.add_argument(
        "-p",
        "--pythonpath",
        action="append",
        type=str,
        metavar="PYTHONPATH",
        help="Paths to add to PYTHONPATH",
    )
    args = parser.parse_args()

    pwd = os.getcwd()
    os.makedirs("sim", exist_ok=True)
    os.chdir("sim")

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
    else:
        print(
            f"Unsupported simulator. Got: {args.simulator}. Expecting: {" ".join(simulator for simulator in supported_simulators)}"
        )
        sys.exit(1)


if __name__ == "__main__":
    hdlworkflow()
