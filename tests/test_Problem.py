from flopt import Variable, Problem, CustomObject

a = Variable('a', iniValue=0, cat='Binary')
b = Variable('b', iniValue=2, cat='Continuous')
prob = Problem()

def test_Problem_obj():
    prob = Problem()
    prob.setObjective(a+b)
    assert prob.getObjectiveValue() == 2

def test_Problem_obj2():
    prob = Problem()
    prob += a + 2*b
    assert prob.getObjectiveValue() == 4

def test_Problem_obj3():
    prob = Problem()
    prob += 1
    assert prob.getObjectiveValue() == 1
