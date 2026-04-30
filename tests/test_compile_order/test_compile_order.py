import pytest
from pathlib import Path
from shutil import which

import hdlworkflow
from hdlworkflow import HdlWorkflow


@pytest.mark.parametrize("eda_tool", hdlworkflow.supported_eda_tools)
@pytest.mark.parametrize(
    "compile_order",
    [
        "../vhdl_compile_order.json",
        "../verilog_compile_order.json",
        "../mixed_hdl_compile_order.json",
        "../messy_compile_order.json",
        "../vhdl_compile_order.txt",
        "../verilog_compile_order.txt",
        "../mixed_hdl_compile_order.txt",
        "../messy_compile_order.txt",
    ],
)
def test_vhdl_compile_order_json(eda_tool, compile_order, worker_id):
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    # nvc mixed HDL sim is still experimental
    if eda_tool == "nvc" and "mixed" in compile_order:
        pytest.skip()

    # Messy compile contains invalid Vivado files
    if eda_tool == "vivado" and "messy" in compile_order:
        pytest.skip()

    pwd = Path(__file__).parent / ("output_" + worker_id)
    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="top_compile_me",
        compile_order=compile_order,
        path_to_working_directory=str(pwd),
    )
    flow.run()
