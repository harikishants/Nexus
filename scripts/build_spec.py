import sys
import os
import time

class plant_variable:
	def __init__(self,name):
		self.name = name
	def add_value(self,min_val,max_val):
		self.min_val = min_val
		self.max_val = max_val
	def add_derivative(self,derivative):
		self.derivative = derivative
	def print_variable(self):
		print("{}=[{},{}], d_{}={}"\
		.format(self.name,self.min_val,self.max_val,self.name,self.derivative))

class tool_spec:
	def __init__(self):
		self.taylor_order=3
		self.bernstein_order=3
		self.partition_num=100
		self.neuron_approx_type='Mix'
		self.remainder_type='Symbolic'
		self.num_threads=-1
		self.cutoff_threshold = 1e-6
		self.flowpipe_step_size=0.01
		self.symbolic_queue_size=100
		self.print_remainder = False
		
	def print_spec(self):
		print("taylor order={}\nbernstein order={}\npartition num={}\nneuron_approx_type={}\nremainder_type={}\nnum_threads={}\n".format(self.taylor_order,self.bernstein_order,self.partition_num,self.neuron_approx_type,self.remainder_type,self.num_threads))
		print("cutoff_threshold={}\nflowpipe_step_size={}\nsymbolic_queue_size={}\n",self.cutoff_threshold,self.flowpipe_step_size, self.symbolic_queue_size)
		
class plant_spec:
	def __init__(self,num_vars):
		self.num_vars = num_vars
		self.variables = []
		self.steps=0
		self.control_step=0
		self.num_safety_property=0
		self.safety_property = []
		self.num_target_property=0
		self.target_property = []

	def add_variable(self, name, min_val, max_val, derivative):
		if len(self.variables) < self.num_vars:
			new_variable = plant_variable(name)
			new_variable.add_value(min_val, max_val)
			new_variable.add_derivative(derivative)
			self.variables.append(new_variable)
		else:
			print("Cannot add more variables. The limit has been reached.")
	def print_spec(self):
		print("No. of plant variables = {}".format(self.num_vars))
		for var in self.variables:
			var.print_variable()
		print("Steps={}\nControl step={}".format(self.steps,self.control_step))
		
		print("No. of safety property={}"\
		.format(self.num_safety_property))
		for prop in self.safety_property:
			print(prop)
		print("No. of target property={}"\
		.format(self.num_target_property))
		for prop in self.target_property:
			print(prop[0],':',prop[1])
			
class controller_spec:
	def __init__(self):
		self.num_inputs=0
		self.input_vars=[]
		self.num_outputs=0
		self.output_vars=[]
		self.num_hid_layers=0
		self.num_hid_neurons=[]
		self.act_funcs=[]
		self.output_error_bound=0
	def add_weights(self,weights):
		self.weights = weights
	def add_biases(self,biases):
		self.biases = biases
	def print_spec(self):
		print("No. of inputs=",self.num_inputs)
		for x in self.input_vars:
			print(x)
		print("No. of outputs=",self.num_outputs)
		for x in self.output_vars:
			print(x)
		print("No. of hid layers=",self.num_hid_layers)
		for i,x in enumerate(self.num_hid_neurons):
			if i<len(self.num_hid_neurons)-1:
				print("{} Hid layer, {}, {}".format(i+1,x,self.act_funcs[i]))
		print("Output layer {}, {}".format(self.num_outputs, self.act_funcs[i]))
		for i,weight in enumerate(self.weights):
			print("Weight",i+1)
			for row in weight:
				print(row)
			print()
		for i,bias in enumerate(self.biases):
			print("Bias",i+1)
			print(bias)

