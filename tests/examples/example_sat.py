from flopt import Variable, Problem, Solver, CustomObject

__doc__ = """
This is a sample code of "MAXSAT"
max (c1+2*c2+3*c3+4*c4)
s.t. c1 = x0 or x1
     c2 = x0 or not x1
     c3 = not x0 or x1
     c4 = not x0 or not x1
     x0, x1 is Binary
"""
DISPLAY = False


# literals
x0 = Variable('x0', cat='Binary')
x1 = Variable('x1', cat='Binary')

# clauses
clause1 = x0 | x1
clause2 = x0 | ~x1
clause3 = ~x0 | x1
clause4 = ~x0 | ~x1

clauses = [clause1, clause2, clause3, clause4]
weights = [1, 2, 3, 4]
obj = sum(w*c for c, w in zip(clauses, weights))

prob = Problem('MaxSat', sense='maximize')
prob += obj

solver = Solver(algo='RandomSearch')
prob.solve(solver, timelimit=2, msg=True)

print('value x0', x0.value())
print('value x1', x1.value())
for clause in clauses:
    print(clause)
