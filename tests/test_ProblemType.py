import pytest

import flopt
from flopt.constants import VariableType, ExpressionType
import flopt.solvers


def test_to_problem_type1():
    x = flopt.Variable("x", cat="Continuous")
    prob = flopt.Problem()
    prob += x
    problem_type = prob.to_problem_type()
    assert problem_type == {
        "Variable": VariableType.Continuous,
        "Objective": ExpressionType.Linear,
        "Constraint": ExpressionType.Non,
    }


def test_to_problem_type2():
    x = flopt.Variable("x", cat="Continuous")
    prob = flopt.Problem()
    prob += x * x
    problem_type = prob.to_problem_type()
    assert problem_type == {
        "Variable": VariableType.Continuous,
        "Objective": ExpressionType.Quadratic,
        "Constraint": ExpressionType.Non,
    }


def test_to_problem_type3():
    x = flopt.Variable("x", cat="Continuous")
    prob = flopt.Problem()
    prob += x * x * x
    problem_type = prob.to_problem_type()
    assert problem_type == {
        "Variable": VariableType.Continuous,
        "Objective": ExpressionType.Any,
        "Constraint": ExpressionType.Non,
    }


def test_to_problem_type4():
    x = flopt.Variable("x", cat="Continuous")
    prob = flopt.Problem()
    prob += x * x
    prob += x <= 3
    problem_type = prob.to_problem_type()
    assert problem_type == {
        "Variable": VariableType.Continuous,
        "Objective": ExpressionType.Quadratic,
        "Constraint": ExpressionType.Linear,
    }


def test_to_problem_type5():
    x = flopt.Variable("x", cat="Continuous")
    prob = flopt.Problem()
    prob += x * x
    prob += x * x <= 3
    problem_type = prob.to_problem_type()
    assert problem_type == {
        "Variable": VariableType.Continuous,
        "Objective": ExpressionType.Quadratic,
        "Constraint": ExpressionType.Quadratic,
    }


def test_to_problem_type6():
    x = flopt.Variable("x", lowBound=0, upBound=10, cat="Permutation")
    prob = flopt.Problem()
    prob += x
    problem_type = prob.to_problem_type()
    assert problem_type == {
        "Variable": VariableType.Permutation,
        "Objective": ExpressionType.Any,
        "Constraint": ExpressionType.Non,
    }


def test_to_problem_type7():
    x = flopt.Variable.array("x", 1, cat="Spin")
    prob = flopt.Problem()
    prob += flopt.Prod(x)
    problem_type = prob.to_problem_type()
    assert problem_type == {
        "Variable": VariableType.Binary,
        "Objective": ExpressionType.Linear,
        "Constraint": ExpressionType.Non,
    }


def test_to_problem_type8():
    x = flopt.Variable.array("x", 2, cat="Spin")
    prob = flopt.Problem()
    prob += flopt.Prod(x)
    problem_type = prob.to_problem_type()
    assert problem_type == {
        "Variable": VariableType.Binary,
        "Objective": ExpressionType.Quadratic,
        "Constraint": ExpressionType.Non,
    }


def test_to_problem_type9():
    x = flopt.Variable.array("x", 10, cat="Spin")
    prob = flopt.Problem()
    prob += flopt.Prod(x)
    problem_type = prob.to_problem_type()
    assert problem_type == {
        "Variable": VariableType.Binary,
        "Objective": ExpressionType.Any,
        "Constraint": ExpressionType.Non,
    }


def test_to_problem_type10():
    x = flopt.Variable.array("x", 10, cat="Spin")
    prob = flopt.Problem()
    prob += flopt.Sum(x)
    problem_type = prob.to_problem_type()
    assert problem_type == {
        "Variable": VariableType.Binary,
        "Objective": ExpressionType.Linear,
        "Constraint": ExpressionType.Non,
    }
