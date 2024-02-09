import pyhop
import json

def check_enough (state, ID, item, num):
	if getattr(state,item)[ID] >= num: return []
	return False

def produce_enough (state, ID, item, num):
	return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods ('have_enough', check_enough, produce_enough)

def produce (state, ID, item):
	return [('produce_{}'.format(item), ID)]

pyhop.declare_methods ('produce', produce)

def make_method (name, rule):
	def method (state, ID):
		method_list = []
		if 'Requires' in rule:
			for item in rule['Requires'].items():
				method_list.append(('have_enough', ID, item[0], item[1]))
		if 'Consumes' in rule:
			my_dict = rule["Consumes"]
			# print(type(my_dict))
			# print(my_dict)
			reversed_dict = {}
			while my_dict:
				key, value = my_dict.popitem()
				reversed_dict[key] = value
			# print(reversed_dict)
			for consumable in reversed_dict.items():
				method_list.append(('have_enough', ID, consumable[0], consumable[1]))
		method_list.append(('op_' + name.replace(" ", "_"), ID))
		#print('\nprinting method list')
		#print(method_list)
		#print('')
		return method_list
		
	name = name.replace(" ", "_")
	method.__name__ = name
	return method

def declare_methods (data):
	# some recipes are faster than others for the same product even though they might require extra tools
	# sort the recipes so that faster recipes go first

	# your code here
	# hint: call make_method, then declare the method to pyhop using pyhop.declare_methods('foo', m1, m2, ..., mk)	
	op = {}
	for it in data['Items']:
		op[it] = []
		for item in data['Recipes'].items():
			# the item is essentially an array which contains two elements
			# the first element is the key and the second is the value
			prod = list(item[1]["Produces"].keys())[0]
			
			if prod == it:
				op[it].append(make_method(item[0], item[1]))
	
	my_list = data["Tools"]
	# print(type(my_list))
	# print(my_list)
	new_list = my_list[::-1]
	#print(new_list)

	for it in new_list:
		op[it] = []
		for item in data['Recipes'].items():
			prod = list(item[1]["Produces"].keys())[0]
			if prod == it:
				op[it].append(make_method(item[0], item[1]))

	# print("printing operators")
	# print(op)


	#sort list based on what recipe goes faster
	for key, value in op.items():
		pyhop.declare_methods("produce_" + key, *value)			

def make_operator(rule):
	key_rule = rule[0]
	value_rule = rule[1]
	# print('printing value')
	# print(value_rule)
	# print(type(value_rule))
	def operator (state, ID):
		# your code here
		conditional = True
		if "Consumes" in value_rule:
			for resource, amount in value_rule["Consumes"].items():
				if getattr(state, resource)[ID] < amount:
					conditional = False

		if "Requires" in value_rule:
			for resource, amount in value_rule["Requires"].items():
				if getattr(state, resource)[ID] < amount:
					conditional = False

		if state.time[ID] < value_rule["Time"]:
			conditional = False
		

		if conditional:
			# decreases resources used:
			if "Consumes" in value_rule:
				for key, value in value_rule["Consumes"].items():
					setattr(state, key, {ID: getattr(state, key)[ID] - value})

			# adds number on what was produced
			for key, value in value_rule["Produces"].items():
				setattr(state, key, {ID: getattr(state, key)[ID] + value})

			# sets time taken
			state.time[ID] -= value_rule["Time"]
			return state
		return False
	# Set the __name__ attribute for the operator function
	key_rule = key_rule.replace(" ", "_")
	operator.__name__ = f"op_{key_rule}"
	return operator

def declare_operators (data):
	# your code here
	# hint: call make_operator, then declare the operator to pyhop using pyhop.declare_operators(o1, o2, ..., ok)
	op = []
	for item in data['Recipes'].items():
		op.append(make_operator(item))
	pyhop.declare_operators(*op)


def add_heuristic (data, ID):
	# prune search branch if heuristic() returns True
	# do not change parameters to heuristic(), but can add more heuristic functions with the same parameters: 
	# e.g. def heuristic2(...); pyhop.add_check(heuristic2)
	def heuristic (state, curr_task, tasks, plan, depth, calling_stack):
		#if the current task is to make a tool
		#and if the current task is in the stack of tasks
		# return true
		# print('\nprinting current task')
		# print(curr_task)
		# print('printing the stack (list of subtasks connecting the goal to current task)')
		# print(calling_stack)
		# print('\n')

		count = 0

		if state.time[ID] < 0:
			print('something is weird!')
			exit()

		count = 0

		if len(curr_task) == 3:
			if curr_task[0] == 'produce' and curr_task[2] in data['Tools']:
				for stack in calling_stack:
					if curr_task == stack:
						count += 1
						if count > 1:
							return True
					
		
		if depth > 65:
			return True

		return False # if True, prune this branch		

		# print('\nprinting current task')
		# print(curr_task)
		# print(type(curr_task))
		# for i in curr_task:
		# 	print(i)
		#print('printing task list')
		#print(tasks)
		#print('')
		#print('printing the current plan')
		#print(plan)
		# print('printing the depth of the search')
		# print(depth)
		# print('printing the stack (list of subtasks connecting the goal to current task)')
		# print(calling_stack)
		# print('\n')

	pyhop.add_check(heuristic)


def set_up_state (data, ID, time=0):
	state = pyhop.State('state')
	state.time = {ID: time}

	for item in data['Items']:
		setattr(state, item, {ID: 0})

	for item in data['Tools']:
		setattr(state, item, {ID: 0})

	for item, num in data['Initial'].items():
		setattr(state, item, {ID: num})

	return state

def set_up_goals (data, ID):
	goals = []
	for item, num in data['Goal'].items():
		goals.append(('have_enough', ID, item, num))

	return goals

if __name__ == '__main__':
	rules_filename = 'crafting.json'

	with open(rules_filename) as f:
		data = json.load(f)

	state = set_up_state(data, 'agent', time=250) # allot time here
	goals = set_up_goals(data, 'agent')

	declare_operators(data)
	declare_methods(data)
	add_heuristic(data, 'agent')

	pyhop.print_operators()
	pyhop.print_methods()

	# Hint: verbose output can take a long time even if the solution is correct; 
	# try verbose=1 if it is taking too long
	pyhop.pyhop(state, goals, verbose=1)
	# pyhop.pyhop(state, [('have_enough', 'agent', 'cart', 1),('have_enough', 'agent', 'rail', 20)], verbose=3)