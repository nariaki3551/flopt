from flopt.constants import VariableType, ExpressionType

algo_list = [
    "RandomSearch",
    "2-Opt",
    "OptunaTPESearch",
    "OptunaCmaEsSearch",
    "HyperoptTPESearch",
    "SFLA",
    "PulpSearch",
    "ScipySearch",
    "ScipyMilpSearch",
    "CvxoptQpSearch",
    # "AmplifySearch",
    "auto",
]


def Solver(algo="auto"):
    """
    Obtain Solver object.

    Parameters
    ----------
    algo : str
      algorithm name

    Returns
    -------
    Solver object
       return Solver
    """
    if algo == "RandomSearch":
        from flopt.solvers.random_search import RandomSearch

        return RandomSearch()
    elif algo == "2-Opt":
        from flopt.solvers.two_opt import TwoOpt

        return TwoOpt()
    elif algo == "OptunaTPESearch":
        from flopt.solvers.optuna_searches import OptunaTPESearch

        return OptunaTPESearch()
    elif algo == "OptunaCmaEsSearch":
        from flopt.solvers.optuna_searches import OptunaCmaEsSearch

        return OptunaCmaEsSearch()
    elif algo == "HyperoptTPESearch":
        from flopt.solvers.hyperopt_search import HyperoptTPESearch

        return HyperoptTPESearch()
    elif algo == "SFLA":
        from flopt.solvers.shuffled_frog_leaping_search import ShuffledFrogLeapingSearch

        return ShuffledFrogLeapingSearch()
    elif algo == "PulpSearch":
        from flopt.solvers.pulp_search import PulpSearch

        return PulpSearch()
    elif algo == "ScipySearch":
        from flopt.solvers.scipy_searches import ScipySearch

        return ScipySearch()
    elif algo == "ScipyMilpSearch":
        from flopt.solvers.scipy_searches import ScipyMilpSearch

        return ScipyMilpSearch()
    elif algo == "CvxoptQpSearch":
        from flopt.solvers.cvxopt_qp_search import CvxoptQpSearch

        return CvxoptQpSearch()
    elif algo == "AmplifySearch":
        from flopt.solvers.amplify_search import AmplifySearch

        return AmplifySearch()
    elif algo == "auto":
        from flopt.solvers.auto_search import AutoSearch

        return AutoSearch()
    else:
        assert True, f"{algo} is not available, choices from {Solver_list()}"


def Solver_list():
    """
    Obtain useable solver list

    Returns
    -------
    list
      return list of algorithm names
    """
    return algo_list


def allAvailableSolvers(prob):
    """Obtain all available solvers to solve the problem

    Parameters
    ----------
    prob : Problem
        problem

    Returns
    -------
    list of str
        algorithm names that can solve the problem

    Examples
    --------


    .. code-block:: python

        import flopt
        from flopt import Variable, Problem, CustomExpression

        # Linear problem without constraint
        a = Variable("a", 0, 1, "Integer")
        b = Variable("b", 1, 2, "Continuous")
        c = Variable("c", 1, 3, "Continuous")
        prob_linear = Problem(name="Only objective")
        prob_linear += a + b + c

        # Problem with constraint
        prob_with_const = Problem(name="With constraint")
        prob_with_const += a + b + c
        prob_with_const += a + b >= 2

        # Non-Linear problem
        prob_nonlinear = Problem("Non Linear")
        prob_nonlinear += a*b*c
        prob_nonlinear += a + b >= 2

        # Permutation Problem
        p = Variable("p", 0, 4, "Permutation")
        prob_perm = Problem("TestP")
        def obj(p):
            return p[-1] - p[0]
        prob_perm +=  CustomExpression(obj, [p])

        # display solvers can solve prob_linear
        print(flopt.allAvailableSolvers(prob_linear)

        # display solvers can solve prob_with_const
        print(flopt.allAvailableSolvers(prob_with_const))

        # display solvers can solve prob_nonlinear
        print(flopt.allAvailableSolvers(prob_nonlinear))

        # display solvers can solve prob_perm
        print(flopt.allAvailableSolvers(prob_perm))
    """
    available_solvers = [
        algo for algo in Solver_list() if Solver(algo=algo).available(prob)
    ]
    return available_solvers


def allAvailableSolversProblemType(problem_type):
    """
    Parameters
    ----------
    problem_type : dict
        key is "Variable", "Objective", "Constraint"

    Returns
    -------
    list of str
        algorithm names that can solve the problem

    Examples
    --------

    .. code-block:: python

        import flopt.constants
        import flopt.solvers

        problem_type = dict(
            Variable=flopt.constants.VariableType.Number,
            Objective=flopt.constants.ExpressionType.BlackBox,
            Constraint=None
        )

        flopt.solvers.allAvailableSolversProblemType(problem_type)

    """
    available_solvers = [
        algo
        for algo in Solver_list()
        if Solver(algo=algo).availableProblemType(problem_type)
    ]
    return available_solvers


def estimate_problem_type_info(prob):
    """Estimate problem types

    Parameters
    ----------
    prob : Problem
    """
    from flopt.solvers.selector import (
        lp,
        mip,
        ising,
        qp,
        permutation,
        blackbox,
        blackbox_mip,
        nonlinear,
        nonlinear_mip,
    )

    problem_classes = [
        (lp, "lp"),
        (mip, "mip"),
        (ising, "ising"),
        (qp, "quadratic"),
        (permutation, "permutation"),
        (blackbox, "blackbox"),
        (blackbox_mip, "blackbox with interger variables"),
        (nonlinear, "nonlinear"),
        (nonlinear_mip, "nonlinear with integer variables"),
    ]

    def check(problem_type, problem_class):
        is_problem_class = (
            problem_type["Variable"].expand() <= problem_class["Variable"].expand()
            and problem_type["Objective"].expand()
            <= problem_class["Objective"].expand()
            and problem_type["Constraint"].expand()
            <= problem_class["Constraint"].expand()
        )
        return is_problem_class

    problem_type = prob.toProblemType()

    print("Problem")
    print(prob.__str__(prefix="\t"))
    print()
    print("Problem components")
    print(f"\tVariable: {problem_type['Variable']}")
    print(f"\tObjective: {problem_type['Objective']}")
    print(f"\tConstraint: {problem_type['Constraint']}")
    print()
    print("Included problem classes")
    for problem_class, name in problem_classes:
        if is_problem_class := check(problem_type, problem_class):
            print("\t-->", name)
        else:
            print("\t   ", name)
