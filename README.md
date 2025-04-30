# hdlworkflow
Streamlining HDL simulations.

Runs the simulation workflow in one command: "analyse, elaborate, simulate".

A directory with the name of the chosen simulator will be created in the directory `hdlworkflow` is run. This directory will contain all output artefacts produced by the simulator and waveform viewer.

## Supported simulators
+ nvc
+ vivado

## Supported waveform viewers
+ gtkwave

## Compatibility table
|     | nvc | Vivado |  
| --- | :---: | :---: |
| cocotb | :white_check_mark: | :negative_squared_cross_mark: |
| gtkwave | :white_check_mark: | :negative_squared_cross_mark: |

## Install
`hdlworkflow` is a Python package and can be installed by following the steps below:
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

### nvc
Simulate a top level design named `design_tb` using the `nvc` HDL simulator. All files required to simulate `design_tb` are listed as paths line by line in `compile_order.txt`:
```sh
hdlworkflow nvc design_tb compile_order.txt
```

If `design_tb` needed requires `DATA_WIDTH` generic declared:
```sh
hdlworkflow nvc design_tb compile_order.txt -g DATA_WIDTH=8
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

### Vivado
Create a project with a top level design named `design_tb` using `Vivado`. All files required to simulate `design_tb` are listed as paths line by line in `compile_order.txt`:
```sh
hdlworkflow vivado design_tb compile_order.txt
```

If `design_tb` needed requires `DATA_WIDTH` generic declared:
```sh
hdlworkflow vivado design_tb compile_order.txt -g DATA_WIDTH=8
```
+ **Note** `Vivado` will open a GUI and run in [project mode](https://docs.amd.com/r/en-US/ug892-vivado-design-flows-overview/Project-Mode). GUI-less mode not yet implemented.
+ **Note** `Vivado` synthesis will be configured as [out-of-context](https://docs.amd.com/r/en-US/ug949-vivado-design-methodology/Out-of-Context-Synthesis).
+ **Note** `Vivado` will set the [Artix-7](https://www.amd.com/en/products/adaptive-socs-and-fpgas/fpga/artix-7.html) as the default part number. Option for target part number not yet implemented.
+ **Note** `Vivado` will use its native waveform viewer instead of third party waveform viewers. 
+ **Note** `Vivado` is *not* compatible with `cocotb`. `hdlworkflow` will raise an error if attempting to use `cocotb` with `Vivado`.

### Positional Arguments
#### `simulator`
HDL simulator to run.

#### `top`
Entity name of top design file to simulate.

#### `path_to_compile_order`
Path to a file containing a list of all files used to simulate the top design file.

### Options
#### `-w WAVEFORM_VIEWER, --wave WAVEFORM_VIEWER`
(Optional) Waveform viewer to run at the end of the simulation.

#### `-g GENERIC=VALUE, --generic GENERIC=VALUE`
(Optional) Generics used to elaborate top design file.

#### `-c COCOTB_MODULE, --cocotb COCOTB_MODULE`
(Optional) Cocotb test module to run during simulation.

#### `-p PYTHONPATH, --pythonpath PYTHONPATH`
(Optional) Path to append to `PYTHONPATH` environment variable. Used in cocotb simulations.