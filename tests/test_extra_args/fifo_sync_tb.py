import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge
import random

PERIOD_NS = 1


async def initialise(dut, num_clock_cycles: int):
    dut.rst_i.value = 1
    dut.wr_en_i.value = 0
    dut.wr_data_i.value = 0
    dut.rd_en_i.value = 0
    await RisingEdge(dut.clk_i)

    for _ in range(num_clock_cycles):
        await RisingEdge(dut.clk_i)

    dut.rst_i.value = 0


def generate_random_datas(num_writes: int, data_w: int) -> list[int]:
    return [random.randint(-(2 ** (data_w - 1)), 2 ** (data_w - 1) - 1) for _ in range(num_writes)]


async def drive_random_writes(dut, write_datas: list[int]):
    for write_data in write_datas:
        dut.wr_en_i.value = 1
        dut.wr_data_i.value = write_data
        await RisingEdge(dut.clk_i)

    dut.wr_en_i.value = 0
    await RisingEdge(dut.clk_i)

    return write_datas


async def read_data(dut, num_reads: int):
    num_completed_reads = 0
    while num_completed_reads < num_reads:
        dut.rd_en_i.value = 1
        await FallingEdge(dut.clk_i)
        if not dut.empty_o.value:
            num_completed_reads += 1
        await RisingEdge(dut.clk_i)

    dut.rd_en_i.value = 0
    await RisingEdge(dut.clk_i)


async def read_to_verify_write_datas(dut, write_datas: list[int]):
    cocotb.start_soon(read_data(dut, len(write_datas)))
    read_count = 0
    while read_count < len(write_datas):
        await FallingEdge(dut.clk_i)
        if dut.rd_data_vld_o.value == 1:
            assert dut.rd_data_o.value.signed_integer == write_datas[read_count]
            read_count += 1


@cocotb.test()
async def test_random_reads_after_writes(dut):
    """Writes random data, and then verifies reads."""
    cocotb.start_soon(Clock(dut.clk_i, PERIOD_NS, "ns").start())
    await initialise(dut, random.randint(1, 10))

    num_writes = min(10, dut.DEPTH.value)
    data_w = dut.DATA_W.value
    write_datas = generate_random_datas(num_writes, data_w)

    write_datas = await drive_random_writes(dut, write_datas)

    await read_to_verify_write_datas(dut, write_datas)

    for _ in range(num_writes):
        await RisingEdge(dut.clk_i)


@cocotb.test()
async def test_random_writes_and_reads(dut):
    """Kicks of read and write tasks simultaneously."""
    cocotb.start_soon(Clock(dut.clk_i, PERIOD_NS, "ns").start())
    await initialise(dut, random.randint(1, 10))

    num_writes = dut.DEPTH.value
    data_w = dut.DATA_W.value
    write_datas = generate_random_datas(num_writes, data_w)
    write_task = cocotb.start_soon(drive_random_writes(dut, write_datas))
    read_task = cocotb.start_soon(read_to_verify_write_datas(dut, write_datas))

    while not read_task.done():
        await RisingEdge(dut.clk_i)
