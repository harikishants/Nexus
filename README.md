# Nexus

Nexus is a two-phase framework that integrates safety verification of neural network-controlled cyber-physical systems (CPS) with mixed precision fixed-point quantization of neural network (NN) controllers.

- **Input**: Plant initial conditions, dynamics, safety properties, NN controller, and error.
- **Output**: Safe implementation of NN controller, which can be compiled by Xilinx Vitis HLS.

## Pre-requisite Software Packages

**Note**: Nexus is implemented on top of POLAR and Aster. Make sure to follow the installation instructions in POLAR and Aster before proceeding with Nexus.

Download POLAR and Aster inside Nexus/.

- **Download [POLAR](https://github.com/ChaoHuang2018/POLAR_Tool)**

- **Download [Aster](https://github.com/dlohar/Aster/tree/extended-code-gen)**

- **Download [Xilinx’s Vitis HLS (version v2023.2)](https://www.xilinx.com)**

### Applying modifications

Replace files in `POLAR_Tool/` from `modifications/` as shown below
```bash
# Assuming that you are inside Nexus/
cp modifications/Continous.cpp POLAR_Tool/flowstar/flowstar-toolbox/
cp modifications/Continous.h POLAR_Tool/flowstar/flowstar-toolbox/
```

### Compiling POLAR
```bash
# Assuming that you are inside Nexus/)
cd POLAR_Tool/POLAR
make
cd ../flowstar/flowstar-toolbox/
make
```

## Running Nexus

**NOTE:** We provide all our specfications of our benchmarks here: `input/`. For running the scripts, we assume that you are in the Nexus/ before running

e.g, running Nexus on `InvPendulum` with Aster setting B and error 1e-5.

### Running whole pipeline ###
```bash
./scripts/run_Nexus.sh input/spec-InvPendulum.txt scripts/polar_parameters.txt scripts/aster_setting_B.txt 1e-5
```
### Running only reachability ###
```bash
./scripts/run_Nexus_reachability.sh input/spec-InvPendulum.txt scripts/polar_parameters.txt 1e-5
```
### Running only quantization ###
``` bash
./scripts/run_Nexus_quantization.sh input/spec-InvPendulum.txt scripts/input_range.txt scripts/aster_setting_B.txt 1e-5
```

The safe implementation of the NN controller, `InvPendulumNN`, will be generated in `output/InvPendulum/InvPendulumNN.cpp`.
The latency of synthesized design can found in `output/InvPendulum/InvPendulumNN/solution/syn/report/nn1_csynth.rpt`

## Workarounds ##

1. If you encounter a "Terminated due to large over-approximation error" during the reachability analysis phase:
   - Consider reducing the `flowpipe_step_size` parameter in the `input/polar-parameters.txt` file.
   - Try clipping the initial conditions into smaller ranges in the `input/spec-<name>.txt` file. Then, execute the 'Running only reachability' script. The `input_range.txt` file will be generated in the `output/<name>/` directory. Repeat this process for all smaller ranges. Finally, create a new file named `input_range.txt` by specifying the maximum and minimum ranges, and execute the 'Running only quantization' script by giving path to `input_range.txt`.

2. If your neural network inputs include a linear combination of plant variables, such as (x0, x1, x5, x2-x3, x4-x5) in ACCs , you can create a linear transformation matrix as the first layer, as shown in the `spec-ACC5.txt` file. Modify the print statements in `spec-ACC5.txt` to output the required ranges by executing the 'Running only reachability' script. Then, create `scripts/input_range.txt` file in the specified format and execute the 'Running only quantization' script. Make sure that #in-vars in `spec-ACC5.txt` match with number of inputs in `input_range.txt`.

## Contributors
- Harikishan T S
- Debasmita Lohar
- Sumana Ghosh

