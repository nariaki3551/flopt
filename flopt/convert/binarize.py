from flopt import Variable
from flopt.variable import VarElement, VarBinary, VarInteger, VarContinuous, VarConst
from flopt.expression import Expression, ExpressionConst, CustomExpression


def binarize(prob):
    """binarize of problem

    Parameters
    ----------
    prob : Problem

    Examples
    --------
    .. code-block:: python

        from flopt import Variable, Problem
        x = Variable.array('x', 2, cat='Binary')
        y = Variable.array('y', 1, lowBound=1, upBound=3, cat='Integer')
        x = np.hstack([x, y])

        prob = Problem()
        prob += x[2] * x[0] + x[1]
        print('[ original ]')
        print(prob.show())

        from flopt.convert import linearize, binarize
        binarize(prob)
        print('[ binarized ]')
        print(prob.show())

        linearize(prob)
        print('[ linearized ]')
        print(prob.show())

    ::

        [ original ]
         Name: None
          Type         : Problem
          sense        : minimize
          objective    : y_0*x_0+x_1
          #constraints : 0
          #variables   : 3 (Binary 2, Integer 1)

        [ binarized ]
         Name: None
          Type         : Problem
          sense        : minimize
          objective    : x_0*(1*bin_y_0_0+2*bin_y_0_1+3*bin_y_0_2)+x_1
          #constraints : 2
          #variables   : 6 (Binary 5, Integer 1)

          C 0, name for_bin_y_0_sum, bin_y_0_0+bin_y_0_2+bin_y_0_1-1 == 0
          C 1, name for_bin_y_0_eq, y_0-(1*bin_y_0_0+2*bin_y_0_1+3*bin_y_0_2) == 0

        [ linearized ]
         Name: None
          Type         : Problem
          sense        : minimize
          objective    : mul_0+2*mul_1+3*mul_2+x_1
          #constraints : 11
          #variables   : 9 (Binary 8, Integer 1)

          C 0, name for_bin_y_0_sum, bin_y_0_0+bin_y_0_1+bin_y_0_2-1 == 0
          C 1, name for_bin_y_0_eq, -bin_y_0_0-(2*bin_y_0_1)-(3*bin_y_0_2)+y_0 == 0
          C 2, name for_mul_0_1, mul_0-bin_y_0_0 <= 0
          C 3, name for_mul_0_2, mul_0-x_0 <= 0
          C 4, name for_mul_0_3, mul_0-(bin_y_0_0+x_0-1) >= 0
          C 5, name for_mul_1_1, mul_1-bin_y_0_1 <= 0
          C 6, name for_mul_1_2, mul_1-x_0 <= 0
          C 7, name for_mul_1_3, mul_1-(bin_y_0_1+x_0-1) >= 0
          C 8, name for_mul_2_1, mul_2-bin_y_0_2 <= 0
          C 9, name for_mul_2_2, mul_2-x_0 <= 0
          C 10, name for_mul_2_3, mul_2-(bin_y_0_2+x_0-1) >= 0
    """
    binarizes = dict()
    prob.obj = prob.obj.expand()
    binarize_expression(prob.obj, binarizes)
    for const in prob.constraints:
        const.expression = const.expression.expand()
        binarize_expression(const.expression, binarizes)

    for source, binaries in binarizes.items():
        prob += sum(binaries) == 1, f'for_bin_{source.name}_sum'
        prob += source == source.toBinary(), f'for_bin_{source.name}_eq'


def binarize_expression(e, binarizes):
    """binarize a expression

    Parameters
    ----------
    e : Expresson or VarElement
    binarizes : dict
        binarizes[var] = binaries, where var = sum(i*var_bin)
    """
    if isinstance(e, (VarElement, VarConst, ExpressionConst)):
        return
    finish = False
    while not finish:
        finish = not binarize_traverse(e, binarizes)


def binarize_traverse(e, binarizes):
    """subroutine of binarize_expression

    Parameters
    ----------
    e : Expresson or VarElement
    binarizes : dict
        binarizes[var] = binaries, where var = sum(i*var_bin)

    Returns
    -------
    bool
        return true if a expession is linearized else false
    """
    assert isinstance(e, Expression)
    convert = False
    for node in e.traverse():
        if isinstance(node, Expression):
            expand = False
            if node.elmA.getType() == 'VarInteger':
                if node.elmA not in binarizes:
                    binarizes[node.elmA] = list(node.elmA.toBinary().getVariables())
                node.elmA = node.elmA.toBinary()
                node.elmA.parents.append(node)
                expand = True
            if node.elmB.getType() == 'VarInteger':
                if node.elmB not in binarizes:
                    binarizes[node.elmB] = list(node.elmB.toBinary().getVariables())
                node.elmB = node.elmB.toBinary()
                node.elmB.parents.append(node)
                expand = True
            if expand:
                convert = True
                node.setName()
                for parent in node.traverseAncestors():
                    parent.setName()
                return convert
    return convert
