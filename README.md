[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Regression Tests](https://github.com/scottshuynh/hdlworkflow/actions/workflows/regression-tests.yml/badge.svg)](https://github.com/scottshuynh/hdlworkflow/actions/workflows/regression-tests.yml)
[![PyPI downloads](https://img.shields.io/pypi/dm/hdlworkflow?label=PyPI%20downloads)](https://pypi.org/p/hdlworkflow)
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
The table below shows supported simulators and their compatibility with tools listed in the left-most column.

|           | nvc                   | Riviera-PRO                   | Vivado                        |  
| ---       | :---:                 | :---:                         | :---:                         |
| cocotb    | :white_check_mark:    | :white_check_mark:            | :negative_squared_cross_mark: |
| gtkwave   | :white_check_mark:    | :negative_squared_cross_mark: | :negative_squared_cross_mark: |

## Install
`hdlworkflow` is a Python package and can be installed using pip:
```sh
pip install hdlworkflow
```

If you want to install the development version of `hdlworkflow`:
```sh
pip install git+https://github.com/scottshuynh/hdlworkflow@main
```

## How to run
`hdlworkflow` can be run from the command line and requires the following arguments:
+ EDA tool of choice.
+ Entity name of top level design.
+ Path to a file listing all required source files for the top level design.

A directory with the name of the chosen EDA tool will be created in the directory `hdlworkflow` is run. This directory will contain all output artefacts produced by the EDA tool.

Some examples of `hdlworkflow` usage can be found below.

> [!NOTE]
> By default, all HDL will be compiled into the *work* library.

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

If stopping the simulation after 42 us is required:
```sh
hdlworkflow nvc design_tb compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --stop-time 42 us
```

If a waveform viewer, gtkwave, is required:
```sh
hdlworkflow nvc design_tb compile_order.txt --gui --wave gtkwave
```
> [!NOTE]
> A new waveform view file will be generated automatically, overwriting any previously generated file.

If gtkwave is required with an existing waveform view file:
```sh
hdlworkflow nvc design_tb compile_order.txt --gui --wave gtkwave --waveform-view-file path/to/waveform_view_file.gtkw
```

If the testbench `design_tb` is a cocotb test module, and the top level design is called `design`:
```sh
hdlworkflow nvc design compile_order.txt --cocotb design_tb
```

Cocotb test modules will be discovered in the same directory that `hdlworkflow` is run.
Adding to `PYTHONPATH` is also supported:
```sh
hdlworkflow nvc design compile_order.txt --cocotb design_tb --pythonpath /abs/path/to/python/module --pythonpath relative/path/to/python/module
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

If stopping the simulation after 42 us is required:
```sh
hdlworkflow riviera design_tb compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --stop-time 42 us
```

If a GUI is required to view waveforms:
```sh
hdlworkflow riviera design_tb compile_order.txt --gui
```
> [!NOTE]
> A new waveform view file will be generated automatically, overwriting any previously generated file.

If a GUI is required with an existing waveform view file:
```sh
hdlworkflow riviera design_tb compile_order.txt --gui --waveform-view-file path/to/waveform_view_file.awc
```

If the testbench `design_tb` is a cocotb test module, and the top level design is called `design`:
```sh
hdlworkflow riviera design compile_order.txt --cocotb design_tb
```

Cocotb test modules will be discovered in the same directory that `hdlworkflow` is run.
Adding to `PYTHONPATH` is also supported:
```sh
hdlworkflow riviera design compile_order.txt --cocotb design_tb --pythonpath /abs/path/to/python/module --pythonpath relative/path/to/python/module
```

If the path to libstdc++ is required to resolve [GLIBCXX_3.4.XX not found](https://docs.cocotb.org/en/development/troubleshooting.html#glibcxx-3-4-xx-not-found):
```sh
hdlworkflow riviera design compile_order.txt --cocotb design_tb --libstdcpp /abs/path/to/libstdc++.so.6
```

If the path to glbl.v is required to resolve [Unresolved hierarchical reference to"glbl.GSR"](https://www.aldec.com/en/support/resources/documentation/faq/1172):
```sh
hdlworkflow riviera design_tb compile_order.txt --glbl /abs/path/to/glbl.v
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

If stopping the simulation after 42 us is required:
```sh
hdlworkflow vivado design_tb compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --stop-time 42 us
```

If a GUI is required to view waveforms:
```sh
hdlworkflow vivado design_tb compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --gui
```
> [!NOTE]
> A new waveform view file will be generated automatically, overwriting any previously generated file.

If a GUI is required with an existing waveform configuration file:
```sh
hdlworkflow vivado design_tb compile_order.txt --gui --waveform-view-file path/to/waveform_view_file.wcfg
```

If synthesis of `design` is required instead of simulating:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --synth
```

If synthesis + implementation of `design` is required instead of simulating:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --impl
```

If synthesis + implementation + generate bitstream of `design` is required instead of simulating:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --bitstream
```

If an out-of-context (OOC) synthesis of `design` is required instead of simulating:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --synth --ooc
```

If an OOC synthesis + implementation of `design` is required instead of simulating:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --impl --ooc
```

Additionally, if a clock period constraints on clock port `clk_a` for OOC synthesis + implementation is required:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --impl --ooc --clk-period-constraint clk_a=10 --clk-period-constraint clk_b=2.000
```

Additionally, if the part number `xczu7ev-ffvc1156-2-e` for OOC synthesis + implementation is required:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --impl --ooc --clk-period-constraint clk_a=10 --clk-period-constraint clk_b=2.000 --part xczu7ev-ffvc1156-2-e
```

Additionally, if the board part (`ZCU106`) for OOC synthesis + implementation is required:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --impl --ooc --clk-period-constraint clk_a=10 --clk-period-constraint clk_b=2.000 --part xczu7ev-ffvc1156-2-e --board xilinx.com:zcu106:part0:2.6  
```
> [!NOTE]
> + `hdlworkflow` will configure `Vivado` with [Artix-7](https://www.amd.com/en/products/adaptive-socs-and-fpgas/fpga/artix-7.html) as the default part number. Use `--part` and/or `--board` arguments to specify target hardware.
> + When running synthesis, the compile order file should contain all requisite files used to synthesise the design: a list of ordered source files, vendor-specific files and constraint files.
> + When running synthesis, `Vivado` will default to use eight logical cores or half of the number of available logical cores, whichever is smaller.

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

#### `--libstdcpp LIBSTDC++`
(Optional) Path to libstdc++ shared object. Used in cocotb simulations to resolve [GLIBCXX_3.4.XX not found](https://docs.cocotb.org/en/development/troubleshooting.html#glibcxx-3-4-xx-not-found).

#### `--glbl GLBL.V`
(Optional) Path to glbl.v. Used in simulations that use Xilinx XPM library. Resolves [Unresolved hierarchical reference to"glbl.GSR"](https://www.aldec.com/en/support/resources/documentation/faq/1172).

#### `--work DEFAULT_LIB`
(Optional) Name of the default library.

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