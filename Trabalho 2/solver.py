# Otimização Aleatória Aplicada
# Universidade Federal de São Carlos
# Aluno: Luís Felipe Corrêa Ortolan
# RA: 759375

from collections import namedtuple
import gurobipy as gp
import numpy as np
import sys
import math

Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])

DEBUG = 0

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def solve_it(input_data):
    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    facility_count = int(parts[0])
    customer_count = int(parts[1])

    facilities = []
    for i in range(1, facility_count+1):
        parts = lines[i].split()
        facilities.append(Facility(i-1, float(parts[0]), int(parts[1]), Point(float(parts[2]), float(parts[3])) ))

    customers = []
    for i in range(facility_count+1, facility_count+1+customer_count):
        parts = lines[i].split()
        customers.append(Customer(i-1-facility_count, int(parts[0]), Point(float(parts[1]), float(parts[2]))))

    return facilityNaive(facility_count, facilities, customer_count, customers)


def facilityNaive(facility_count, facilities, customer_count, customers):
    if DEBUG >= 1:
        print(f"Numero de possiveis instalacoes = {facility_count}")
        print(f"Numero de clientes = {customer_count}")

    if DEBUG >= 2:
        print("Instalacoes na ordem que foram lidas")
        for facility in facilities:
            print(facility)
        print()

    if DEBUG >= 2:
        print("Clientes na ordem que foram lidos")
        for customer in customers:
            print(customer)
        print()

    # Modify this code to run your optimization algorithm
    solution = [-1]*len(customers)
    capacity_remaining = [f.capacity for f in facilities]

    if facility_count < 500:
        model = gp.Model("SolverIOCA")

        # Creating Variable that indicates if a store is open.
        y = {}

        for i in facilities:
            y[i.index] = model.addVar(vtype = "B" , name = "y["+str(i.index)+"]")

        x = {}
        # Creating Variable that indicates if a customer is conected to a store.
        for i in facilities:
            for j in customers:
                x[i.index,j.index] = model.addVar(vtype = "B", name = "x["+str(i.index)+","+str(j.index)+"]")

        # Each client is conected to one store.
        for j in customers:
            model.addConstr(gp.quicksum(x[i.index,j.index] for i in facilities) == 1)

        # Clients can only be conected to an open store.
        for i in facilities:
            for j in customers:
                model.addConstr(x[i.index,j.index] <= y[i.index])

        # The sum of client's demands have to be equal or less to the store's capacity.
        for i in facilities:
            model.addConstr(gp.quicksum((j.demand * x[i.index,j.index]) for j in customers) <= i.capacity)

        # Setting the objective
        obj = (gp.quicksum((i.setup_cost * y[i.index]) for i in facilities)) + (gp.quicksum(gp.quicksum((length(i.location, j.location) * x[i.index,j.index]) for i in facilities) for j in customers))
        model.setObjective(obj, gp.GRB.MINIMIZE)
        model.optimize()

        value = model.objVal
        
        for i in facilities:
            for j in customers:
                if(model.getVarByName("x["+str(i.index)+","+str(j.index)+"]").x == 1):
                    solution[j.index] = i.index

    else:
        # trivial solution: pack the facilities one by one until all the customers are served
        facility_index = 0
        for customer in customers:
            if capacity_remaining[facility_index] >= customer.demand:
                solution[customer.index] = facility_index
                capacity_remaining[facility_index] -= customer.demand
            else:
                facility_index += 1
                assert capacity_remaining[facility_index] >= customer.demand
                solution[customer.index] = facility_index
                capacity_remaining[facility_index] -= customer.demand

        used = [0]*len(facilities)
        for facility_index in solution:
            used[facility_index] = 1

        # calculate the cost of the solution
        value = sum([f.setup_cost*used[f.index] for f in facilities])
        for customer in customers:
            value += length(customer.location, facilities[solution[customer.index]].location)

    # prepare the solution in the specified output format
    output_data = '%.2f' % value + '\n'
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
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)')
