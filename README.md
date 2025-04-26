# hdlworkflow
Streamlining HDL simulations.

Runs the simulation workflow in one command: "compile -> elaborate -> simulate".

A `sim` folder will be created in the directory `hdlworkflow` is run. `sim` will contain all output artefacts produced by the simulator and waveform viewer.

## Supported simulators
+ nvc

## Supported waveform viewers
+ gtkwave

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

### Positional Arguments
#### `simulator`
Specified HDL simulator to run.

#### `top`
Specified top design file to simulate.

#### `path_to_compile_order`
Specified path to a file containing a list of all files used to simulate the top design file.

### Options
#### `-w WAVEFORM_VIEWER, --wave WAVEFORM_VIEWER`
(Optional) Specified waveform viewer to run at the end of the simulation.

#### `-g GENERIC=VALUE, --generic GENERIC=VALUE`
(Optional) Specified generics used to elaborate top design file.

#### `-c COCOTB_MODULE, --cocotb COCOTB_MODULE`
(Optional) Specified cocotb test module to run during simulation.

#### `-p PYTHONPATH, --pythonpath PYTHONPATH`
(Optional) Path to append to `PYTHONPATH` environment variable. Used in cocotb simulations.