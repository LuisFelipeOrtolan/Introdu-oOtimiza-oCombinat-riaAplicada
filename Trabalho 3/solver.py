import gurobipy as gp

DEBUG = 0

def grau(edges, node_count):
    nodes = [0] * node_count
    grau = 0

    for edge in edges:
        nodes[edge[0]] = nodes[edge[0]] + 1
        nodes[edge[1]] = nodes[edge[1]] + 1
    for i in nodes:
        if i > grau:
            grau = i

    return grau

def rightSolution(solution):
    unique = []
    for number in solution:
        if number not in unique:
            unique.append(number)
    unique.sort()
 
    i = 0
    erase = []
    write = []
    
    for number in unique:
        if i != number:
            erase.append(number)
            write.append(i)
        i = i + 1
    
    i = 0
    for number in solution:
        if number in erase:
            solution[i] = write[erase.index(number)]
        i = i + 1

    return solution

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


def ColoringNaive(node_count, edge_count, edges):

    if node_count < 1000:
        grauGrafo = grau(edges, node_count)

        model = gp.Model("SolverIOCA")

        # Creating variable that indicates if a color k is used.
        y = {}
        for k in range(grauGrafo):
            y[k] = model.addVar(vtype = "B", name = "y["+str(k)+"]")

        # Creating variable that indicates if a node u has the color k.
        x = {}
        for u in range(node_count):
            for k in range(grauGrafo):
                x[u,k] = model.addVar(vtype = "B", name = "x["+str(u)+","+str(k)+"]")

        # Every node has only one color.
        for u in range(node_count):
            model.addConstr(gp.quicksum(x[u,k] for k in range(grauGrafo)) == 1)

        # A node can only use an avaliable color.
        for u in range(node_count):
            for k in range(grauGrafo):
                model.addConstr(x[u,k] <= y[k])

        # Adjacent nodes need to have different colors.
        for edge in edges:
            for k in range(grauGrafo):
                model.addConstr(x[edge[0],k] + x[edge[1],k] <= 1)

        # Objective.
        obj = gp.quicksum(y[k] for k in range(grauGrafo))
        model.setObjective(obj, gp.GRB.MINIMIZE)
        model.optimize()

        colors_used = int(model.objVal)

        solution = [-1] * node_count

        for u in range(node_count):
            for k in range(grauGrafo):
                if model.getVarByName("x["+str(u)+","+str(k)+"]").x == 1:
                    solution[u] = k
                    break

        solution = rightSolution(solution)

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
