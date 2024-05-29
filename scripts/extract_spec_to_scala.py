import sys
import os

class controller_spec:
	def __init__(self):
		self.num_inputs=0
		self.input_vars=[]
		self.input_vars_range=[]
		self.num_outputs=0
		self.output_vars=[]
		self.num_hid_layers=0
		self.num_hid_neurons=[]
		self.act_funcs=[]
		self.error=0
	def add_weights(self,weights):
		self.weights = weights
	def add_biases(self,biases):
		self.biases = biases
		
def load_nn(spec_file, input_range_file, error):
	print("\nLoading NN...")
	controller = controller_spec()
	controller.error = error
	with open(spec_file, 'r') as file:
		content = file.read()
	lines = content.split('\n')
	
	for i in range(len(lines)):
		#print(lines[i])
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
	with open(input_range_file, 'r') as file:
		content = file.read()
	lines = content.split('\n')
	print("Loading NN ranges...\n")
	for i in range(1,controller.num_inputs+1):
		print(lines[i])
		range_part = lines[i].split('=')[1].strip()
		range_values = range_part.strip('[]').split(',')
		range_tuple = (float(range_values[0]), float(range_values[1]))
		controller.input_vars_range.append(range_tuple)
	return controller

def create_scala(NN, spec_name):
	print("Creating scala file...")
	scala_file = "output/" + spec_name + "/" + spec_name + "NN.scala"
	with open(scala_file, 'w') as f:
		f.write('import daisy.lang._\nimport Vector._\n\nobject {}NN {{\n   def nn1(x: Vector): Vector = {{\n\t\trequire(lowerBounds(x, List('.format(spec_name))
		i=0
		for i in range(len(NN.input_vars_range)-1):
			f.write('{}, '.format(NN.input_vars_range[i][0]))
		f.write('{})) &&\n'.format(NN.input_vars_range[i][0]))
		f.write('\t\t\t\tupperBounds(x, List(')
		for i in range(len(NN.input_vars_range)-1):
			f.write('{}, '.format(NN.input_vars_range[i][1]))
		f.write('{})))\n'.format(NN.input_vars_range[i][1]))

		#weights
		for w in range(len(NN.weights)):
			f.write('\tval weights{} = Matrix(List('.format(w+1))
			i=0
			for i in range(len(NN.weights[w])-1):
				f.write('\n\t\tList( ')
				for j in range(len(NN.weights[w][i])-1):
					f.write(str(NN.weights[w][i][j])+', ')
				f.write(str(NN.weights[w][i][j+1]) + '),')
			if(len(NN.weights[w])>1): i+=1
			f.write('\n\t\tList( ')
			for j in range(len(NN.weights[w][i])-1):
				f.write(str(NN.weights[w][i][j])+', ')
			j += 1
			f.write(str(NN.weights[w][i][j]) + ')))\n\n')
			
		#biases
		for b in range(len(NN.biases)):
			f.write('\tval bias{} = Vector(List('.format(b+1))
			i=0
			for i in range(len(NN.biases[b])-1):
				f.write('{}, '.format(NN.biases[b][i]))
			if(len(NN.biases[b])>1): i+=1
			f.write('{}))\n\n'.format(NN.biases[b][i]))
		input_ = "x"
		for i in range(len(NN.biases)):
			f.write('\tval layer{} = {}(weights{} * {} + bias{})\n'.format(i+1, NN.act_funcs[i], i+1, input_, i+1))
			input_ = "layer" + str(i+1)
		f.write('\n\tlayer{}\n\n\t}} ensuring(res => res +/- {})\n}}'.format(i+1, NN.error))
		
	print("Scala file created.")
				
			

spec_file = sys.argv[1]
filename = os.path.basename(spec_file)
prefix = 'spec-'
suffix = '.txt'
spec_name = filename[len(prefix):-len(suffix)]

input_range_file = sys.argv[2]
error = float(sys.argv[3])

NN = load_nn(spec_file, input_range_file, error)

create_scala(NN, spec_name)


