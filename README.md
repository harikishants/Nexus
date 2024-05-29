# Nexus #

Nexus, a two-phase framework that integrates safety verification of neural network controlled cyber-physical systems (CPS) with mixed precision fixed-point quantization of neural network (NN) controllers.

Input: Plant initial conditions, dynamics, NN controller and error.
Output: Safe implementation of NN controller which can be compiled by Xilinx Vitis HLS.

## Pre-requisite Software Packages

**NOTE:** Nexus implemented on top of POLAR and Aster. Make sure to follow the installation instructions mentioned in the `README-POLAR` and `README-Aster` file of this project, and then proceed with Nexus.

Download POLAR: git clone https://github.com/ChaoHuang2018/POLAR_Tool (commit 13d42b0)
Download Aster: git clone https://github.com/dlohar/Aster/tree/Nexus
Download Xilinx: [Xilinx’s Vitis HLS (version v2023.2)](https://www.xilinx.com)

Rename POLAR_Tool/ to POLAR/ and keep it inside Nexus/
Keep Aster/ inside Nexus/

The folder structure should look like this:
Nexus/POLAR/...
Nexus/Aster/...

Replace files in POLAR/ from modifications/ as shown below
(Assuming that you are inside Nexus/)
cp modifications/Continous.cpp POLAR/flowstar/flowstar-toolbox/
cp modifications/Continous.h POLAR/flowstar/flowstar-toolbox/

To compile POLAR
(Assuming that you are inside Nexus/)
cd POLAR/POLAR
make
cd ../flowstar/flowstar-toolbox/
make

## Running Nexus

**NOTE:** We provide all our specfications of our benchmarks here: `input/`. For running the scripts, we assume that you are in the Nexus/

e.g, running Nexus on `InvPendulum`:

### Running whole pipeline ###
- ``` bash ./scripts/run_Nexus.sh input/spec-InvPendulum.txt input/polar-parameters.txt input/aster-parameters.txt 1e-5 ```
- 
### Running only reachability ###
- ``` bash ./scripts/run_Nexus_reachability.sh input/spec-InvPendulum.txt input/polar-parameters.txt 1e-5 ```

### Running only quantization ###
- ``` bash ./scripts/run_Nexus_quantization.sh input/spec-InvPendulum.txt input/input_range.txt input/aster-parameters.txt 1e-5 ```

The safe implementation of NN controller `InvPendulumNN.cpp` will be generated in output/InvPendulum/.

