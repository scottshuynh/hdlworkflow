import pytest
from pathlib import Path
from hdlworkflow import HdlWorkflow


def test_libraries0():
    pwd = Path(__file__).parent
    flow = HdlWorkflow(
        eda_tool="nvc",
        top="a",
        path_to_compile_order="compile_order.json",
        path_to_working_directory=pwd,
    )
    flow.run()
