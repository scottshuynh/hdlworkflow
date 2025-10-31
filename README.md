[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Regression Tests](https://github.com/scottshuynh/hdlworkflow/actions/workflows/regression-tests.yml/badge.svg)](https://github.com/scottshuynh/hdlworkflow/actions/workflows/regression-tests.yml)
# hdlworkflow
Seamless FPGA workflows.

All HDL simulators follow the same process (analyse, elaborate and simulate) though each uses its own variation of these commands.

Similarly, all HDL synthesis tools follow the same flow (synthesise, place and route, and generate bitstream).

`hdlworkflow` abstracts away these tool-specific commands, making project setup and usage fast and effortless.

## Supported tools
+ [nvc](https://github.com/nickg/nvc)
+ [Riviera-PRO](https://www.aldec.com/en/products/functional_verification/riviera-pro)
+ [Vivado](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vivado.html)

## Supported waveform viewers
+ [gtkwave](https://github.com/gtkwave/gtkwave)

## Simulation compatibility table
Each column shows support simulators and their compatibility with tools listed in the left-most column.

|           | nvc                   | Riviera-PRO                   | Vivado                        |  
| ---       | :---:                 | :---:                         | :---:                         |
| cocotb    | :white_check_mark:    | :white_check_mark:            | :negative_squared_cross_mark: |
| gtkwave   | :white_check_mark:    | :negative_squared_cross_mark: | :negative_squared_cross_mark: |

## Install
`hdlworkflow` is a Python package and can be installed by following the steps below:
```sh
git clone https://github.com/scottshuynh/hdlworkflow.git
cd hdlworkflow
pip install .
```

## How to run
`hdlworkflow` can be run in command line and requires the following arguments:
+ EDA tool of choice.
+ Entity name of top level design.
+ Path to a file containing a list of all files used to simulate the top design file.

A directory with the name of the chosen EDA tool will be created in the directory `hdlworkflow` is run. This directory will contain all output artefacts produced by the tool and waveform viewer.

*Note*: All HDL will be compiled into the *work* library.

---
### nvc
Simulate a top level design named `design_tb` using the `nvc` HDL simulator. All files required to simulate `design_tb` are listed as *absolute* paths line by line in `compile_order.txt`:
```sh
hdlworkflow nvc design_tb compile_order.txt
```

If `design_tb` requires `DATA_WIDTH` and `ADDR_WIDTH` generic declared:
```sh
hdlworkflow nvc design_tb compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4
```

If you want to stop the simulation after 42 us:
```sh
hdlworkflow nvc design_tb compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --stop-time 42 us
```

If a waveform viewer, gtkwave, is required:
```sh
hdlworkflow nvc design_tb compile_order.txt --gui --wave gtkwave
```

If the testbench `design_tb` is a cocotb test module, and the top level design is called `design`:
```sh
hdlworkflow nvc design compile_order_txt --cocotb design_tb
```

Cocotb test modules will be discovered in the same directory that `hdlworkflow` is run.
Adding to `PYTHONPATH` is also supported:
```sh
hdlworkflow nvc design compile_order_txt --cocotb design_tb --pythonpath /abs/path/to/python/module --pythonpath relative/path/to/python/module
```

---
### Riviera-PRO
Simulate a top level design named `design_tb` using the `riviera` HDL simulator. All files required to simulate `design_tb` are listed as *absolute* paths line by line in `compile_order.txt`:
```sh
hdlworkflow riviera design_tb compile_order.txt
```

If `design_tb` requires `DATA_WIDTH` and `ADDR_WIDTH` generic declared:
```sh
hdlworkflow riviera design_tb compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4
```

If you want to stop the simulation after 42 us:
```sh
hdlworkflow riviera design_tb compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --stop-time 42 us
```

If a GUI is required to view waveforms:
```sh
hdlworkflow riviera design_tb compile_order.txt --gui
```

If the testbench `design_tb` is a cocotb test module, and the top level design is called `design`:
```sh
hdlworkflow riviera design compile_order_txt --cocotb design_tb
```

Cocotb test modules will be discovered in the same directory that `hdlworkflow` is run.
Adding to `PYTHONPATH` is also supported:
```sh
hdlworkflow riviera design compile_order_txt --cocotb design_tb --pythonpath /abs/path/to/python/module --pythonpath relative/path/to/python/module
```

---
### Vivado
Simulate a top design named `design_tb` using `Vivado`. All files required to simulate `design_tb` are listed as *absolute* paths line by line in `compile_order.txt`:
```sh
hdlworkflow vivado design_tb compile_order.txt
```

If `design_tb` requires `DATA_WIDTH` and `ADDR_WIDTH` generic declared:
```sh
hdlworkflow vivado design_tb compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4
```

If you want to stop the simulation after 42 us:
```sh
hdlworkflow vivado design_tb compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --stop-time 42 us
```

If a GUI is required to view waveforms:
```sh
hdlworkflow vivado design_tb compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --gui
```

If you want to run synthesis on `design` instead of simulating:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --synth --ooc
```

If you want to run synthesis + implementation on `design` instead of simulating:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --impl
```

If you want to run synthesis + implementation + generate bitstream on `design` instead of simulating:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --bitstream
```

If you want to run an out-of-context (OOC) synthesis on `design` instead of simulating:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --synth --ooc
```

If you want to run an OOC synthesis + implementation on `design` instead of simulating:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --impl --ooc
```

Additionally, if you wanted to set up some clock period constraints for your OOC synthesis + implementation:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --impl --ooc --clk-period-constraint clk_a=10 --clk-period-constraint clk_b=2.000
```

Additionally, if you wanted to set the part number `xczu7ev-ffvc1156-2-e` for your OOC synthesis + implementation:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --impl --ooc --clk-period-constraint clk_a=10 --clk-period-constraint clk_b=2.000 --part xczu7ev-ffvc1156-2-e
```

Additionally, if you wanted to set the board part (`ZCU106`) for your OOC synthesis + implementation:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --impl --ooc --clk-period-constraint clk_a=10 --clk-period-constraint clk_b=2.000 --part xczu7ev-ffvc1156-2-e --board xilinx.com:zcu106:part0:2.6  
```

#### Notes
+ `hdlworkflow` will configure `Vivado` with [Artix-7](https://www.amd.com/en/products/adaptive-socs-and-fpgas/fpga/artix-7.html) as the default part number. Use `--part` and/or `--board` arguments to specify target hardware.
+ When running synthesis, the compile order file should contain all requisite files used to synthesise the design: a list of ordered source, vendor-specific files and constraint files.
+ When running synthesis, `Vivado` will default to use eight logical cores or half of the number of available logical cores, whichever is smaller.

---
### Positional Arguments
#### `eda_tool`
EDA tool to run.

#### `top`
Entity name of top design file.

#### `path_to_compile_order`
Path to a file containing a list of all requisite files for the top design.

### Options
#### `--gui`
(Optional) Opens the EDA tool GUI, if supported.

#### `--wave WAVEFORM_VIEWER`
(Optional) Waveform viewer to run for simulators that do not have native waveform viewers. Defaults to "gtkwave".

#### `--waveform-view-file WAVEFORM_VIEW_FILE`
(Optional) Waveform view file path.

#### `-g GENERIC=VALUE, --generic GENERIC=VALUE`
(Optional) Generics used to elaborate top design file.

#### `--stop-time INTEGER_PERIOD TIME_UNITS`
(Optional) Simulation stops after the specified period.

#### `-v VERBOSE_LEVEL, --verbose VERBOSE_LEVEL`
(Optional) Logging verbosity. Valid values for `VERBOSE_LEVEL` are 0, 1, 2.

#### `--cocotb COCOTB_MODULE`
(Optional) Cocotb test module to run during simulation.

#### `--pythonpath PYTHONPATH`
(Optional) Path to append to `PYTHONPATH` environment variable. Used in cocotb simulations.

#### `--part PART`
(Optional) Part number used to set up `Vivado` project. Only used in `Vivado` workflow.

#### `--board BOARD`
(Optional) Board part used to set up `Vivado` project. Only used in `Vivado` workflow.

#### `--synth`
(Optional) `Vivado` will run synthesis instead of simulation. Only used in `Vivado` workflow.

#### `--impl`
(Optional) `Vivado` will run synthesis + implementation instead of simulation. Only used in `Vivado` workflow.

#### `--bitfile`
(Optional) `Vivado` will run synthesis + implementation + generate bitstream instead of simulation. Only used in `Vivado` workflow.

#### `--ooc`
(Optional) `Vivado` will set synthesis mode to out-of-context. Only used in `Vivado` workflow.

#### `--clk-period-constraint CLK_PORT=PERIOD_NS`
(Optional) Clock period constraint for `Vivado` project. Only used in `Vivado` workflow.