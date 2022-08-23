import functools
import operator

import numpy as np

from flopt.polynomial import Monomial, Polynomial
from flopt.expression import ExpressionElement
from flopt.constants import (
    ExpressionType,
    number_classes,
)


# ------------------------------------------------
#   Utilities
# ------------------------------------------------
to_value_ufunc = np.frompyfunc(lambda x: x.value(), 1, 1)


def to_value_with_var_dict(elm, var_dict):
    if isinstance(elm, ExpressionElement):
        elm.setVarDict(self.var_dict)
        return elm.value()
    elif elm.name in var_dict:
        return var_dict[elm.name].value()
    else:
        return elm.value()


to_value_with_var_dict_ufunc = np.frompyfunc(to_value_with_var_dict, 2, 1)


# ------------------------------------------------
#   Operation Class
# ------------------------------------------------
class Operation(ExpressionElement):
    def __init__(self, var_or_exps, name=None):
        assert len(var_or_exps) > 0
        self.elms = np.array(var_or_exps)
        super().__init__(name=name)

    def linkChildren(self):
        for elm in self.elms:
            if isinstance(elm, ExpressionElement):
                elm.parents.append(self)

    def getVariables(self):
        variables = set()
        for elm in self.elms:
            variables |= elm.getVariables()
        return variables

    def traverse(self):
        """traverse Expression tree as root is self

        Yield
        -----
        Expression or VarElement
        """
        yield self
        for elm in self.elms:
            if isinstance(elm, ExpressionElement):
                yield from elm.traverse()

    def isNeg(self):
        return False


class Sum(Operation):
    """
    Parameters
    ----------
    var_of_exps : list of VarELement or ExpressionElement
    """

    def __init__(self, var_or_exps, name=None):
        self._type = ExpressionType.Sum
        super().__init__(var_or_exps, name=name)

    def setName(self):
        self.name = ""
        const = 0

        elm = self.elms[0]
        if isinstance(elm, number_classes):
            const += elm
        elif isinstance(elm, ExpressionElement) and elm.name.startswith("-"):
            self.name += f"({elm.name})"
        else:
            self.name += f"{elm.name}"

        for elm in self.elms[1:]:
            if isinstance(elm, number_classes):
                const += elm
            elif isinstance(elm, ExpressionElement) and elm.name.startswith("-"):
                self.name += f"+({elm.name})"
            else:
                self.name += f"+{elm.name}"

        if const != 0:
            self.name += f"+{const}"

    def setPolynomial(self):
        if any(not elm.isPolynomial() for elm in self.elms):
            self.polynomial = None
        else:
            self.polynomial = sum(elm.toPolynomial() for elm in self.elms)

    def _value(self):
        """
        Returns
        -------
        float or int
            return value of expression
        """

        if self.var_dict is not None:
            return to_value_with_var_dict_ufunc(self.elms, self.var_dict).sum()
        else:
            return to_value_ufunc(self.elms).sum()

    def __str__(self):
        s = f"Name: {self.name}\n"
        s += f"  Type    : {self._type}\n"
        s += f"  Value   : {self.value()}\n"
        return s

    def __repr__(self):
        s = f"Sum({self.elms})"
        return s


class Prod(Operation):
    """
    Parameters
    ----------
    var_of_exps : list of VarELement or ExpressionElement
    """

    def __init__(self, var_or_exps, name=None):
        self._type = ExpressionType.Prod
        super().__init__(var_or_exps, name=name)

    def setName(self):
        self.name = ""
        const = 0

        elm = self.elms[0]
        if isinstance(elm, number_classes):
            const += elm
        elif isinstance(elm, ExpressionElement) and elm.name.startswith("-"):
            self.name += f"({elm.name})"
        else:
            self.name += f"{elm.name}"

        for elm in self.elms[1:]:
            if isinstance(elm, number_classes):
                const += elm
            elif isinstance(elm, ExpressionElement) and elm.name.startswith("-"):
                self.name += f"*({elm.name})"
            else:
                self.name += f"*{elm.name}"

        if const != 0:
            self.name = f"{const}*" + self.name

    def setPolynomial(self):
        if any(not elm.isPolynomial() for elm in self.elms):
            self.polynomial = None
        else:
            self.polynomial = functools.reduce(
                operator.mul, (elm.toPolynomial() for elm in self.elms)
            )

    def _value(self):
        """
        Returns
        -------
        float or int
            return value of expression
        """
        if self.var_dict is not None:
            return to_value_with_var_dict_ufunc(self.elms, self.var_dict).prod()
        else:
            return to_value_ufunc(self.elms).prod()

    def __str__(self):
        s = f"Name: {self.name}\n"
        s += f"  Type    : {self._type}\n"
        s += f"  Value   : {self.value()}\n"
        return s

    def __repr__(self):
        s = f"Prod({self.elms})"
        return s
