import pytest
from pathlib import Path
from shutil import which

import hdlworkflow
from hdlworkflow import HdlWorkflow


@pytest.mark.parametrize("eda_tool", hdlworkflow.supported_eda_tools)
@pytest.mark.parametrize("data_w", [8])
@pytest.mark.parametrize("depth", [16])
@pytest.mark.parametrize("stop_time", [tuple([10, "ns"])])
def test_vhdl_sim(eda_tool, data_w, depth, stop_time, worker_id):
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    pwd = Path(__file__).parent / ("output_" + worker_id)
    pwd.mkdir(parents=True, exist_ok=True)

    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="fifo_sync_tb",
        path_to_compile_order="../compile_order.json",
        path_to_working_directory=pwd,
        generic=[f"{data_w=}", f"{depth=}"],
        stop_time=stop_time,
    )
    flow.run()


@pytest.mark.parametrize("data_w", [8])
@pytest.mark.parametrize("depth", [16])
@pytest.mark.parametrize("synth", [False, True])
@pytest.mark.parametrize("impl", [False, True])
@pytest.mark.parametrize(
    "part",
    ["", "xczu7ev-ffvc1156-2-e"],
)
@pytest.mark.parametrize("board", ["", "xilinx.com:zcu106:part0:2.6"])
@pytest.mark.parametrize("clk_period_constraint", ["clk_i=4"])
def test_vhdl_synth_vivado(data_w, depth, synth, impl, part, board, clk_period_constraint, worker_id):
    eda_tool = "vivado"
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")
    if not synth ^ impl:
        pytest.skip(f"{synth=} and {impl=} must be mutually exclusive. Skipping...")

    pwd = Path(__file__).parent / ("output_" + worker_id)
    pwd.mkdir(parents=True, exist_ok=True)

    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="fifo_sync",
        path_to_compile_order="../compile_order.json",
        path_to_working_directory=pwd,
        generic=[f"{data_w=}", f"{depth=}"],
        synth=synth,
        impl=impl,
        ooc=True,
        part=part,
        board=board,
        clk_period_constraint=[clk_period_constraint],
    )
    flow.run()


@pytest.mark.parametrize("eda_tool", hdlworkflow.supported_eda_tools)
@pytest.mark.parametrize("data_w", [8])
@pytest.mark.parametrize("depth", [16])
def test_vhdl_cocotb(eda_tool, data_w, depth, worker_id):
    if eda_tool == "vivado":
        pytest.skip("Vivado does not support cocotb. Skipping...")
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    pwd = Path(__file__).parent / ("output_" + worker_id)
    pwd.mkdir(parents=True, exist_ok=True)

    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="fifo_sync",
        path_to_compile_order="../compile_order.json",
        path_to_working_directory=pwd,
        generic=[f"{data_w=}", f"{depth=}"],
        pythonpaths=[str(pwd.parent)],
        cocotb="fifo_sync_tb",
    )
    flow.run()
