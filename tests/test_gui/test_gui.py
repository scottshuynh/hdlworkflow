import os
import pytest
from pathlib import Path
from shutil import which

import hdlworkflow
from hdlworkflow import HdlWorkflow


@pytest.mark.parametrize("dump_file", ["", "fifo_dump.fst"])
@pytest.mark.parametrize("view_file", ["", "fifo_view.gtkw"])
@pytest.mark.gui
@pytest.mark.nvc
def test_nvc_gtkwave(dump_file, view_file):
    if not which("nvc"):
        pytest.skip("nvc is not installed. Skipping...")
    pwd = Path(__file__).parent / "build"
    pwd.mkdir(parents=True, exist_ok=True)

    flow = HdlWorkflow(
        eda_tool="nvc",
        top="fifo_sync_tb",
        compile_order="../compile_order.json",
        path_to_working_directory=pwd,
        generics=["data_w=16", "depth=128"],
        gui=True,
        waveform_dump_file=dump_file,
        waveform_view_file=view_file,
    )
    flow.run()


@pytest.mark.parametrize("dump_file", ["", "fifo_dump.fst"])
@pytest.mark.parametrize("view_file", ["", "fifo_view.gtkw"])
@pytest.mark.gui
@pytest.mark.nvc
def test_nvc_gtkwave_cli(dump_file, view_file):
    if not which("nvc"):
        pytest.skip("nvc is not installed. Skipping...")
    pwd = Path(__file__).parent / "build"
    pwd.mkdir(parents=True, exist_ok=True)
    os.chdir(pwd)

    argv = [
        "nvc",
        "fifo_sync_tb",
        "../compile_order.json",
        "-g",
        "data_w=16",
        "-g",
        "depth=128",
        "--gui",
    ]
    if dump_file:
        argv.append(f"--waveform-dump-file={dump_file}")
    if view_file:
        argv.append(f"--waveform-view-file={view_file}")
    hdlworkflow.cli.main(argv)


@pytest.mark.parametrize("dump_file", ["", "fifo_dump.fst"])
@pytest.mark.parametrize("view_file", ["", "fifo_view.ron"])
@pytest.mark.gui
@pytest.mark.nvc
def test_nvc_surfer(dump_file, view_file):
    if not which("nvc"):
        pytest.skip("nvc is not installed. Skipping...")
    pwd = Path(__file__).parent / "build"
    pwd.mkdir(parents=True, exist_ok=True)

    flow = HdlWorkflow(
        eda_tool="nvc",
        top="fifo_sync_tb",
        compile_order="../compile_order.json",
        path_to_working_directory=pwd,
        generics=["data_w=16", "depth=128"],
        gui=True,
        wave="surfer",
        waveform_dump_file=dump_file,
        waveform_view_file=view_file,
    )
    flow.run()


@pytest.mark.parametrize("dump_file", ["", "fifo_dump.fst"])
@pytest.mark.parametrize("view_file", ["", "fifo_view.ron"])
@pytest.mark.gui
@pytest.mark.nvc
def test_nvc_surfer_cli(dump_file, view_file):
    if not which("nvc"):
        pytest.skip("nvc is not installed. Skipping...")
    pwd = Path(__file__).parent / "build"
    pwd.mkdir(parents=True, exist_ok=True)
    os.chdir(pwd)

    argv = [
        "nvc",
        "fifo_sync_tb",
        "../compile_order.json",
        "-g",
        "data_w=16",
        "-g",
        "depth=128",
        "--gui",
        "--wave",
        "surfer",
    ]
    if dump_file:
        argv.append(f"--waveform-dump-file={dump_file}")
    if view_file:
        argv.append(f"--waveform-view-file={view_file}")
    hdlworkflow.cli.main(argv)


@pytest.mark.parametrize("dump_file", ["", "fifo_dump.wdb"])
@pytest.mark.parametrize("view_file", ["", "fifo_view.wcfg"])
@pytest.mark.gui
@pytest.mark.vivado
def test_vivado_gui(dump_file, view_file):
    if not which("vivado"):
        pytest.skip("vivado is not installed. Skipping...")
    pwd = Path(__file__).parent / "build"
    pwd.mkdir(parents=True, exist_ok=True)

    flow = HdlWorkflow(
        eda_tool="vivado",
        top="fifo_sync_tb",
        compile_order="../compile_order.json",
        path_to_working_directory=pwd,
        generics=["data_w=16", "depth=128"],
        gui=True,
        waveform_dump_file=dump_file,
        waveform_view_file=view_file,
    )
    flow.run()


@pytest.mark.parametrize("dump_file", ["", "fifo_dump.wdb"])
@pytest.mark.parametrize("view_file", ["", "fifo_view.wcfg"])
@pytest.mark.gui
@pytest.mark.vivado
def test_vivado_gui_cli(dump_file, view_file):
    if not which("vivado"):
        pytest.skip("vivado is not installed. Skipping...")
    pwd = Path(__file__).parent / "build"
    pwd.mkdir(parents=True, exist_ok=True)
    os.chdir(pwd)

    argv = [
        "vivado",
        "fifo_sync_tb",
        "../compile_order.json",
        "-g",
        "data_w=16",
        "-g",
        "depth=128",
        "--gui",
    ]
    if dump_file:
        argv.append(f"--waveform-dump-file={dump_file}")
    if view_file:
        argv.append(f"--waveform-view-file={view_file}")
    hdlworkflow.cli.main(argv)


@pytest.mark.parametrize("dump_file", ["", "fifo_dump.asdb"])
@pytest.mark.parametrize("view_file", ["", "fifo_view.awc"])
@pytest.mark.gui
@pytest.mark.riviera
def test_riviera_gui(dump_file, view_file):
    if not which("riviera"):
        pytest.skip("riviera is not installed. Skipping...")
    pwd = Path(__file__).parent / "build"
    pwd.mkdir(parents=True, exist_ok=True)

    flow = HdlWorkflow(
        eda_tool="riviera",
        top="fifo_sync_tb",
        compile_order="../compile_order.json",
        path_to_working_directory=pwd,
        generics=["data_w=16", "depth=128"],
        gui=True,
        waveform_dump_file=dump_file,
        waveform_view_file=view_file,
    )
    flow.run()


@pytest.mark.parametrize("dump_file", ["", "fifo_dump.asdb"])
@pytest.mark.parametrize("view_file", ["", "fifo_view.awc"])
@pytest.mark.gui
@pytest.mark.riviera
def test_riviera_gui_cli(dump_file, view_file):
    if not which("riviera"):
        pytest.skip("riviera is not installed. Skipping...")
    pwd = Path(__file__).parent / "build"
    pwd.mkdir(parents=True, exist_ok=True)
    os.chdir(pwd)

    argv = [
        "riviera",
        "fifo_sync_tb",
        "../compile_order.json",
        "-g",
        "data_w=16",
        "-g",
        "depth=128",
        "--gui",
    ]
    if dump_file:
        argv.append(f"--waveform-dump-file={dump_file}")
    if view_file:
        argv.append(f"--waveform-view-file={view_file}")
    hdlworkflow.cli.main(argv)
