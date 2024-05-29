start_global=$(date +%s.%N)

spec_file=$1
polar_param_file=$2
aster_param_file=$3
error=$4

prefix="input/spec-"
suffix=".txt"
foo=${spec_file#"$prefix"}
spec_name=${foo%"$suffix"}

echo -e "\n*********************Starting Phase 1: Reachability analysis*********************\n"
python3 scripts/build_spec.py ${spec_file} ${polar_param_file} ${error}
cd output/${spec_name}/
make
./run
layer=$(tail -n 1 input_range.txt | cut -d'=' -f2)

first_line=$(head -n 1 input_range.txt)
if [ "$first_line" == "SAFE" ]; then
	echo "CPS is $first_line. Generating $first_line implementation..."

	cd ../../
	echo -e "\n*********************Reachability analysis completed*********************\n"
	echo -e "\n*********************Starting Phase 2: NN quantization*********************\n"
	python3 scripts/extract_spec_to_scala.py ${spec_file} output/${spec_name}/input_range.txt ${error}
	
	source ${aster_param_file}
	cd Aster/
	
	sbt compile
	if [ ! -e daisy ]
	then
  		sbt script
	fi
	
	sbt "run --qnn --qnn-quant --precision=Fixed32 --layer=$layer --minLen=$minLen --maxLen=$maxLen --initLen=$initLen --lang=C --codegenNNOriginal --apfixed ../output/${spec_name}/${spec_name}NN.scala"

	mv output/${spec_name}NN.cpp ../output/${spec_name}/
	if [ $? -ne 0 ]; then
        echo -e "\nQuantization is infeasible. Exiting Nexus..."
        end_global=$(date +%s.%N)
        elapsed=$(echo "$end_global - $start_global" | bc -l)
        printf "\nNexus execution time: %.3f seconds\n" "$elapsed"
        exit 1
    fi
    
	cd ..
	echo -e "\n**********************NN quantization completed**********************\n"
	#To run Xilinx
	echo -e "\n**********************Starting design synthesis**********************\n"
	/var/tmp/Vitis_HLS/2023.2/bin/vitis_hls Aster/scripts/qnn/vivado_compile_general.tcl output/${spec_name}/${spec_name}NN nn1 output/${spec_name}/${spec_name}NN.cpp
	echo -e "\n**********************Design synthesis completed**********************\n"
elif [ "$first_line" == "UNSAFE" ]; then
	echo -e "\nCPS is $first_line. Exiting Nexus..."
else
	echo -e "\nReachability terminated. Exiting Nexus..."
fi

end_global=$(date +%s.%N)

elapsed=$(echo "$end_global - $start_global" | bc -l) 

printf "\nNexus execution time: %.3f seconds\n" "$elapsed"

