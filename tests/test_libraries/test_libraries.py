import pytest
from pathlib import Path
from shutil import which

import hdlworkflow
from hdlworkflow import HdlWorkflow


@pytest.mark.parametrize("eda_tool", hdlworkflow.supported_eda_tools)
def test_libraries(eda_tool):
    pwd = Path(__file__).parent

    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="a_tb",
        path_to_compile_order="compile_order.json",
        path_to_working_directory=pwd,
    )
    flow.run()


@pytest.mark.parametrize("eda_tool", hdlworkflow.supported_eda_tools)
def test_libraries_cocotb(eda_tool):
    pwd = Path(__file__).parent

    if eda_tool == "vivado":
        pytest.skip("Vivado does not support cocotb. Skipping...")
    if not which(eda_tool):
        pytest.skip(f"{eda_tool} is not installed. Skipping...")

    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="a_tb",
        path_to_compile_order="compile_order.json",
        path_to_working_directory=pwd,
        pythonpaths=[pwd],
        cocotb="a_tb",
    )
    flow.run()
