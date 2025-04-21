# hdlworkflow
Streamlining HDL simulations.

Runs the simulation workflow: compile -> elaborate -> simulate.

User must provide:
+ simulator of choice.
+ entity name of top level design.
+ path to a file containing a list of all files used to simulate the top design file.

## Supported simulators
+ nvc

## Supported waveform viewers
+ gtkwave

## Install
```sh
git clone https://github.com/scottshuynh/hdlworkflow.git
cd hdlworkflow
pip install .
```
## How to run
```sh
hdlworkflow [-h] [-w WAVEFORM_VIEWER] [-g GENERIC=VALUE] [-c COCOTB_MODULE] simulator top path_to_compile_order
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