[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Regression Tests](https://github.com/scottshuynh/hdlworkflow/actions/workflows/regression-tests.yml/badge.svg)](https://github.com/scottshuynh/hdlworkflow/actions/workflows/regression-tests.yml)
# hdlworkflow
All HDL simulators follow the same process (analyse, elaborate and simulate) though each uses its own variation of these commands. `hdlworkflow` abstracts away the simulator-specific commands to simplify simulation project creation.

## Supported tools
+ [nvc](https://github.com/nickg/nvc)
+ [Riviera-PRO](https://www.aldec.com/en/products/functional_verification/riviera-pro)
+ [Vivado](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vivado.html)

## Supported waveform viewers
+ [gtkwave](https://github.com/gtkwave/gtkwave)

## Compatibility table
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
+ Simulator of choice.
+ Entity name of top level design.
+ Path to a file containing a list of all files used to simulate the top design file.

A directory with the name of the chosen simulator will be created in the directory `hdlworkflow` is run. This directory will contain all output artefacts produced by the simulator and waveform viewer.

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

If a waveform viewer, gtkwave, is required:
```sh
hdlworkflow nvc design_tb compile_order.txt --wave gtkwave
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

If a GUI is required to view waveforms:
```sh
hdlworkflow riviera design_tb compile_order.txt --wave riviera
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

If you want to run an out-of-context (OOC) synthesis on `design` instead of simulating:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --synth
```

Additionally, if you wanted to set the part number `xczu7ev-ffvc1156-2-e` for your OOC synthesis:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --synth --part xczu7ev-ffvc1156-2-e
```

Additionally, if you wanted to set the board part (`ZCU106`) for your OOC synthesis:
```sh
hdlworkflow vivado design compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4 --synth --part xczu7ev-ffvc1156-2-e --board xilinx.com:zcu106:part0:2.6  
```

#### Notes
+ `hdlworkflow` will configure `Vivado` synthesis as [out-of-context](https://docs.amd.com/r/en-US/ug949-vivado-design-methodology/Out-of-Context-Synthesis).
+ A clock constraint of 500 MHz is set up by default to constrain the clock port `clk_i`.
+ `hdlworkflow` will configure `Vivado` with [Artix-7](https://www.amd.com/en/products/adaptive-socs-and-fpgas/fpga/artix-7.html) as the default part number. Use `--part` and/or `--board` positional arguments to specify target hardware.
+ When running synthesis, `Vivado` will default to use eight logical cores or half of the number of available logical cores, whichever is smaller.
+ `Vivado` will use its native waveform viewer instead of third party waveform viewers. 
+ `Vivado` is *not* compatible with `cocotb`. `hdlworkflow` will raise an error if attempting to use `cocotb` with `Vivado`.

---
### Positional Arguments
#### `simulator`
HDL simulator to run.

#### `top`
Entity name of top design file to simulate.

#### `path_to_compile_order`
Path to a file containing a list of all files used to simulate the top design file.

### Options
#### `--wave WAVEFORM_VIEWER`
(Optional) Waveform viewer to run at the end of the simulation.

#### `-g GENERIC=VALUE, --generic GENERIC=VALUE`
(Optional) Generics used to elaborate top design file.

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