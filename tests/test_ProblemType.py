import pytest

import flopt
from flopt.constants import VariableType, ExpressionType
import flopt.solvers


def test_toProblemType1():
    x = flopt.Variable("x", cat="Continuous")
    prob = flopt.Problem()
    prob += x
    problem_type = prob.toProblemType()
    assert problem_type == {
        "Variable": VariableType.Continuous,
        "Objective": ExpressionType.Linear,
        "Constraint": ExpressionType.Non,
    }


def test_toProblemType2():
    x = flopt.Variable("x", cat="Continuous")
    prob = flopt.Problem()
    prob += x * x
    problem_type = prob.toProblemType()
    assert problem_type == {
        "Variable": VariableType.Continuous,
        "Objective": ExpressionType.Quadratic,
        "Constraint": ExpressionType.Non,
    }


def test_toProblemType3():
    x = flopt.Variable("x", cat="Continuous")
    prob = flopt.Problem()
    prob += x * x * x
    problem_type = prob.toProblemType()
    assert problem_type == {
        "Variable": VariableType.Continuous,
        "Objective": ExpressionType.Any,
        "Constraint": ExpressionType.Non,
    }


def test_toProblemType4():
    x = flopt.Variable("x", cat="Continuous")
    prob = flopt.Problem()
    prob += x * x
    prob += x <= 3
    problem_type = prob.toProblemType()
    assert problem_type == {
        "Variable": VariableType.Continuous,
        "Objective": ExpressionType.Quadratic,
        "Constraint": ExpressionType.Linear,
    }


def test_toProblemType5():
    x = flopt.Variable("x", cat="Continuous")
    prob = flopt.Problem()
    prob += x * x
    prob += x * x <= 3
    problem_type = prob.toProblemType()
    assert problem_type == {
        "Variable": VariableType.Continuous,
        "Objective": ExpressionType.Quadratic,
        "Constraint": ExpressionType.Quadratic,
    }


def test_toProblemType6():
    x = flopt.Variable("x", lowBound=0, upBound=10, cat="Permutation")
    prob = flopt.Problem()
    prob += x
    problem_type = prob.toProblemType()
    assert problem_type == {
        "Variable": VariableType.Permutation,
        "Objective": ExpressionType.Any,
        "Constraint": ExpressionType.Non,
    }


def test_toProblemType7():
    x = flopt.Variable.array("x", 1, cat="Spin")
    prob = flopt.Problem()
    prob += flopt.Prod(x)
    problem_type = prob.toProblemType()
    assert problem_type == {
        "Variable": VariableType.Binary,
        "Objective": ExpressionType.Linear,
        "Constraint": ExpressionType.Non,
    }


def test_toProblemType8():
    x = flopt.Variable.array("x", 2, cat="Spin")
    prob = flopt.Problem()
    prob += flopt.Prod(x)
    problem_type = prob.toProblemType()
    assert problem_type == {
        "Variable": VariableType.Binary,
        "Objective": ExpressionType.Quadratic,
        "Constraint": ExpressionType.Non,
    }


def test_toProblemType9():
    x = flopt.Variable.array("x", 10, cat="Spin")
    prob = flopt.Problem()
    prob += flopt.Prod(x)
    problem_type = prob.toProblemType()
    assert problem_type == {
        "Variable": VariableType.Binary,
        "Objective": ExpressionType.Any,
        "Constraint": ExpressionType.Non,
    }


def test_toProblemType10():
    x = flopt.Variable.array("x", 10, cat="Spin")
    prob = flopt.Problem()
    prob += flopt.Sum(x)
    problem_type = prob.toProblemType()
    assert problem_type == {
        "Variable": VariableType.Binary,
        "Objective": ExpressionType.Linear,
        "Constraint": ExpressionType.Non,
    }
