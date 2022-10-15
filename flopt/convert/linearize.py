from flopt.variable import Variable, VarElement
from flopt.expression import Expression, Const
from flopt.convert.binarize import binarize
from flopt.constants import VariableType
from flopt.env import setup_logger, create_variable_mode

logger = setup_logger(__name__)


class LinearizeError(Exception):
    pass


class NeedToBinarize(Exception):
    pass


def linearize(prob):
    """linearize of problem

    Parameters
    ----------
    prob : Problem

    Examples
    --------

    .. code-block:: python

        from flopt import Variable, Problem

        x = Variable.array('x', 3, cat='Binary')

        prob = Problem()
        prob += x[0] - 2*x[1] - x[0]*x[1]*x[2]
        print('[ original ]')
        print(prob.show())

        from flopt.convert import linearize
        linearize(prob)
        print('[ linearized ])
        print(prob.show())

    ::

        [ original ]
         Name: None
          Type         : Problem
          sense        : minimize
          objective    : x_0-(2*x_1)-((x_0*x_1)*x_2)
          #constraints : 0
          #variables   : 3 (Binary 3)


        [ linearized ]
         Name: None
          Type         : Problem
          sense        : minimize
          objective    : 0-mul_1+x_0-(2*x_1)
          #constraints : 6
          #variables   : 5 (Binary 5)

          C 0, name for_mul_0_1, mul_0-x_0 <= 0
          C 1, name for_mul_0_2, mul_0-x_1 <= 0
          C 2, name for_mul_0_3, mul_0-(x_0+x_1-1) >= 0
          C 3, name for_mul_1_1, mul_1-mul_0 <= 0
          C 4, name for_mul_1_2, mul_1-x_2 <= 0
          C 5, name for_mul_1_3, mul_1-(mul_0+x_2-1) >= 0

    """
    try:
        var_muls = dict()
        prob.setObjective(linearize_expression(prob.obj, var_muls))
        for const in prob.getConstraints():
            const.expression = linearize_expression(const.expression, var_muls)
    except NeedToBinarize:
        logger.info(
            f"problem will be binarized because it includes dislinearable multipry"
        )
        return linearize(binarize(prob))
    except LinearizeError as e:
        logger.error(f"this problem can not be linearized")
    except Exception as e:
        raise e

    # add constraints for variable-multipry
    for (var_a, var_b), var_mul in var_muls.items():
        # (Binary, Binary)
        if {var_a.type(), var_b.type()} == {VariableType.Binary}:
            prob += var_mul <= var_a, f"for_{var_mul.name}_1"
            prob += var_mul <= var_b, f"for_{var_mul.name}_2"
            prob += var_mul >= var_a + var_b - 1, f"for_{var_mul.name}_3"
        # (Binary, Integer)
        elif {var_a.type(), var_b.type()} == {
            VariableType.Binary,
            VariableType.Integer,
        }:
            if var_a.type() == VariableType.Binary:
                var_bin, var_int = var_a, var_b
            else:
                var_bin, var_int = var_b, var_a
            l = var_int.getLb(must_number=True)
            u = var_int.getUb(must_number=True)
            prob += var_mul >= l * var_bin, f"for_{var_mul.name}_1"
            prob += var_mul <= u * var_bin, f"for_{var_mul.name}_2"
            prob += var_mul >= var_int - u * (1 - var_bin), f"for_{var_mul.name}_3"
            prob += var_mul <= var_int - l * (1 - var_bin), f"for_{var_mul.name}_4"
        #  (Binary, Continuous)
        elif {var_a.type(), var_b.type()} == {
            VariableType.Binary,
            VariableType.Continuous,
        }:
            if var_a.type() == VariableType.Binary:
                var_bin, var_con = var_a, var_b
            else:
                var_bin, var_con = var_b, var_a
            l = var_con.getLb(must_number=True)
            u = var_con.getUb(must_number=True)
            prob += var_mul >= l * var_bin, f"for_{var_mul.name}_1"
            prob += var_mul <= u * var_bin, f"for_{var_mul.name}_2"
            prob += var_mul >= var_con - l * (1 - var_bin), f"for_{var_mul.name}_3"
            prob += var_mul <= var_con - u * (1 - var_bin), f"for_{var_mul.name}_4"

    prob.resetVariables()
    return prob


def linearize_expression(e, var_muls):
    """linearize a expression

    Parameters
    ----------
    e : Expresson or VarElement
    var_muls : dict
        var_muls[var_a, var_b] = var_c, where var_c = var_a * var_b
    """
    if isinstance(e, (VarElement, Const)):
        return e
    if e.isLinear():
        return e
    e.resetlinkChildren()

    finish = False
    while not finish:
        finish, e = linearize_traverse(e, var_muls)
        if finish and not e.isLinear():
            e = e.expand()
            e.resetlinkChildren()
            finish = False
    return e


