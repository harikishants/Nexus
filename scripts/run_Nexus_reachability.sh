start_global=$(date +%s.%N)

spec_file=$1
polar_param_file=$2
error=$3

prefix="input/spec-"
suffix=".txt"
foo=${spec_file#"$prefix"}
spec_name=${foo%"$suffix"}

echo -e "\n*********************Starting Reachability analysis*********************\n"
python3 scripts/build_spec.py ${spec_file} ${polar_param_file} ${error}
cd output/${spec_name}/
make
./run
layer=$(tail -n 1 input_range.txt | cut -d'=' -f2)

first_line=$(head -n 1 input_range.txt)
if [ "$first_line" == "SAFE" ]; then
	echo -e "\nCPS is $first_line. Exiting Nexus..."
elif [ "$first_line" == "UNSAFE" ]; then
	echo -e "\nCPS is $first_line. Exiting Nexus..."
else
	echo -e "\nReachability terminated. Exiting Nexus..."
fi

end_global=$(date +%s.%N)

elapsed=$(echo "$end_global - $start_global" | bc -l) 

printf "\nNexus_reachability execution time: %.3f seconds\n" "$elapsed"

