import logging, os, pytest
from pathlib import Path
from shutil import which

import hdlworkflow
from hdlworkflow import HdlWorkflow
from hdlworkflow.logging import set_log_level, LoggingLevel

# logger = logging.getLogger("hdlworkflow")
set_log_level(LoggingLevel(2))


@pytest.mark.parametrize("data_w", [72])
@pytest.mark.parametrize("depth", [2**19])
def test_nvc_extra_args_cocotb(data_w, depth, worker_id):
    eda_tool = "nvc"
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    pwd = Path(__file__).parent / ("output_" + worker_id)
    pwd.mkdir(parents=True, exist_ok=True)

    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="fifo_sync",
        compile_order="../compile_order.json",
        path_to_working_directory=pwd,
        generics=[f"{data_w=}", f"{depth=}"],
        pythonpaths=[str(pwd.parent)],
        cocotb="fifo_sync_tb",
        extra_args=["-H 64m"],
    )
    flow.run()


@pytest.mark.parametrize("data_w", [72])
@pytest.mark.parametrize("depth", [2**19])
def test_nvc_extra_args_cocotb_cli(data_w, depth, worker_id):
    eda_tool = "nvc"
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    pwd = Path(__file__).parent / ("output_" + worker_id)
    pwd.mkdir(parents=True, exist_ok=True)
    os.chdir(pwd)

    argv = [
        eda_tool,
        "fifo_sync",
        "../compile_order.json",
        "-g",
        f"{data_w=}",
        "-g",
        f"{depth=}",
        "--cocotb",
        "fifo_sync_tb",
        "--pythonpath",
        str(pwd.parent),
        "--extra_args",
        "-H 64m",
    ]

    hdlworkflow.cli.main(argv)


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [8])
def test_riviera_extra_args_cocotb(data_w, depth, worker_id):
    eda_tool = "riviera"
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    pwd = Path(__file__).parent / ("output_" + worker_id)
    pwd.mkdir(parents=True, exist_ok=True)

    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="fifo_sync",
        compile_order="../compile_order.json",
        path_to_working_directory=pwd,
        generics=[f"{data_w=}", f"{depth=}"],
        pythonpaths=[str(pwd.parent)],
        cocotb="fifo_sync_tb",
        extra_args=["-dbg"],
    )
    flow.run()


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [8])
def test_riviera_extra_args_cocotb_cli(data_w, depth, worker_id):
    eda_tool = "riviera"
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    pwd = Path(__file__).parent / ("output_" + worker_id)
    pwd.mkdir(parents=True, exist_ok=True)
    os.chdir(pwd)

    argv = [
        eda_tool,
        "fifo_sync",
        "../compile_order.json",
        "-g",
        f"{data_w=}",
        "-g",
        f"{depth=}",
        "--cocotb",
        "fifo_sync_tb",
        "--pythonpath",
        str(pwd.parent),
        "--extra_args",
        "-dbg ",
    ]

    hdlworkflow.cli.main(argv)


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [8])
def test_vivado_extra_args(data_w, depth, worker_id):
    eda_tool = "vivado"
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    pwd = Path(__file__).parent / ("output_" + worker_id)
    pwd.mkdir(parents=True, exist_ok=True)

    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="fifo_sync_tb",
        compile_order="../compile_order.json",
        path_to_working_directory=pwd,
        generics=[f"{data_w=}", f"{depth=}"],
        extra_args=["-quiet", "-onfinish quit"],
    )
    flow.run()


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [8])
def test_vivado_extra_args_cli(data_w, depth, worker_id):
    eda_tool = "vivado"
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    pwd = Path(__file__).parent / ("output_" + worker_id)
    pwd.mkdir(parents=True, exist_ok=True)
    os.chdir(pwd)

    argv = [
        eda_tool,
        "fifo_sync_tb",
        "../compile_order.json",
        "-g",
        f"{data_w=}",
        "-g",
        f"{depth=}",
        "--extra_args",
        "-quiet ",
        "--extra_args",
        "-onfinish quit",
    ]

    hdlworkflow.cli.main(argv)
