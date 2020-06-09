from collections import namedtuple
from operator import attrgetter

Item = namedtuple("Item", ['index', 'value', 'weight','reason','unreason'])

# Function that increases by one a binary number in a vector.
# Input: a binary number in a vector with every digit in a position in the vector and the number of positions you want to have at the end.
# Output: a vector with the old binary number increased by one with every digit in a position in the vector.
def increase(vector, num_items):
    number = 0
    # Convert the binary to decimal.
    for position in vector:
        number = (number << 1) | position
    # Add one to the decimal number.
    number = number + 1
    # Transforms the decimal into binary.
    new_vector = [int(x) for x in bin(number)[2:]]
    # If needed, add 0's until it has the size intended.
    for i in range(len(new_vector),num_items):
        new_vector.insert(0,0)
    return new_vector

# Function that solves the snapsack problem testing all the possibilities.
# Input: The number of items avaliable, tuples with the items, the capacity of the backpack and a matrix with all the conflicts.
# Output: A vector with the best solution, an integer with the value of the items selected and it's weight.
def bruteForce(num_items, items, capacity, conflicts):
    curr_solution = []
    # Create a vector with 0's
    for i in range(num_items):
        curr_solution.append(0)

    curr_value = 0
    curr_weight = 0

    aux_solution = curr_solution

    # For all the possibilities:
    for i in range(2 ** (num_items)-1):
        # Treating like all the items were a unique binary number, where 1 the item is in the backpack and 0 it's not.
        # Increase the binary number so we have the next possibility.
        aux_solution = increase(aux_solution,num_items)
        # If the value of the next possibility is bigger than the current, weight's less, and there's no conflict in the new possibility:
        if((calculateValue(aux_solution, items) > curr_value) & (calculateWeight(aux_solution, items) <= capacity) & (checkConflicts(aux_solution, conflicts))):
            # This is the new solution.
            curr_solution = aux_solution
            curr_value = calculateValue(aux_solution, items)
            curr_weight = calculateWeight(aux_solution, items)

    return curr_solution, curr_value, curr_weight

# A function that calculates the weight of a solution in the knapsack problem.
# Input: A binary vector with a solution and tuples with the items avaliable for the backpack.
# Output: The weight of the backpack in this solution.
def calculateWeight(solution, items):
    i = 0
    weight = 0
    for item in solution:
        if item == 1:
            weight = weight + getItem(i, items).weight
        i = i + 1
    return weight

# A function that calculates the value of a solution in the knapsack problem.
# Input: A binary vector with a solution and tuples with the items avaliable for the backpack.
# Output: The value of the backpack in this solution.
def calculateValue(solution, items):
    i = 0
    value = 0
    for item in solution:
        if item == 1:
            value = value + getItem(i,items).value
        i = i + 1
    return value

# A function that returns an item from it's index.
# Input: an index for the wanted item and tuples with the items avaliable for the backpack.
# Output: a tuple with the wanted index.
def getItem(index, items):
    for item in items:
        if item.index == index:
            return item
# A function that checks if there's any conflicts in one solution.
# Input: a binary vector with the solution and a matrix with which items conflicts.
# Output: 0 if the solution is not valid and 1 if it is.
def checkConflicts(solution, conflicts):
    i = 0
    for item in solution:
        if item == 1:
            for conflict in conflicts[i]:
                if (solution[conflict] == 1) & (conflict != -1):
                    return 0
        i = i + 1
    return 1 