def extract_spec(spec_file, polar_params_file,error):	
	#spec_file = spec_name + "/" + "spec-" + spec_name + ".txt"
	print("Extracting specification file...")
	tool = tool_spec()
	controller = controller_spec()
	controller.output_error_bound = error
	with open(spec_file, 'r') as file:
		content = file.read()
	lines = content.split('\n')
	
	for i in range(len(lines)):
		if lines[i].startswith("/*plant*/"):
			i += 2
			plant = plant_spec(int(lines[i]))
			i += 1
			for j in range(plant.num_vars):
				parts = lines[i].split('=')
				var_name = parts[0].strip()
				var_value = parts[1].strip()
				if var_value.startswith('[') and var_value.endswith(']'):
					var_value = [float(x.strip()) for x in var_value[1:-1].split(',')]
					min_val = var_value[0]
					max_val = var_value[1]
				else:
					min_val = float(var_value)
					max_val = float(var_value)
				derivative = lines[i+plant.num_vars+2]
				plant.add_variable(var_name,min_val,max_val,derivative)
				i += 1
			continue
			
		if lines[i].startswith("/*model parameters*/"):
			i += 2
			plant.steps = int(lines[i])
			i += 2
			plant.control_step = float(lines[i])
			continue
			
		if lines[i].startswith("/*safety-property*/"):
			i += 1
			plant.num_safety_property = int(lines[i])
			i += 1
			for j in range(plant.num_safety_property):
				plant.safety_property.append(lines[i])
				i += 1
			continue
			
		if lines[i].startswith("/*target-property*/"):
			i += 1
			plant.num_target_property = int(lines[i])
			i += 1
			for j in range(plant.num_target_property):
				parts = lines[i].split(':')
				condition=parts[0]
				target=parts[1]
				plant.target_property.append([condition,target])
				i += 1
			continue
			
		'''if lines[i].startswith("/*output error bound*/"):
			i += 1
			controller.output_error_bound=float(lines[i])
			continue'''
			
		if lines[i].startswith("/*plant-NN*/"):
			i += 2
			controller.num_inputs = int(lines[i])
			i += 1
			for j in range(controller.num_inputs):
				controller.input_vars.append(lines[i])
				i += 1
			i += 2
			controller.num_outputs = int(lines[i])
			i += 1
			for j in range(controller.num_outputs):
				controller.output_vars.append(lines[i])
				i += 1
			i += 2
			controller.num_hid_layers = int(lines[i])
			i += 1
			for j in range(controller.num_hid_layers):
				controller.num_hid_neurons.append(int(lines[i]))
				i += 1
			controller.num_hid_neurons.append(controller.num_outputs)
			i += 2
			for j in range(controller.num_hid_layers+1):
				controller.act_funcs.append(lines[i])
				i += 1
			continue
			
		if lines[i].startswith("#weights"):
			i += 1
			matrices = []
			for k in range(controller.num_hid_layers+1):
				matrix = []
				for m in range(controller.num_hid_neurons[k]):
					if m==0:
						lines[i]=lines[i][8:]
					if m==controller.num_hid_neurons[k]-1:
						lines[i]=lines[i][:-2]
					values = lines[i][lines[i].find("(")+1\
							:lines[i].find(")")].split(',')
					row_values = [float(val.strip()) for val in values]
					matrix.append(row_values)
					i += 1
				matrices.append(matrix)
				i += 1
			controller.add_weights(matrices)
			continue
		
		if lines[i].startswith("#bias"):
			i += 1
			vectors = []
			for k in range(controller.num_hid_layers+1):
				vector = []
				lines[i]=lines[i][7:]
				values = lines[i][lines[i].find("(")+1\
							:lines[i].find(")")].split(',')
				vector = [float(val.strip()) for val in values]
				vectors.append(vector)
				i += 2
			controller.add_biases(vectors)
			continue
		
		if lines[i].startswith("/*print-remainder*/"):
			i += 1
			if lines[i] == 'ON':
				tool.print_remainder = True
	print("Extraction completed")
	print("Extracting polar parameters file...")
	#polar_parameters_file = spec_name + "/" + "polar-parameters.txt"
	with open(polar_params_file, 'r') as file:
		content = file.read()
	lines = content.split('\n')
	for i in range(len(lines)):
		if lines[i].startswith("/*polar parameters*/"):
			i += 2
			tool.taylor_order=int(lines[i])
			i += 2
			tool.bernstein_order=int(lines[i])
			i += 2
			tool.partition_num=int(lines[i])
			i += 2
			tool.neuron_approx_type=lines[i]
			i += 2
			tool.remainder_type=lines[i]
			i += 2
			tool.num_threads=int(lines[i])
			continue
		if lines[i].startswith("/*flowstar parameters*/"):
			i += 2
			tool.cutoff_threshold=float(lines[i])
			i += 2
			tool.flowpipe_step_size=float(lines[i])
			i += 2
			tool.symbolic_queue_size=int(lines[i])
			continue
	return (plant,controller,tool)
	
