# Aster #

<img src="https://dlohar.github.io/assets/images/aster-logo.jpg" width="150">
Aster is the first sound mixed fixed-point quantizer for fully connected feed-forward neural networks. It takes as input a network and generates a quantized network in .cpp format. The quantized network can be compiled by Xilinx Vivado HLS.

Reference paper: [Sound Mixed Fixed-Point Quantization of Neural Networks](https://dlohar.github.io/assets/documents/emsoft2023.pdf), Debasmita Lohar, Clothilde Jeangoudoux, Anastasia Volkova, and Eva Darulova, EMSOFT 2023.

## Required Software Packages

**NOTE:** Aster is implemented on top of Daisy. Make sure to follow the installation instructions mentioned in the `README-daisy` file of this project, and then proceed with Aster.

* MILP solver: [SCIP optimization Suite 7.0.3](https://www.scipopt.org/index.php#download)

* If require latency evaluation: [Xilinx’s Vivado (version v2020.1)](https://www.xilinx.com) 

**NOTE:** Aster currently uses CPLEX for generating optimization constraints. Unzip the cplex files in the `lib/` folder and ensure renaming the appropriate jar file to `cplex.jar` and move it from`lib/cplex` to `lib/`. 

## Running Aster

**NOTE:** We provide all our benchmarks here: `testcases/qnn`. For running the scripts, we assume that you are in the main directory.

### Running Aster on the a single network ###
- ``` bash scripts/qnn/run_Aster.sh <input_file> <function_name> <#layers> <setting> ```

e.g, running Aster's setting A on `SinglePendulum`:
``` bash scripts/qnn/run_Aster.sh testcases/qnn/SinglePendulumNN.scala nn1 3 A ```

**NOTE:** This script generates the quantized network in .cpp format and the optimization problem in .lp format in the folder: `Aster-Single-Network`.

- ``` bash scripts/qnn/run_Aster_Xilinx.sh <input_file> <function_name> <#layers> <setting> ```

e.g, running Aster's setting A on `SinglePendulum` and evaluate it with Xilinx:

``` bash scripts/qnn/run_Aster_Xilinx.sh testcases/qnn/SinglePendulumNN.scala nn1 3 A ```

**NOTE:** This script generates the quantized network in .cpp format, the optimization problem in .lp format, and the synthesis report in the folder: `Aster-Single-Network`.

### Running Aster on all networks with a specific setting and Xilinx to compute the latencies (as presented in the paper) ###
``` bash scripts/qnn/run-Aster_<Setting>.sh ```

**NOTE:** This script generates all quantized networks in .cpp format, optimization problems in .lp format, and the synthesis reports in the folder: `Aster-<Setting>`

## Running Daisy
We provide scripts to run Daisy's uniform and mixed precision analysis on all benchmarks and to compute latencies using Xilinx, as described in the paper. Please note that these scripts require Xilinx. 

If you wish to run a single network using only Daisy, you can use the following commands after compiling Daisy (compilation instructions are in the `README-daisy` file).

- ```./daisy --qnn --codegen --lang=C --apfixed --precision=Fixed32 <full_path_to_the_network>```(uniform precision)

- ```./daisy --qnn --codegen --lang=C --apfixed --mixed-tuning --precision=Fixed32 <full_path_to_the_network>```(mixed precision)

**NOTE:** These scripts generate the quantized networks in .cpp format in the folder: `output`

### Running Daisy's uniform precision on all networks and Xilinx to compute the latencies ###
``` bash scripts/qnn/nn_daisy_uniform_precision.sh ```

**NOTE:** This script generates all quantized networks in .cpp format and the synthesis reports in the folder: `uniform32`

### Running Daisy's mixed precision on all networks and Xilinx to compute the latencies(as presented in the paper) ###
``` bash scripts/qnn/nn_daisy_mixed_precision.sh ```

**NOTE:** This script generates all quantized networks in .cpp format and the synthesis reports in the folder: `mixed-precision`

## Contributors ##
- Debasmita Lohar
- Eva Darulova
- Anastasia Volkova
- Clothilde Jeangoudoux

## Acknowledgements ##
Aster is implemented on top of Daisy's infrustructure.
