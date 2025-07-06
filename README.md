# hdlworkflow
Streamlining HDL simulations.

Runs the simulation workflow in one command: "analyse, elaborate, simulate".

A directory with the name of the chosen simulator will be created in the directory `hdlworkflow` is run. This directory will contain all output artefacts produced by the simulator and waveform viewer.

## Supported tools
+ [nvc](https://github.com/nickg/nvc)
+ [vivado](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vivado.html)

## Supported waveform viewers
+ [gtkwave](https://github.com/gtkwave/gtkwave)

## Compatibility table
|           | nvc                   | Vivado                        |  
| ---       | :---:                 | :---:                         |
| cocotb    | :white_check_mark:    | :negative_squared_cross_mark: |
| gtkwave   | :white_check_mark:    | :negative_squared_cross_mark: |

## Install
`hdlworkflow` is a [Python](https://www.python.org/) package and can be installed by following the steps below:
```sh
git clone https://github.com/scottshuynh/hdlworkflow.git
cd hdlworkflow
pip install .
```

## How to run
`hdlworkflow` requires the following arguments:
+ Simulator of choice.
+ Entity name of top level design.
+ Path to a file containing a list of all files used to simulate the top design file.

---
### nvc
Simulate a top level design named `design_tb` using the `nvc` HDL simulator. All files required to simulate `design_tb` are listed as *absolute* paths line by line in `compile_order.txt`:
```sh
hdlworkflow nvc design_tb compile_order.txt
```

If `design_tb` needed requires `DATA_WIDTH` and `ADDR_WIDTH` generic declared:
```sh
hdlworkflow nvc design_tb compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4
```

If a waveform viewer, gtkwave, is required:
```sh
hdlworkflow nvc design_tb compile_order.txt -w gtkwave
```

If the testbench `design_tb` is a cocotb test module, and the top level design is called `design`:
```sh
hdlworkflow nvc design compile_order_txt -c design_tb
```

Cocotb test modules will be discovered in the same directory that `hdlworkflow` is run.
Alternatively, if adding to `PYTHONPATH` is required for cocotb:
```sh
hdlworkflow nvc design compile_order_txt -c design_tb -p /abs/path/to/python/module -p relative/path/to/python/module
```

---
### Vivado
Create a project with a top level design named `design_tb` using `Vivado`. All files required to synthesise/simulate `design_tb` are listed as *absolute* paths line by line in `compile_order.txt`:
```sh
hdlworkflow vivado design_tb compile_order.txt
```

If `design_tb` needed requires `DATA_WIDTH` and `ADDR_WIDTH` generic declared:
```sh
hdlworkflow vivado design_tb compile_order.txt -g DATA_WIDTH=8 -g ADDR_WIDTH=4
```

#### Notes
+ `hdlworkflow` will open `Vivado` GUI and run in [project mode](https://docs.amd.com/r/en-US/ug892-vivado-design-flows-overview/Project-Mode). GUI-less mode not yet implemented.
+ `hdlworkflow` will configure `Vivado` synthesis as [out-of-context](https://docs.amd.com/r/en-US/ug949-vivado-design-methodology/Out-of-Context-Synthesis).
+ A clock constraint of 500MHz is set up by default to constrain a clock port `clk_i`.
+ `hdlworkflow` will configure `Vivado` with [Artix-7](https://www.amd.com/en/products/adaptive-socs-and-fpgas/fpga/artix-7.html) as the default part number. Use `--part` and/or `--board` positional arguments to specify target hardware.
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

#### `--cocotb COCOTB_MODULE`
(Optional) Cocotb test module to run during simulation.

#### `--pythonpath PYTHONPATH`
(Optional) Path to append to `PYTHONPATH` environment variable. Used in cocotb simulations.

#### `--part PART`
(Optional) Part number used to set up `Vivado` project. Only used in `Vivado` workflow.

#### `--board BOARD`
(Optional) Board part used to set up `Vivado` project. Only used in `Vivado` workflow.