# A function that tries to improve a solution by changing one item in the backpack for other which is not. 
#   It does that for all the possible combinations.
# Input: The number of items avaliable, tuples with the items, the capacity of the backpack, a matrix with all the conflicts
#           and a binary vector with the current solution that is going to be changed.
# Output: if there is a better solution by changing two items, it returns the new solution, otherwise the old one.
def trocaSimples(num_items, items, capacity, conflicts, curr_solution):
    i = 0
    for item in curr_solution:
        # Search for an item that is in the list.
        if item == 1:
            j = 0
            for item_aux in curr_solution:
                # Search for an item that is not in the list to trade with the one there is.
                if item_aux == 0:
                    # If it's more valueble and weigth less or equal,
                    if (getItem(j, items).value > getItem(i,items).value) & (getItem(j, items).weight <= getItem(i, items).weight):
                        # Put the new item in the backpack and remove the old one.
                        aux_solution = curr_solution
                        aux_solution[i] = 0
                        aux_solution[j] = 1
                        # If there's no conflict in the solution,
                        if(checkConflicts(aux_solution,conflicts)):
                            # Set the current solution to this one.
                            curr_solution = aux_solution
                            break
                j = j + 1
        i = i + 1
    return curr_solution
# A function that tries to improve a solution by changing one item in the backpack for two others which are not.
#   It does that for all the possible combinations.
# Input: The number of items avaliable, tuples with the items, the capacity of the backpack, a matrix with all the conflicts
#           and a binary vector with the current solution that is going to be changed.
# Output: if there is a better solution by changing two items, it returns the new solution, otherwise the old one.
def trocaDupla(num_items, items, capacity, conflicts, curr_solution):
    i = 0
    done = 0
    for item in curr_solution:
        # Search for an item in the backpack.
        if item == 1:
            j = 0
            for substitute_one in curr_solution:
                # Search for an item that is not in the backpack.
                if substitute_one == 0:
                    # If the item has less weight than the original one,
                    if(getItem(j, items).weight < getItem(i, items).weight):
                        k = 0
                        # Search for a second item that is not in the backpack.
                        for substitute_two in curr_solution:
                            # If the two items that are now in the backpack have less or equal weight and more value,
                            if((substitute_two == 0) & (getItem(j,items).weight + getItem(k, items).weight <= getItem(i, items).weight) & 
                                (getItem(j,items).value + getItem(k, items).value > getItem(i, items).value) & (k != j)):
                                # Put the two new items in the backpack and remove the original one.
                                aux_solution = curr_solution
                                aux_solution[i] = 0
                                aux_solution[j] = 1
                                aux_solution[k] = 1
                                # If there are no conflicts,
                                if(checkConflicts(aux_solution, conflicts)):
                                    # It becomes the current solution and it breaks the loop to find a new item in the backpack.
                                    curr_solution = aux_solution
                                    done = 1
                                    break
                            k = k + 1
                # This is a check to see if the original item is still in the backpack and avaliable to trade for other items.
                # If it's not, it breaks the for and it searches for a new item avaliable.
                if(done == 1):
                    done = 0
                    break

                j = j + 1
        i = i + 1
    return curr_solution

# Remove an item based in it's id.
# Input: tuples with the items and an integer with the id of the item to be removed.
# Output: the item removed from the items.
def removeIndex(self, id):
    for elem in self:
        if (elem.index == id):
            self.remove(elem)
            break
# A function that recieves lines with two numbers with conclicts and transforms it to a matrix where every line has all
#   the items that that line(item) has.
# Input: lines with two numbers with conflicts and the number of items avaliable for the backpack.
# Ouput: a matrix with all the conflicts.
def treatConflicts(conflicts, num_items):
    new_conflicts = []
    # Start every position with -1, indicating that there are no conflicts for that position, at least for now.
    for i in range(0,num_items):
        new_conflicts.append([-1])
    
    # For every conflict line, put the numbers that conflict for each line. (Ex: if the conflict is 1 and 2,
    #   put in the line 1 a number 2 and in the line 2 a number 1).
    for conflict in conflicts:
        # If there's no conflict there yet, remove -1 and put the index of the item that conflicts in that line.
        if new_conflicts[conflict[0]] == [-1]:
            new_conflicts[conflict[0]] = [conflict[1]]
        # If already is a conflict, just append the index of the item.
        else:
            new_conflicts[conflict[0]].append(conflict[1])
        # Do the same for the other index from the other item.
        if new_conflicts[conflict[1]] == [-1]:
            new_conflicts[conflict[1]] = [conflict[0]]
        else:
            new_conflicts[conflict[1]].append(conflict[0])

    return new_conflicts