def create_polar_file(spec_file,spec_name,plant,controller,tool):
	print("Creating polar file...")
	polar_file = "output/" + spec_name + "/" + spec_name + ".cpp"
	os.makedirs(os.path.dirname(polar_file), exist_ok=True)
	nn_file = spec_name + "_nn"

	f = open(polar_file,'w')
	f.write('#include "../../POLAR_Tool/POLAR/NeuralNetwork.h"\n#include <chrono>\n')
	f.write('using namespace std;\nusing namespace flowstar;\n\n')
	f.write('int main(int argc, char *argv[])\n{\n')
	f.write('cout<<endl<<"Safety verification started...";\n')
	f.write('unsigned int numVars = {};\n'.format(plant.num_vars))
	f.write('Variables vars;\n')

	for i in range(plant.num_vars):
		f.write('int {}_id = vars.declareVar("{}");\n'.format(plant.variables[i].name,plant.variables[i].name))

	f.write('ODE<Real> dynamics({\n')
	for i in range(plant.num_vars-1):
		f.write('"{}",\n'.format(plant.variables[i].derivative))
	f.write('"{}"\n'.format(plant.variables[i+1].derivative))
	f.write('},vars);\n\n');

	f.write('Computational_Setting setting(vars);\nunsigned int order = {};\nunsigned int bernstein_order = {};\n'.format(tool.taylor_order, tool.bernstein_order))
	f.write('unsigned int partition_num = {};\nsetting.setFixedStepsize({}, order);'.format(tool.partition_num,tool.flowpipe_step_size))
	f.write('\nsetting.setCutoffThreshold({});\nsetting.printOff();\nInterval I(-0.01, 0.01);\nvector<Interval> remainder_estimation(numVars, I);\nsetting.setRemainderEstimation(remainder_estimation);\n\n'.format(tool.cutoff_threshold))

	f.write('int steps = {};\n'.format(plant.steps))
	for i in range(plant.num_vars):
		f.write('Interval init_{}({},{});\n'.format(plant.variables[i].name,plant.variables[i].min_val,plant.variables[i].max_val))

	f.write('std::vector<Interval> X0;\n')
	for i in range(plant.num_vars):
		f.write('X0.push_back(init_{});\n'.format(plant.variables[i].name))

	f.write('Flowpipe initial_set(X0);\nSymbolic_Remainder symbolic_remainder(initial_set, {});\n\n'.format(tool.symbolic_queue_size))

	f.write('vector<Constraint> safeSet;\n')
	for i in range(plant.num_safety_property):
		f.write('Constraint c{}("{}",vars);\n'.format(i+1,plant.safety_property[i][:-3]))
	for i in range(plant.num_safety_property):
		f.write('safeSet.push_back(c{});\n'.format(i+1)) 
		
	f.write('vector<Constraint> targetSet;\n')
	for i in range(plant.num_target_property):
		f.write('Constraint t{}("{}",vars);\n'.format(i+1,plant.target_property[i][1][:-3]))
	for i in range(plant.num_target_property):
		f.write('targetSet.push_back(t{});\n'.format(i+1))
		
	f.write('Result_of_Reachability result;\n');
	f.write('NeuralNetwork nn("{}");\n'.format(nn_file))
	f.write('double err_max = 0;\ntime_t start_timer;\ntime_t end_timer;\ndouble seconds;\ntime(&start_timer);\n\n')

	f.write('vector<string> state_vars;\n')
	for i in range(plant.num_vars):
		f.write('state_vars.push_back("{}");\n'.format(plant.variables[i].name))

	f.write('string safe_result;\nauto begin = std::chrono::high_resolution_clock::now();\n')
	f.write('bool safety=false;\n')
	f.write('bool terminated=false;\n')
	f.write('double t=0;\n')
	for i in range(controller.num_outputs):
		f.write('double min_error_{} = 1000;\n'.format(controller.output_vars[i]))
	f.write('\nfor (int iter = 0; iter < steps; ++iter)\n{\ncout << endl << endl<<"Step " << iter+1 << " ";\nTaylorModelVec<Real> tmv_input;\n\n')

	for i in range(controller.num_inputs):
		f.write('tmv_input.tms.push_back(initial_set.tmvPre.tms[{}_id]);\n'.format(controller.input_vars[i]))
	
	f.write('\nPolarSetting polar_setting(order, bernstein_order, partition_num, "{}", "{}");\npolar_setting.set_num_threads({});\nTaylorModelVec<Real> tmv_output;\nnn.get_output_tmv_symbolic(tmv_output, tmv_input, initial_set.domain, polar_setting, setting);\n\n'.format(tool.neuron_approx_type, tool.remainder_type,tool.num_threads))

	# Printing error before adding error manually
	
	if(tool.print_remainder == True):
		f.write('cout << endl<<"NN output remainders (before adding error): " << endl;\n')
		for i in range(controller.num_outputs):
			f.write('cout <<"{} "<<tmv_output.tms[{}].remainder << endl;\n'.format(controller.output_vars[i],i))
	f.write('Interval P;\n')
	for i in range(controller.num_outputs):
		f.write('P.set(-{},{});\ntmv_output.tms[{}].remainder += P;\n'.format(controller.output_error_bound,controller.output_error_bound,i))
	
	if(tool.print_remainder == True):
		f.write('cout <<"NN output remainders:" << endl;\n')
		for i in range(controller.num_outputs):
			f.write('cout <<"{} "<<tmv_output.tms[{}].remainder << " mag = "<<tmv_output.tms[{}].remainder.mag() << endl;\n'.format(controller.output_vars[i],i,i))
			f.write('if((min_error_{} > tmv_output.tms[{}].remainder.mag()) && (tmv_output.tms[{}].remainder.mag() != 0)) \n\tmin_error_{} = tmv_output.tms[{}].remainder.mag();\n'.format(controller.output_vars[i],i,i,controller.output_vars[i],i))
	
	for i in range(controller.num_outputs):
		f.write('initial_set.tmvPre.tms[{}_id] = tmv_output.tms[{}];\n'.format(controller.output_vars[i],i))
	
	f.write('\ndynamics.reach(result, initial_set, {}, setting, safeSet, symbolic_remainder);\n'.format(plant.control_step))

	f.write('\ninitial_set = result.fp_end_of_time;\n')
	
	if(tool.print_remainder == True):
		f.write('cout <<"NN input remainders: " << endl;\n')
		for i in range(controller.num_inputs):
			f.write('cout <<"{} "<<initial_set.tmv.tms[{}].remainder << endl;\n'.format(controller.input_vars[i],i))
	
	f.write('if (result.status == COMPLETED_SAFE){\n')
	if(plant.num_safety_property>0):
		f.write('cout << "Safety property: SAFE";')
	f.write('\nsafety=true;}\nelse if (result.status == COMPLETED_UNSAFE){\n')
	if(plant.num_safety_property>0):
		f.write('cout << "Safety property: UNSAFE";')
	f.write('\nsafety=false;}\nelse if(result.status == COMPLETED_UNKNOWN){\n')
	if(plant.num_safety_property>0):
		f.write('cout  <<"Safety property: UNKNOWN";')
	f.write('\nsafety=false;}\nelse\n{\ncout<<"Terminated due to too large overestimation."<<endl<<endl;\nsafety=false;terminated=true;\n')
	f.write('std::string filePath = "input_range.txt";\nstd::ofstream file(filePath);\nfile.close();\nfile.open(filePath,std::ofstream::app);\nfile << "FAILED" <<endl;\nreturn 1;\n}\n')
	
	f.write('t={}*iter;\n'.format(plant.control_step))
	if(plant.num_target_property>0):
		f.write('if({})\n'.format(plant.target_property[0][0]))
		f.write('{\nbool b = result.fp_end_of_time.isInTarget(targetSet, setting);\nif(b) cout<< "	Target property: SAFE";\nelse cout<< "	Target property: UNSAFE";\n}\n')
	f.write('}\n')
	if(tool.print_remainder == True):
		for i in range(controller.num_outputs):
			f.write('cout<<endl<<endl<<"Min error = " << min_error_{} << endl;\n'.format(controller.output_vars[i]))
	if(plant.num_safety_property>0):
		f.write('if (safety==true) cout<<endl<<endl<<"Safety: True"<<endl;\
	else cout <<endl<<endl<< "Safety: False" << endl;\n')	
	f.write('auto end = std::chrono::high_resolution_clock::now();\nauto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin);\nseconds = elapsed.count() *  1e-9;\ncout << endl;\nvector<Interval> end_box;\nresult.fp_end_of_time.intEval(end_box, order,setting.tm_setting.cutoff_threshold);\nresult.transformToTaylorModels(setting);\n\n')
	
	#spec_file = spec_name + "/" + "spec-" + spec_name + ".txt"
	with open(spec_file, 'r') as f2:
		content = f2.read()
	lines = content.split('\n')
	f.write('Plot_Setting print_setting(vars);\ndouble min, max;\n')
	for i in range(len(lines)):
		if lines[i].startswith("/*print*/"):
			i += 1
			num_print = int(lines[i])
			i += 1
			for j in range(num_print):
				x = lines[i]
				f.write('print_setting.setOutputDim("{}");\ncout << "{}" << endl;\nprint_setting.print_interval(result.tmv_flowpipes, setting, 0,min,max,true);\nprintf("{} range = [%f,%f]",min,max);\ncout<<endl<<endl;\n'.format(x,x,x))
				i += 1
		if lines[i].startswith("#in-vars"):
			f.write('std::string filePath = "input_range.txt";\n'.format(spec_name))
			f.write('std::ofstream file(filePath);\nfile.close();\n')
			f.write('file.open(filePath,std::ofstream::app);\n')
			f.write('if (safety==true) file << "SAFE" << endl;\n')
			f.write('else file << "UNSAFE" << endl;\n')
			i += 1
			num_print = int(lines[i])
			i += 1
			for j in range(num_print):
				x = lines[i]
				f.write('print_setting.setOutputDim("{}");\nprint_setting.print_interval(result.tmv_flowpipes, setting, 0,min,max,false);\nprintf("{} range = [%f,%f]",min,max);\n'.format(x,x))
				f.write('file << "{} = ["<< min << "," << max << "]"<< endl;\ncout<<endl;\n'.format(x))
				i += 1
			f.write('file << "layer={}";\n'.format(controller.num_hid_layers+1))
				
	f.write('\ncout<<endl;\nprintf("Time taken for reachability: %.3f seconds", seconds);cout << endl;\n')
	f.write('return 0;\n}')
				
	f2.close()
	f.close()
	print("Polar file created")
	return 1

