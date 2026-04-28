import pytest
from pathlib import Path
from shutil import which

import hdlworkflow
from hdlworkflow import HdlWorkflow


@pytest.mark.parametrize("eda_tool", hdlworkflow.supported_eda_tools)
@pytest.mark.skip
def test_vhdl_compile_order_json(eda_tool, worker_id):
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    pwd = Path(__file__).parent / ("output_" + worker_id)
    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="top_compile_me",
        path_to_compile_order="../vhdl_compile_order.json",
        path_to_working_directory=str(pwd),
    )
    flow.run()


@pytest.mark.parametrize("eda_tool", hdlworkflow.supported_eda_tools)
@pytest.mark.skip
def test_verilog_compile_order_json(eda_tool, worker_id):
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    pwd = Path(__file__).parent / ("output_" + worker_id)
    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="top_compile_me",
        path_to_compile_order="../verilog_compile_order.json",
        path_to_working_directory=str(pwd),
    )
    flow.run()


@pytest.mark.parametrize("eda_tool", hdlworkflow.supported_eda_tools)
@pytest.mark.skip
def test_mixed_compile_order_json(eda_tool, worker_id):
    if eda_tool == "nvc":
        pytest.skip()

    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    pwd = Path(__file__).parent / ("output_" + worker_id)
    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="top_compile_me",
        path_to_compile_order="../mixed_hdl_compile_order.json",
        path_to_working_directory=str(pwd),
    )
    flow.run()


def test_messy_compile_order_json(worker_id):
    pwd = Path(__file__).parent / ("output_" + worker_id)
    flow = HdlWorkflow(
        eda_tool="nvc",
        top="top_compile_me",
        path_to_compile_order="../messy_compile_order.json",
        path_to_working_directory=str(pwd),
    )
    flow.run()