# A function that uses a greedy algorithm of getting the items with the biggest weight/value first.
# Input: The number of items avaliable, tuples with the items, the capacity of the backpack and a matrix with all the conflicts.
# Output: A binary vector with a solution, an integer with the value of the solution and another integer with the weight of the solution. 
def greedyUnreason(num_items, items, capacity, conflicts):
    solution_weight = 0
    solution_value = 0
    solution = [0]*num_items

    # Sorting items for the reason value/weight as a Greedy Algorithm.
    items = sorted(items, key = attrgetter('unreason'), reverse = True)

    # Check every item
    for item in items:
        if solution_weight + item.weight <= capacity: # If it fits the capacity, add the item.
            solution[item.index] = 1
            solution_value += item.value
            solution_weight += item.weight
            # Then, remove all the items that conflicts with the item in the backpack.
            for conflict in conflicts[item.index]:
                removeIndex(items, conflict)

    return solution, solution_value, solution_weight

# A function that uses a greedy algorithm of getting the items with the biggest value/weight first.
# Input: The number of items avaliable, tuples with the items, the capacity of the backpack and a matrix with all the conflicts.
# Output: A binary vector with a solution, an integer with the value of the solution and another integer with the weight of the solution. 
def greedyReason(num_items, items, capacity, conflicts):
    solution_weight = 0
    solution_value = 0
    solution = [0]*num_items

    # Sorting items for the reason value/weight as a Greedy Algorithm.
    items = sorted(items, key = attrgetter('reason'), reverse = True)

    # Check every item
    for item in items:
        if solution_weight + item.weight <= capacity: # If it fits the capacity, add the item.
            solution[item.index] = 1
            solution_value += item.value
            solution_weight += item.weight
            # Then, remove all the items that conflicts with the item in the backpack.
            for conflict in conflicts[item.index]:
                removeIndex(items, conflict)

    return solution, solution_value, solution_weight

# A function that uses a greedy algorithm of getting the items with the biggest value first.
# Input: The number of items avaliable, tuples with the items, the capacity of the backpack and a matrix with all the conflicts.
# Output: A binary vector with a solution, an integer with the value of the solution and another integer with the weight of the solution. 
def greedyHelp(num_items, items, capacity, conflicts):
    solution_weight = 0
    solution_value = 0
    solution = [0]*num_items

    # Sorting items for the reason value/weight as a Greedy Algorithm.
    items = sorted(items, key = attrgetter('value'), reverse = True)

    for item in items:
        if solution_weight + item.weight <= capacity: # If it fits the capacity, add the item.
            solution[item.index] = 1
            solution_value += item.value
            solution_weight += item.weight
            # Then, remove all the items that conflicts with the item in the backpack.
            for conflict in conflicts[item.index]:
                removeIndex(items, conflict)

    return solution, solution_value, solution_weight

# A function that uses a greedy algorithm of getting the items with the smallest weight first.
# Input: The number of items avaliable, tuples with the items, the capacity of the backpack and a matrix with all the conflicts.
# Output: A binary vector with a solution, an integer with the value of the solution and another integer with the weight of the solution. 
def greedyWeight(num_items, items, capacity, conflicts):
    solution_weight = 0
    solution_value = 0
    solution = [0]*num_items

    # Sorting items for the reason value/weight as a Greedy Algorithm.
    items = sorted(items, key = attrgetter('weight'), reverse = False)

    for item in items:
        if solution_weight + item.weight <= capacity: # If it fits the capacity, add the item.
            solution[item.index] = 1
            solution_value += item.value
            solution_weight += item.weight
            # Then, remove all the items that conflicts with the item in the backpack.
            for conflict in conflicts[item.index]:
                removeIndex(items, conflict)

    return solution, solution_value, solution_weight

