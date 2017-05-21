from collections import defaultdict
assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Check each unit
    for unit in unitlist:

        # naked twin candidates have a "value" for the box with a length of 2 (only 2 possible digits)
        # there should be exactly two boxes that have a particular value
        possibleTwins = defaultdict(list)
        [possibleTwins[values[box]].append(box) for box in unit if len(values[box]) == 2]

        # If there are two of these twins for a given value within a unit, then we have a naked twin
        for k,v in possibleTwins.items():
            if len(v) == 2:
                # Remove the naked twin values from possible solutions
                dplaces = [box for box in unit if box not in v]
                for place in dplaces:
                    old = values[place]
                    s1 = values[place].replace(k[0],'')
                    s2 = s1.replace(k[1],'')
                    assign_value(values, place, s2)

    return values


"""
Set up the units - most of this is borrowed from quiz solutions. However, to implement diagonal sudoku, we add
two additional units
"""

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

boxes = cross(rows, cols) 

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# Create diagonal units
diagonal_units = [['A1','B2','C3','D4','E5','F6','G7','H8','I9'],['A9','B8','C7','D6','E5','F4','G3','H2','I1']]
# Add diagonal units to the unitlist
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Note: Implementation copied from quiz solutions
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    out = {}
    for i,g in enumerate(grid):
        row = str(chr(ord('A') + i//9))
        col = str(i%9 + 1)
        if g == '.':
            out[row+col] = "123456789"
        else:
            out[row+col] = g
    return out


def display(values):
    """
    Display the values as a 2-D grid.
    Note: Implementation copied from quiz solutions
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    Note: Implementation copied from quiz solutions
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit,''))
    return values

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    Note: Implementation copied from quiz solutions
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
                #values[dplaces[0]] = digit
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice() and naked_twins. If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    Note: Implementation borrowed from quiz solutions with the addition of naked twins 
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        # reduce further via naked twins
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form or False if no solution found
    DFS of possible puzzle solutions
    """
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values

    # Choose one of the unfilled squares with the fewest possibilities by sorting based on the 
    # smallest number of possible solutions (length of the string)
    choices = [(values[v],v) for v in values.keys() if len(values[v]) > 1]
    choices = sorted(choices, key=lambda x: len(x))

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    value,c = choices[0]
    for v in value:
        # make a copy of the dictionary before we modify it
        newpuzzle = values.copy()


        assign_value(newpuzzle, c, v)
        #newpuzzle[c] = v

        # give this solution a shot and if we found one, return
        result = search(newpuzzle)
        if result:
            return result 

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
