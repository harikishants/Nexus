# Nexus

Nexus is a two-phase framework that integrates safety verification of neural network-controlled cyber-physical systems (CPS) with mixed precision fixed-point quantization of neural network (NN) controllers.

- **Input**: Plant initial conditions, dynamics, safety properties, NN controller, and error.
- **Output**: Safe implementation of NN controller, which can be compiled by Xilinx Vitis HLS.

## Pre-requisite Software Packages

**Note**: Nexus is implemented on top of POLAR and Aster. Make sure to follow the installation instructions in the `README-POLAR` and `README-Aster` files of this project before proceeding with Nexus.

- **Download POLAR**
  ```bash
  git clone https://github.com/ChaoHuang2018/POLAR_Tool
  ```

- **Download Aster**
  ```bash
  git clone https://github.com/dlohar/Aster/tree/Nexus
  ```
- **Download Xilinx** from [Xilinx’s Vitis HLS (version v2023.2)](https://www.xilinx.com)

### Directory Setup

1. Rename the `POLAR_Tool/` directory to `POLAR/` and place it inside `Nexus/`.
2. Place the `Aster/` directory inside `Nexus/`.

The folder structure should look like this:
Nexus/POLAR/...
Nexus/Aster/...

### Applying modifications

Replace files in POLAR/ from modifications/ as shown below
```bash
# Assuming that you are inside Nexus/
cp modifications/Continous.cpp POLAR/flowstar/flowstar-toolbox/
cp modifications/Continous.h POLAR/flowstar/flowstar-toolbox/
```

### Compiling POLAR
```bash
# Assuming that you are inside Nexus/)
cd POLAR/POLAR
make
cd ../flowstar/flowstar-toolbox/
make
```

## Running Nexus

**NOTE:** We provide all our specfications of our benchmarks here: `input/`. For running the scripts, we assume that you are in the Nexus/

e.g, running Nexus on `InvPendulum`:

### Running whole pipeline ###
```bash
./scripts/run_Nexus.sh input/spec-InvPendulum.txt input/polar-parameters.txt input/aster-parameters.txt 1e-5
```
### Running only reachability ###
```bash
./scripts/run_Nexus_reachability.sh input/spec-InvPendulum.txt input/polar-parameters.txt 1e-5
```
### Running only quantization ###
``` bash
./scripts/run_Nexus_quantization.sh input/spec-InvPendulum.txt input/input_range.txt input/aster-parameters.txt 1e-5
```

The safe implementation of NN controller of `InvPendulumNN` will be generated in output/InvPendulum/InvPendulumNN.cpp

## Workarounds ##

1. If you encounter "Terminated due to large over-approximation error" during reachability analysis phase:
- Consider reducing flowpipe_step_size in input/polar-parameters.txt
- Consider clipping initial conditions into smaller ranges in input/spec-<name>.txt. Then, execute 'Running only reachability'. The input_range.txt will be available in output/<name>/. Do for all smaller ranges. Create a new file input_range.txt by mentioning max and min of ranges and execute 'Running only quantization'

2. As of now, Nexus only accepts plant variables as NN inputs. If your NN input has linear combination of plant variables like in ACC (x0,x1,x5,x2-x3,x4-x5), then create a linear transformation matrix as first layer as shown in spec-ACC3.txt. Modify print in spec-ACC3.txt to print required ranges by executing 'Running only reachability'. Then create input_range.txt in format provided and then execute 'Running only quantization'.

## Workarounds ##

1. If you encounter a "Terminated due to large over-approximation error" during the reachability analysis phase:
   - Consider reducing the `flowpipe_step_size` parameter in the `input/polar-parameters.txt` file.
   - Try clipping the initial conditions into smaller ranges in the `input/spec-<name>.txt` file. Then, execute the 'Running only reachability' script. The `input_range.txt` file will be generated in the `output/<name>/` directory. Repeat this process for all smaller ranges. Finally, create a new file named `input_range.txt` by specifying the maximum and minimum ranges, and execute the 'Running only quantization' script.

2. If your neural network inputs includes a linear combination of plant variables, such as (x0, x1, x5, x2-x3, x4-x5) in ACC3 , you can create a linear transformation matrix as the first layer, as shown in the `spec-ACC3.txt` file. Modify the print statements in `spec-ACC3.txt` to output the required ranges and execute the 'Running only reachability' script. Then, create the `input_range.txt` file in the specified format and execute the 'Running only quantization' script.