# Function to prepare the data and call the function that will really solve the problem.
# Input: First line with how many items are avaliable, how much cost we can spend and how many conflicts between items therea are.
#        Then, a line for every item with a first value(how much the item helps in the mission) and a second value(how much it cost).
#        At the end, a line for every conflict, with the two values for the items that conflict.
def solve_it(input_data):
    lines = input_data.split('\n') # Splits the lines.

    firstLine = lines[0].split() # Gets the first line
    item_count = int(firstLine[0]) # Gets how many items there are.
    capacity = int(firstLine[1])  # Gets how much it can cost.
    conflict_count = int(firstLine[2]) # Gets how many conflicts there are.

    items = []
    conflicts = []

    # Reads all the items
    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1]),(int(parts[0])/int(parts[1])),(int(parts[1]))/(int(parts[0]))))

    # Reads all the conflicts.
    for i in range(1, conflict_count+1):
        line = lines[item_count + i]
        parts = line.split()
        conflicts.append((int(parts[0]), int(parts[1])))

    # Call the function that will solve the problem.
    return knapsackNaive(item_count, items, capacity, conflict_count, conflicts)

# A function that solves the knapsack problem.
# Input: The number of items avaliable, tuples with the items, the capacity of the backpack, lines with all the conflicts and the number of conflicts.
# Output: A string with the solution value and the solution itself. 
def knapsackNaive(num_items, items, capacity, num_conflicts, conflicts):
    solution = [0]*num_items # Creates a vector with the number of items.
    solution_value = 0 # The total value for the solution.
    solution_weight = 0 # The total cost for the solution.

    # Transform the conflict's lines in conflict's matrix.
    conflicts = treatConflicts(conflicts, num_items)

    # If there aren't many items, use brute force and find the optimal solution.
    if(num_items <= 30):
        solution, solution_value, solution_weight = bruteForce(num_items, items, capacity, conflicts)

    # Else, try greedy solutions and simple trades.
    else:
        # Find a solution with the greedy algorithm of picking the items with the best value/weight.
        solution, solution_value, solution_weight = greedyReason(num_items, items, capacity, conflicts)
        # Find a solution with the greedy algorithm of picking the items with the best value.
        aux_solution, aux_solution_value, aux_solution_weight = greedyHelp(num_items, items, capacity, conflicts)

        # If the value of the second greedy algorithm is better than the first one, this is the new solution.
        if(aux_solution_value > solution_value):
            solution = aux_solution
            solution_value = aux_solution_value
            solution_weight = aux_solution_weight

        # Find a solution with the greedy algorithm of picking the items with the best weight.
        aux_solution, aux_solution_value, aux_solution_weight = greedyWeight(num_items, items, capacity, conflicts)

        # If the value of the second greedy algorithm is better than the first one, this is the new solution.
        if(aux_solution_value > solution_value):
            solution = aux_solution
            solution_value = aux_solution_value
            solution_weight = aux_solution_weight

        # Find a solution with the greedy algorithm of picking the items with the best weight/value.
        aux_solution, aux_solution_value, aux_solution_weight = greedyUnreason(num_items, items, capacity, conflicts)

        # If the value of the second greedy algorithm is better than the first one, this is the new solution.
        if(aux_solution_value > solution_value):
            solution = aux_solution
            solution_value = aux_solution_value
            solution_weight = aux_solution_weight

        # Try to improve the best solution yet by trying to trade one item for other.
        solution = trocaSimples(num_items, items, capacity, conflicts, solution)
        solution_value = calculateValue(solution, items)
        solution_weight = calculateWeight(solution, items)
        
        # Try to improve the best solution yet by trying to trade one item for two others.
        solution = trocaDupla(num_items, items, capacity, conflicts, solution)
        solution_value = calculateValue(solution, items)
        solution_weight = calculateWeight(solution, items)

    # Prepare the solution in the specified output format
    output_data = str(solution_value) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        # Reads the file that is supposed to be solved.
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        # Call the function to solve the problem.
        output_data = solve_it(input_data)
        # Print the solution
        print(output_data)
        # Writes the solution in a new file.
        solution_file = open(file_location + ".sol", "w")
        solution_file.write(output_data)
        solution_file.close()
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')