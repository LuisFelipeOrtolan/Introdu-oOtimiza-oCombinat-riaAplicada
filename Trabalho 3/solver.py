# Otimização Aleatória Aplicada
# Universidade Federal de São Carlos
# Aluno: Luís Felipe Corrêa Ortolan
# RA: 759375

import gurobipy as gp

DEBUG = 0

# Function that calculates the degree of the graph.
# Input: A list of points with the graph's edges and the number of nodes in the graph.
# Output: the graph's degree.
def degree(edges, node_count):
    nodes = [0] * node_count # List with all the nodes and its degrees.
    degree = 0

    # Go for each edge and increase the current degree of both nodes.
    for edge in edges:
        nodes[edge[0]] = nodes[edge[0]] + 1
        nodes[edge[1]] = nodes[edge[1]] + 1
    # Gets the highest degree as the graph's degree.
    for i in nodes:
        if i > degree: # If the degree from the current node is higher than the current graph's degree, this is the new graph's degree.
            degree = i
    # Return the graph's degree.
    return degree

# Function that transform the solution to use the colors with the lowest number avaliable.
# Input: The current solution of the problem using any numbers.
# Output: A new solution using the lowest numbers avaliable.
def rightSolution(solution):
    # Get all the unique numbers in the solution.
    unique = []
    for number in solution:
        if number not in unique:
            unique.append(number)
    # Sorting the unique numbers in the solution.
    unique.sort()
 
    i = 0
    # Erase and write lists are to link the number in the current solution to the number its going to be in the final solution.
    # For example, if a number is 27 and the number 3 is avaliable, erase[i] will have number 27 and write[i] will have number 3. 
    erase = []
    write = []
    
    # Check every number in the solution.
    for number in unique:
        if i != number: # If a number in the solution is not as low as it can be, put in the erase/write list.
            erase.append(number)
            write.append(i)
        i = i + 1
    
    i = 0
    # Check every number in the solution.
    for number in solution:
        if number in erase: # If the number is in the erase list, 
            solution[i] = write[erase.index(number)] # Swap it for the number in the write list.
        i = i + 1

    return solution

# Function that prepares the data for the function that actually solves the problem.
# Input: The data from the instances.
# Output: How many colors were used and what's the solution.
def solve_it(input_data):   
    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))

    if DEBUG >= 1:
        print(f"Numero de vertices = {node_count}")
        print(f"Numero de arestas = {edge_count}")

    if DEBUG >= 2:
        print("Arestas:")
        for edge in edges:
            print(edge)
        print()

    return ColoringNaive(node_count, edge_count, edges)

# Function that solves the problem.
# Input: how many nodes are in the graph, how many edges are in the graph and the egdes.
# Output: How many colors were used and what's the solution.
def ColoringNaive(node_count, edge_count, edges):
    # For memory purposes, if the problem has less than 1000 nodes, solve with Gurobi.
    if node_count < 1000:
        degreeGraph = degree(edges, node_count) # Calculates the graph's degree.

        model = gp.Model("SolverIOCA") # Call Gurobi solver.

        # Creating variable that indicates if a color k is used.
        y = {}
        for k in range(degreeGraph):
            y[k] = model.addVar(vtype = "B", name = "y["+str(k)+"]")

        # Creating variable that indicates if a node u has the color k.
        x = {}
        for u in range(node_count):
            for k in range(degreeGraph):
                x[u,k] = model.addVar(vtype = "B", name = "x["+str(u)+","+str(k)+"]")

        # Every node has only one color.
        for u in range(node_count):
            model.addConstr(gp.quicksum(x[u,k] for k in range(degreeGraph)) == 1)

        # A node can only use an avaliable color.
        for u in range(node_count):
            for k in range(degreeGraph):
                model.addConstr(x[u,k] <= y[k])

        # Adjacent nodes need to have different colors.
        for edge in edges:
            for k in range(degreeGraph):
                model.addConstr(x[edge[0],k] + x[edge[1],k] <= 1)

        # Objective.
        obj = gp.quicksum(y[k] for k in range(degreeGraph))
        model.setObjective(obj, gp.GRB.MINIMIZE)
        model.optimize()

        colors_used = int(model.objVal) # How many colors were used.

        solution = [-1] * node_count

        # Getting the solution.
        for u in range(node_count):
            for k in range(degreeGraph):
                if model.getVarByName("x["+str(u)+","+str(k)+"]").x == 1:
                    solution[u] = k
                    break

        solution = rightSolution(solution)

    # For memory purposes, if the problem has more than 1000 nodes, solve with a naive algorithm.
    else:
        solution = range(0, node_count)
        colors_used = node_count

    # prepare the solution in the specified output format
    output_data = str(colors_used) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        output_data = solve_it(input_data)
        print(output_data)
        solution_file = open(file_location + ".sol", "w")
        solution_file.write(output_data)
        solution_file.close()
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')
