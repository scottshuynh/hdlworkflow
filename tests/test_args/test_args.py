import logging, os, pytest
from pathlib import Path
from shutil import which

import hdlworkflow
from hdlworkflow import HdlWorkflow
from hdlworkflow.logging import set_log_level, LoggingLevel

# logger = logging.getLogger("hdlworkflow")
set_log_level(LoggingLevel(2))


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_nvc_analyse_args(data_w, depth, worker_id):
    eda_tool = "nvc"
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
        pythonpaths=[str(pwd.parent)],
        analyse_args=["--relaxed", "-Werror"],
    )
    flow.run()


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_nvc_elaborate_args(data_w, depth, worker_id):
    eda_tool = "nvc"
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
        elaborate_args=["-O3", "-V"],
    )
    flow.run()


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_nvc_run_args(data_w, depth, worker_id):
    eda_tool = "nvc"
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
        run_args=["--stats"],
    )
    flow.run()


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_nvc_analyse_args_cli(data_w, depth, worker_id):
    eda_tool = "nvc"
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
        "--analyse_args=--relaxed",
        "--analyse_args=-Werror",
    ]

    hdlworkflow.cli.main(argv)


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_nvc_elaborate_args_cli(data_w, depth, worker_id):
    eda_tool = "nvc"
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
        "--elaborate_args=-O3",
        "--elaborate_args=-V",
    ]

    hdlworkflow.cli.main(argv)


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_nvc_run_args_cli(data_w, depth, worker_id):
    eda_tool = "nvc"
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
        "--run_args=--stats",
    ]

    hdlworkflow.cli.main(argv)


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_riviera_analyse_args(data_w, depth, worker_id):
    eda_tool = "riviera"
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
        pythonpaths=[str(pwd.parent)],
        analyse_args=["-quiet", "-O3"],
    )
    flow.run()


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_riviera_elaborate_args(data_w, depth, worker_id):
    eda_tool = "riviera"
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
        elaborate_args=["-relax"],
    )
    flow.run()


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_riviera_run_args(data_w, depth, worker_id):
    eda_tool = "riviera"
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
        run_args=["-l fifo_sync_tb.log"],
    )
    flow.run()


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_riviera_analyse_args_cli(data_w, depth, worker_id):
    eda_tool = "riviera"
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
        "--analyse_args=-quiet",
        "--analyse_args=-O3",
    ]

    hdlworkflow.cli.main(argv)


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_riviera_elaborate_args_cli(data_w, depth, worker_id):
    eda_tool = "riviera"
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
        "--elaborate_args=-relax",
    ]

    hdlworkflow.cli.main(argv)


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_riviera_run_args_cli(data_w, depth, worker_id):
    eda_tool = "riviera"
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
        "--run_args=-l fifo_sync_tb.log",
    ]

    hdlworkflow.cli.main(argv)


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_vivado_analyse_args(data_w, depth, worker_id):
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
        pythonpaths=[str(pwd.parent)],
        analyse_args=["-relax"],
    )
    flow.run()


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_vivado_elaborate_args(data_w, depth, worker_id):
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
        elaborate_args=["--O3"],
    )
    flow.run()


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_vivado_run_args(data_w, depth, worker_id):
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
        run_args=["-log fifo_sync_tb.log"],
    )
    flow.run()


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_vivado_analyse_args_cli(data_w, depth, worker_id):
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
        "--analyse_args=-relax",
    ]

    hdlworkflow.cli.main(argv)


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_vivado_elaborate_args_cli(data_w, depth, worker_id):
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
        "--elaborate_args=--O3",
    ]

    hdlworkflow.cli.main(argv)


@pytest.mark.parametrize("data_w", [16])
@pytest.mark.parametrize("depth", [128])
def test_vivado_run_args_cli(data_w, depth, worker_id):
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
        "--run_args=-log fifo_sync_tb.log",
    ]

    hdlworkflow.cli.main(argv)
