import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge

from ctypes import c_uint8

import pytest, random
from pathlib import Path
from hdlworkflow import HdlWorkflow


async def initialise(dut):
    Clock(dut.clk_i, 1, "ns").start()
    dut.rst_i.set(cocotb.handle.Immediate(0))
    dut.ce_i.set(cocotb.handle.Immediate(1))
    await RisingEdge(dut.clk_i)


async def reset(dut):
    dut.rst_i.value = 1
    await RisingEdge(dut.clk_i)
    dut.rst_i.value = 0


async def drive_rand_en(dut):
    while True:
        dut.ce_i.value = random.randint(0, 1)
        await RisingEdge(dut.clk_i)


async def verify_count(dut, num_outputs: int):
    ADJUST = dut.ADJUST.value
    IS_DECREMENT = dut.IS_DECREMENT.value
    await FallingEdge(dut.clk_i)
    expected = c_uint8(dut.count_o.value.to_unsigned())

    for idx in range(num_outputs):
        if IS_DECREMENT:
            expected.value -= ADJUST
        else:
            expected.value += ADJUST

        while not dut.count_vld_o.value:
            await FallingEdge(dut.clk_i)

        assert expected.value == dut.count_o.value.to_unsigned()
        await FallingEdge(dut.clk_i)


if cocotb.is_simulation:

    @cocotb.test()
    @cocotb.parametrize(
        rand_clk_en=[False] + [True] * (1 if "rand_clk_en" in cocotb.plusargs else 0),
        num_outputs=[
            int(cocotb.plusargs.get("num_outputs", 42)),
        ],
    )
    async def test_counter(dut, rand_clk_en: bool, num_outputs: int):
        await initialise(dut)
        await reset(dut)
        if rand_clk_en:
            cocotb.start_soon(drive_rand_en(dut))

        await verify_count(dut, num_outputs)


@pytest.mark.parametrize("eda_tool", ["nvc"])
@pytest.mark.parametrize("adjust", [3, 11])
@pytest.mark.parametrize("is_decrement", [True, False])
@pytest.mark.parametrize("test", ["rand_clk_en"])
@pytest.mark.parametrize("num_outputs", [128])
@pytest.mark.skipif(
    int(cocotb.__version__.split(".", 1)[0]) < 2,
    reason="cocotb.parametrize decorator only supprted in v2.0.0 or higher",
)
def test_plusargs(eda_tool, adjust, is_decrement, test, num_outputs):
    pwd = Path(__file__).parent

    flow = HdlWorkflow(
        eda_tool=eda_tool,
        top="counter",
        path_to_compile_order="compile_order.json",
        path_to_working_directory=pwd,
        generic=[f"{adjust=}", f"{is_decrement=}"],
        cocotb=str(Path(__file__).stem),
        plusargs=[f"{test}", f"{num_outputs=}"],
        pythonpaths=[pwd],
    )
    flow.run()
