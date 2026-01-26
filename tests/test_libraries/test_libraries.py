import pytest
from pathlib import Path
from hdlworkflow import HdlWorkflow


@pytest.mark.parametrize("eda_tool", ["nvc"])
def test_libraries(eda_tool):
    pwd = Path(__file__).parent
    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="a_tb",
        path_to_compile_order="compile_order.json",
        path_to_working_directory=pwd,
    )
    flow.run()


@pytest.mark.parametrize("eda_tool", ["nvc"])
def test_libraries_cocotb(eda_tool):
    pwd = Path(__file__).parent
    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="a_tb",
        path_to_compile_order="compile_order.json",
        path_to_working_directory=pwd,
        pythonpaths=[pwd],
        cocotb="a_tb",
    )
    flow.run()
