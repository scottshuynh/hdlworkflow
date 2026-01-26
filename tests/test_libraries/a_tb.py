import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


@cocotb.test()
async def test_dut(dut):
    Clock(dut.clk, 1, "ns").start()
    dut.reset.value = 1
    for _ in range(10):
        await RisingEdge(dut.clk)
