from flopt import Variable
from flopt.variable import VarElement, VarBinary, VarInteger, VarContinuous, VarConst
from flopt.expression import Expression, ExpressionConst, CustomExpression


class LinearizeError(Exception):
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
    mul_vars = dict()
    prob.obj = prob.obj.expand()
    linearize_expression(prob.obj, mul_vars)
    for const in prob.constraints:
        const.expression = const.expression.expand()
        linearize_expression(const.expression, mul_vars)

    # add constraints for variable-multipry
    for (var_a, var_b), mul_var in mul_vars.items():
        # (Binary, Binary)
        if {type(var_a), type(var_b)} == {VarBinary}:
            prob += mul_var <= var_a,               f'for_{mul_var.name}_1'
            prob += mul_var <= var_b,               f'for_{mul_var.name}_2'
            prob += mul_var >= var_a + var_b - 1,   f'for_{mul_var.name}_3'
        # (Binary, Integer)
        elif {type(var_a), type(var_b)} == {VarBinary, VarInteger}:
            if isinstance(var_a, VarBinary):
                var_bin, var_int = var_a, var_b
            else:
                var_bin, var_int = var_b, var_a
            l, u = var_int.getLb(), var_int.getUb()
            prob += mul_var >= l * var_bin,                 f'for_{mul_var.name}_1'
            prob += mul_var <= u * var_bin,                 f'for_{mul_var.name}_2'
            prob += mul_var >= var_int - u * (1 - var_bin), f'for_{mul_var.name}_3'
            prob += mul_var <= var_int - l * (1 - var_bin), f'for_{mul_var.name}_4'
        #  (Binary, Continuous)
        elif {type(var_a), type(var_b)} == {VarBinary, VarContinuous}:
            if isinstance(var_a, VarBinary):
                var_bin, var_con = var_a, var_b
            else:
                var_bin, var_con = var_b, var_a
            l, u = var_con.getLb(), var_con.getUb()
            prob += mul_var >= l * var_bin,                 f'for_{mul_var.name}_1'
            prob += mul_var <= u * var_bin,                 f'for_{mul_var.name}_1'
            prob += mul_var >= var_con - l * (1 - var_bin), f'for_{mul_var.name}_1'
            prob += mul_var <= var_con - u * (1 - var_bin), f'for_{mul_var.name}_1'


def linearize_expression(e, mul_vars):
    """linearize a expression

    Parameters
    ----------
    e : Expresson or VarElement
    mul_vars : dict
        mul_vars[var_a, var_b] = var_c, where var_c = var_a * var_b
    """
    if isinstance(e, (VarElement, VarConst, ExpressionConst)):
        return
    finish = False
    while not finish:
        finish = not linearize_traverse(e, mul_vars)


def linearize_traverse(e, mul_vars):
    """subroutine of linearize_expression

    Parameters
    ----------
    e : Expresson or VarElement
    mul_vars : dict
        mul_vars[var_a, var_b] = var_c, where var_c = var_a * var_b

    Returns
    -------
    bool
        return true if a expession is linearized else false
    """
    assert isinstance(e, Expression)
    convert = False
    for node in e.traverse():
        if isinstance(node, Expression):
            reduced = False
            if is_mul_var(node.elmA):
                if not is_linearable_mul_var(node.elmA):
                    raise LinearizeError()
                node.elmA = create_mul_var(node.elmA, mul_vars)
                reduced = True
            if is_mul_var(node.elmB):
                if not is_linearable_mul_var(node.elmB):
                    raise LinearizeError()
                node.elmB = create_mul_var(node.elmB, mul_vars)
                reduced = True
            if reduced:
                node.setName()
                for parent in node.traverseAncestors():
                    parent.setName()
                convert = True
    return convert


def create_mul_var(node, mul_vars):
    """create new variable and replace variable-multiply to it
    Parameters
    ----------
    node : Expression
    mul_vars : dict
        stocked multiplized variables
    """
    var_a, var_b = sorted([node.elmA, node.elmB], key=lambda x: x.name)
    if (var_a, var_b) not in mul_vars:
        if {var_a.getType(), var_b.getType()} == {'VarBinary'}:
            mul_var = Variable(
                f'mul_{len(mul_vars)}',
                cat='Binary',
                ini_value=var_a.value() * var_b.value(),
            )
        elif {var_a.getType(), var_b.getType()} == {'VarBinary', 'VarInteger'}:
            mul_var = Variable(
                f'mul_{len(mul_vars)}',
                cat='Integer',
                ini_value=var_a.value() * var_b.value(),
            )
        elif {var_a.getType(), var_b.getType()} == {'VarBinary', 'VarContinuous'}:
            mul_var = Variable(
                f'mul_{len(mul_vars)}',
                cat='Continuous',
                ini_value=var_a.value() * var_b.value(),
            )
        mul_vars[var_a, var_b] = mul_var
    return mul_vars[var_a, var_b]


def is_mul_var(node):
    """
    Parameters
    ----------
    node : Expression or VarElement

    Returns
    -------
    bool
        return true if node is Expression and variable-multiply else false
    """
    return isinstance(node, Expression)\
        and node.operater == '*'\
        and isinstance(node.elmA, VarElement)\
        and isinstance(node.elmB, VarElement)


def is_linearable_mul_var(node):
    """
    Parameters
    ----------
    node : Expression or VarElement

    Returns
    -------
    bool
        return true if node is Expression and variable-multiply
    """
    if is_mul_var(node):
        linearable_pairs = [
            {'VarBinary',  'VarBinary'},
            {'VarBinary',  'VarInteger'},
            {'VarBinary',  'VarContinuous'},
            {'VarInteger', 'VarInteger'},
            {'VarInteger', 'VarContinuous'},
        ]
        return {node.elmA.getType(), node.elmB.getType()} in linearable_pairs
    else:
        return False

