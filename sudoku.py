from flopt import Variable, Problem, Solver, Sum, Const, Value

# A list of number sequence
Sequence = list(range(9))

# The Vals, Rows and Cols sequences all follow this form
Vals = Sequence
Rows = Sequence
Cols = Sequence

# The starting numbers are entered as constraints
sudoku = [
    # value, row, col
    (1, 0, 7),
    (4, 1, 0),
    (2, 2, 1),
    (5, 3, 4), (4, 3, 6), (7, 3, 8),
    (8, 4, 2), (3, 4, 6),
    (1, 5, 2), (9, 5, 4),
    (3, 6, 0), (4, 6, 3), (2, 6, 6),
    (5, 7, 1), (1, 7, 3),
    (8, 8, 3), (6, 8, 5),
]

# The problem variables are created
choices = Variable.array("Choice", (9, 9, 9), cat='Binary')

# The starting numbers are entered as constant
for value, row, col in sudoku:
    choices[value-1, row, col] = Const(1)

# display board
print('before')
row_line = "+-------+-------+-------+"
print(row_line)
for r in Rows:
    if r in {3, 6}:
        print(row_line)
    for c in Cols:
        if c in {0, 3, 6}:
            print("| ", end='')
        if any(Value(choices[v, r, c]) == 1 for v in Vals):
            for v in Vals:
                if Value(choices[v, r, c]) == 1:
                    print(f'{v+1} ', end='')
        else:
            print(f'  ', end='')
        if c == 8:
            print("|")
print(row_line)

# The prob variable is created to contain the problem data
prob = Problem("Sudoku")

# A constraint ensuring that only one value can be in each square is created
for r in Rows:
    for c in Cols:
        prob += Sum(choices[:, r, c]) == 1

# The row, column and box constraints are added for each value
for v in Vals:
    for r in Rows:
        prob += Sum(choices[v, r, :]) == 1

    for c in Cols:
        prob += Sum(choices[v, :, c]) == 1

    for r in [0, 3, 6]:
        for c in [0, 3, 6]:
            prob += Sum(choices[v, r:r+3, c:c+3]) == 1

print(prob)

solver = Solver('PulpSearch')
prob.solve(solver, msg=True)

# display result
row_line = "+-------+-------+-------+"
print(row_line)
for r in Rows:
    if r in {3, 6}:
        print(row_line)
    for c in Cols:
        for v in Vals:
            if choices[v, r, c].value() == 1:
                if c in {0, 3, 6}:
                    print("| ", end='')
                print(f'{v+1} ', end='')
                if c == 8:
                    print("|")
print(row_line)


from flopt.convert import LpStructure
lp = LpStructure.fromFlopt(prob)
print(lp)