def create_nn_file(spec_name,plant,controller):
	print("Creating Neural network file...")
	nn_file = "output/" + spec_name + "/" + spec_name + "_nn"
	os.makedirs(os.path.dirname(nn_file), exist_ok=True)
	f = open(nn_file,'w')
	f.write('{}\n{}\n{}\n'.format(controller.num_inputs,controller.num_outputs,controller.num_hid_layers))
	
	for i in range(controller.num_hid_layers):
		f.write('{}\n'.format(controller.num_hid_neurons[i]))
	for i in range(controller.num_hid_layers+1):
		if controller.act_funcs[i] == "linear":
			act_func = "Affine"
		elif controller.act_funcs[i] == "relu":
			act_func = "ReLU"
		else:
			act_func = controller.act_funcs[i]
		f.write('{}\n'.format(act_func))
	
	for i in range(len(controller.weights)):
		for j,row in enumerate(controller.weights[i]):
			for element in row:
				f.write(str(element)+'\n')
			f.write(str(controller.biases[i][j])+'\n')
			
	f.write('0\n1')	
	f.close()
	print("Neural network file created")
	return 1
	
def create_make_file(spec_name):
	print("Creating Makefile...")
	f = open("output/" + spec_name + "/" + "Makefile",'w')
	f.write('CXX = g++\nHOME= /usr/local/include\nPOLAR_HOME = ../../POLAR_Tool/POLAR\nFLOWSTAR_HOME = ../../POLAR_Tool/flowstar/flowstar-toolbox\nLIBS = -lpolar -lflowstar -lmpfr -lgmp -lgsl -lgslcblas -lm -lglpk -lpthread\nCFLAGS = -I . -I $(HOME) -g -std=c++11\nLINK_FLAGS = -g  -L$(POLAR_HOME) -L$(FLOWSTAR_HOME) -L/usr/local/lib\n\n')
	f.write('all:run\n\n'.format(spec_name))
	f.write('run:{}.o\n	g++ -w $(LINK_FLAGS) -o $@ $^ $(LIBS)\n\n'.format(spec_name,spec_name))
	f.write('%.o: %.cpp\n	$(CXX) -c $(CFLAGS) -o $@ $<\n\n')
	f.write('clean:\n	rm -f *.o {}'.format(spec_name))
	f.close()
	print("Makefile created")
	print("Compiling...")
	return 1
	
	

spec_file = sys.argv[1]
polar_params_file = sys.argv[2]
error = float(sys.argv[3])
filename = os.path.basename(spec_file)
prefix = 'spec-'
suffix = '.txt'
spec_name = filename[len(prefix):-len(suffix)]

print(spec_file)
CPS = extract_spec(spec_file, polar_params_file,error)
plant=CPS[0]
controller=CPS[1]
tool=CPS[2]
#plant.print_spec()
#controller.print_spec()
#tool.print_spec()
create_polar_file(spec_file,spec_name,plant,controller,tool)
create_nn_file(spec_name,plant,controller)
create_make_file(spec_name)



