import random
from math import sqrt, floor, ceil
from copy import deepcopy

from flopt.env import setup_logger


logger = setup_logger(__name__)


class Solution:
    """
    Solution Class

    Parameters
    ----------
    name : str
      name of solution
    variables : list of VarElement family
      variables which has no duplicate

    Examples
    ----------
    Create a Solution which has Integer, Continuous and Binary Variables

    >>> a = Variable(name='a', lowBound=0, upBound=1, cat='Integer')
    >>> b = Variable(name='b', lowBound=1, upBound=2, cat='Continuous')
    >>> c = Variable(name='c', cat='Binary')
    >>> sol = Solution(name='abc', [a, b, c])

    Four arithmetic operations are supported
    between Solutions or between a Solution and a constant.

    >>> sol1 = Solution(name='sol1', [a, b])
    >>> sol2 = Solution(name='sol2', [a, c])
    >>> sol_plus = sol1 + sol2  # (Solution + Solution or Solution + list)
    >>> sol_minus = sol1 - sol2  # (Solution - Solution or Solution - list)
    >>> sol_product = sol1 * 2  # (Solution * constant)
    >>> sol_divide = sol1 / 2  # (Solution / constant)
    """
    def __init__(self, name=None, variables=[]):
        self.name = name
        self.type = 'Solution'
        self._variables = sorted(variables, key=lambda var: var.name)

    def value(self):
        """
        Returns
        -------
        list
          values of the variables in the Solution
        """
        values = [variable.value() for variable in self._variables]
        return values

    def getVariables(self):
        """
        Returns
        -------
        list
          Variable instances which belong to the Solution
        """
        return self._variables

    def clone(self):
        """
        Returns
        -------
        Solution
          Copy of the Solution (call by value)
        """
        return +self

    def copy(self, other):
        """
        Copy the values of a Solution to itself (call by value)
        """
        for vb, ovb in zip(self._variables, other._variables):
            vb.setValue(ovb.value())

    def setRandom(self):
        """
        Set the solution values uniformly random
        """
        for vb in self._variables:
            vb.setRandom()

    def feasible(self):
        """
        Returns
        -------
        bool
          Whether the solution is feasible or not
        """
        return all(vb.feasible() for vb in self._variables)

    def clip(self):
        """
        Guarantee feasibility of the solution
        """
        for vb in self._variables:
            vb.clip()

    def squaredNorm(self):
        """
        Returns
        -------
        float
          Squared 2-norm of the solution as a vector in Euclid space
        """
        return sum(vb.value()*vb.value() for vb in self._variables)

    def norm(self):
        """
        Returns
        -------
        float
          2-norm of the solution as a vector in Euclid space
        """
        return sqrt(self.squaredNorm())

    def dot(self, other):
        """
        Returns
        -------
        float
          Inner product between the Solution and another Solution
        """
        inner = 0
        for vb1, vb2 in zip(self._variables, other._variables):
            inner += vb1.value()*vb2.value()
        return inner

    def floor(self):
        """
        Returns
        -------
        Solution
          Solution which has values applied floor function respectively
        """
        vbs = deepcopy(self._variables)
        for vb in vbs:
            vb.setValue(floor(vb.value()))
        return Solution(f'floor({self.name})', vbs)

    def ceil(self):
        """
        Returns
        -------
        Solution
          Solution which has values applied ceiling function respectively
        """
        vbs = deepcopy(self._variables)
        for vb in vbs:
            vb.setValue(ceil(vb.value()))
        return Solution(f'ceil({self.name})', vbs)

    def __pos__(self):
        vbs = deepcopy(self._variables)
        return Solution(f'+({self.name})', vbs)

    def __neg__(self):
        vbs = deepcopy(self._variables)
        for vb in vbs:
            vb.setValue(-vb.value())
        return Solution(f'-({self.name})', vbs)

    def __add__(self, other):
        """
        Solution + Solution
        Solution + list
        Solutino + scalar
        """
        vbs1 = deepcopy(self._variables)
        if isinstance(other, Solution):
            for vb1, vb2 in zip(vbs1, other._variables):
                vb1.setValue(vb1.value() + vb2.value())
            return Solution('+Solution', vbs1)
        elif isinstance(other, list):
            for vb, v in zip(vbs1, other):
                vb.setValue(vb.value() + v)
            return Solution('+list', vbs1)
        elif isinstance(other, (int, float)):
            for vb1 in vbs1:
                vb1.setValue(vb1.value() + other)
            return Solution('+scalar', vbs1)
        else:
            return NotImplemented

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        """
        Solution - Solution = (Solution + (-Solution))
        Solution - list     = (Solution + (-list))
        Solutino - scalar   = (Solution + (-scalar))
        """
        if isinstance(other, Solution):
            return self + (-other)
        elif isinstance(other, list):
            minus_other = [-v for v in other]
            return self + minus_other
        elif isinstance(other, (int, float)):
            return self + (-other)
        else:
            return NotImplemented

    def __rsub__(self, other):
        return - self + other

    def __mul__(self, other):
        """
        Solution * Solution (hadamard product)
        Solution * list
        Solution * scalar
        """
        vbs1 = deepcopy(self._variables)
        if isinstance(other, Solution):
            for vb1, vb2 in zip(vbs1, other._variables):
                vb1.setValue(vb1.value() * vb2.value())
            return Solution('*Solution', vbs1)
        elif isinstance(other, list):
            for vb, v in zip(vbs1, other):
                vb.setValue(vb.value() * v)
            return Solution('*list', vbs1)
        elif isinstance(other, (int, float)):
            for vb1 in vbs1:
                vb1.setValue(vb1.value() * other)
            return Solution('*scalar', vbs1)
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        """
        Solution / list     = Solution * (1/list)
        Solution / scalar   = Solution * (1/scalar)
        """
        if isinstance(other, list):
            reverse_list = [1/v for v in other]
            return self * reverse_list
        elif isinstance(other, (int, float)):
            return self * (1 / other)
        else:
            return NotImplemented

    def __abs__(self):
        vbs = deepcopy(self._variables)
        for vb in vbs:
            vb.setValue(abs(vb.value()))
        return Solution('abs', vbs)

    def __hash__(self):
        return hash((self.name, tuple(self._variables)))

    def __len__(self):
        return len(self._variables)

    def __iter__(self):
        return iter(self._variables)

    def __getitem__(self, k):
        return self._variables[k]

    def __str__(self):
        s  = f'Name: {self.name}\n'
        s += f'  Type    : {self.type}\n'
        for vb in self:
            s += f'  {vb.__str__()}\n'
        return s

    def __repr__(self):
        return f'Solution({self.name}, [{", ".join([vb.name for vb in self._variables])}])'