def linearize_traverse(e, var_muls):
    """subroutine of linearize_expression

    Parameters
    ----------
    e : Expresson or VarElement
    var_muls : dict
        var_muls[var_a, var_b] = var_c, where var_c = var_a * var_b

    Returns
    -------
    bool
        return true if a expession is linearized else false
    """
    if is_var_mul(e):
        if not is_linearable(e):
            raise LinearizeError()
        elif need_binarize(e):
            raise NeedToBinarize()
        var_mul = create_var_mul(e, var_muls)
        return True, var_mul

    for node in e.traverse():
        if isinstance(node, Expression):
            update = False
            if is_var_mul(node.elmA):
                if not is_linearable(node.elmA):
                    raise LinearizeError()
                elif need_binarize(node.elmA):
                    raise NeedToBinarize()
                node.elmA = create_var_mul(node.elmA, var_muls)
                update = True
            if is_var_mul(node.elmB):
                if not is_linearable(node.elmB):
                    raise LinearizeError()
                elif need_binarize(node.elmB):
                    raise NeedToBinarize()
                node.elmB = create_var_mul(node.elmB, var_muls)
                update = True
            if update:
                node.setName()
                node.setPolynomial()
                for parent in node.traverseAncestors():
                    parent.setName()
                    parent.setPolynomial()
                return False, e
    return True, e


def create_var_mul(node, var_muls):
    """create new variable and replace variable-multiply to it
    Parameters
    ----------
    node : Expression
    var_muls : dict
        stocked multiplized variables
    """
    var_a, var_b = sorted([node.elmA, node.elmB], key=lambda x: x.name)
    if (var_a, var_b) not in var_muls:
        # (Binary, Binary)
        if {var_a.type(), var_b.type()} == {VariableType.Binary}:
            with create_variable_mode():
                var_mul = Variable(
                    f"mul",
                    cat="Binary",
                    ini_value=var_a.value() * var_b.value(),
                )
        # (Binary, Integer)
        elif {var_a.type(), var_b.type()} == {
            VariableType.Binary,
            VariableType.Integer,
        }:
            with create_variable_mode():
                var_mul = Variable(
                    f"mul",
                    lowBound=get_lower_bound(var_a, var_b),
                    upBound=get_upper_bound(var_a, var_b),
                    cat="Integer",
                    ini_value=var_a.value() * var_b.value(),
                )
        #  (Binary, Continuous)
        elif {var_a.type(), var_b.type()} == {
            VariableType.Binary,
            VariableType.Continuous,
        }:
            with create_variable_mode():
                var_mul = Variable(
                    f"mul",
                    lowBound=get_lower_bound(var_a, var_b),
                    upBound=get_upper_bound(var_a, var_b),
                    cat="Continuous",
                    ini_value=var_a.value() * var_b.value(),
                )
        var_muls[var_a, var_b] = var_mul
    return var_muls[var_a, var_b]


def get_lower_bound(var_a, var_b):
    """calculate lower bound of var_a * var_b

    Notes
    -----
    pair of var_a and var_b type is only (VariableType.Binary, VariableType.Integer) or (VariableType.Binary, VariableType.Continuous)
    """
    assert {var_a.type(), var_b.type()} == {
        VariableType.Binary,
        VariableType.Integer,
    } or {var_a.type(), var_b.type()} == {VariableType.Binary, VariableType.Continuous}
    if var_a.type() == VariableType.Binary:
        var_binary, var_other = var_a, var_b
    else:
        var_binary, var_other = var_b, var_a
    if var_other.lowBound is None:
        return None
    return min(0, var_other.lowBound)


def get_upper_bound(var_a, var_b):
    """calculate upper bound of var_a * var_b

    Notes
    -----
    pair of var_a and var_b type is only (VariableType.Binary, VariableType.Integer) or (VariableType.Binary, VariableType.Continuous)
    """
    assert {var_a.type(), var_b.type()} == {
        VariableType.Binary,
        VariableType.Integer,
    } or {var_a.type(), var_b.type()} == {VariableType.Binary, VariableType.Continuous}
    if var_a.type() == VariableType.Binary:
        var_binary, var_other = var_a, var_b
    else:
        var_binary, var_other = var_b, var_a
    if var_other.upBound is None:
        return None
    return max(0, var_other.upBound)


def is_var_mul(node):
    """
    Parameters
    ----------
    node : Expression or VarElement

    Returns
    -------
    bool
        return true if node is Expression and variable-multiply else false
    """
    return (
        isinstance(node, Expression)
        and node.operator == "*"
        and isinstance(node.elmA, VarElement)
        and isinstance(node.elmB, VarElement)
    )


def is_linearable(node):
    """
    Parameters
    ----------
    node : Expression or VarElement

    Returns
    -------
    bool
        return true if node is Expression and variable-multiply
    """
    assert is_var_mul(node)
    linearable_pairs = [
        {VariableType.Binary, VariableType.Binary},
        {VariableType.Binary, VariableType.Integer},
        {VariableType.Binary, VariableType.Continuous},
        {VariableType.Binary, VariableType.Spin},
        {VariableType.Spin, VariableType.Spin},
        {VariableType.Spin, VariableType.Integer},
        {VariableType.Spin, VariableType.Continuous},
        {VariableType.Integer, VariableType.Integer},
        {VariableType.Integer, VariableType.Continuous},
    ]
    return {node.elmA.type(), node.elmB.type()} in linearable_pairs


def need_binarize(node):
    """
    Parameters
    ----------
    node : Expression or VarElement

    Returns
    -------
    bool
        return true if node must be binarized for linearize else false
    """
    assert is_var_mul(node)
    need_binarize_pairs = [
        {VariableType.Binary, VariableType.Spin},
        {VariableType.Spin, VariableType.Spin},
        {VariableType.Spin, VariableType.Integer},
        {VariableType.Spin, VariableType.Continuous},
        {VariableType.Integer, VariableType.Integer},
        {VariableType.Integer, VariableType.Continuous},
    ]
    return {node.elmA.type(), node.elmB.type()} in need_binarize_pairs
