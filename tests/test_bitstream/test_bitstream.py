import os
from pathlib import Path
import pytest
from shutil import which

import hdlworkflow
from hdlworkflow import HdlWorkflow


def test_vhdl_bitstream_vivado_cli(worker_id):
    eda_tool = "vivado"
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    pwd = Path(__file__).parent / ("output_" + worker_id)
    pwd.mkdir(parents=True, exist_ok=True)
    os.chdir(pwd)

    argv = [
        eda_tool,
        "blinky",
        "../vhdl_compile_order.json",
        "--bitstream",
        "--part",
        "xc7a100tcsg324-1",
        "--clk-period-constraint",
        "clk_i=10",
    ]

    hdlworkflow.cli.main(argv)


def test_vhdl_bitstream_vivado(worker_id):
    eda_tool = "vivado"
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    pwd = Path(__file__).parent / ("output_" + worker_id)
    pwd.mkdir(parents=True, exist_ok=True)
    os.chdir(pwd)

    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="blinky",
        compile_order="../vhdl_compile_order.json",
        path_to_working_directory=pwd,
        bitstream=True,
        part="xc7a100tcsg324-1",
        clk_period_constraints=["clk_i=10"],
    )
    flow.run()


def test_verilog_bitstream_vivado_cli(worker_id):
    eda_tool = "vivado"
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    pwd = Path(__file__).parent / ("output_" + worker_id)
    pwd.mkdir(parents=True, exist_ok=True)
    os.chdir(pwd)

    argv = [
        eda_tool,
        "blinky",
        "../verilog_compile_order.json",
        "--bitstream",
        "--part",
        "xc7a100tcsg324-1",
        "--clk-period-constraint",
        "clk_i=10",
    ]

    hdlworkflow.cli.main(argv)


def test_verilog_bitstream_vivado(worker_id):
    eda_tool = "vivado"
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    pwd = Path(__file__).parent / ("output_" + worker_id)
    pwd.mkdir(parents=True, exist_ok=True)
    os.chdir(pwd)

    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="blinky",
        compile_order="../verilog_compile_order.json",
        path_to_working_directory=pwd,
        bitstream=True,
        part="xc7a100tcsg324-1",
        clk_period_constraints=["clk_i=10"],
    )
    flow.run()
