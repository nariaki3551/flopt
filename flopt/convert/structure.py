import numpy as np

from flopt import Variable, Problem
from flopt.variable import VariableArray
from flopt.convert.linearize import linearize
from flopt.constants import VariableType, ConstraintType, array_classes, np_float
from flopt.error import ConversionError
from flopt.env import setup_logger, create_variable_mode

logger = setup_logger(__name__)


# -------------------------------------------------------
#   Utils
# -------------------------------------------------------


def to_nparray_or_None(x):
    if x is not None:
        if isinstance(x, array_classes) and not isinstance(x, np.ndarray):
            x = np.array(x, dtype=np_float)
    return x


def merge(func, arrays):
    """
    Parameters
    ----------
    func: numpy function
    arrays: list of (array, coeff)

    Returns
    -------
    np.ndarray
    """
    if all(array is None for array, coeff in arrays):
        return None
    else:
        non_nones = [coeff * array for array, coeff in arrays if array is not None]
        return func(non_nones)


def zero_percentage(array):
    if array is None:
        return None
    else:
        return f"{(1 - np.count_nonzero(array)/array.size)*100:.3f}"


def shape(array):
    if array is None:
        return None
    else:
        return array.shape


# -------------------------------------------------------
#   Expression Structures
# -------------------------------------------------------


class QuadraticStructure:
    """Quadratic Structure
    ::

      1/2 x.T.dot(Q).dot(x) + c.T.dot(x) + C
    """

    def __init__(self, Q, c, C, x=None):
        self.Q = to_nparray_or_None(Q)
        self.c = to_nparray_or_None(c)
        self.C = C
        self.x = to_nparray_or_None(x)

    def toLinear(self):
        """
        Returns
        -------
        LinearStructure

        Raises
        ------
        ConversionError
            If this problem cannot be converted to LinearStructure
        """
        if self.Q is not None and not np.all(self.Q == 0):
            raise ConversionError()
        return LinearStructure(self.c, self.C, self.x)

    def __repr__(self):
        return f"QuadraticStructure{self.Q, self.c, self.C, self.x}"


class LinearStructure:
    """Linear Structure
    ::

      c.T.dot(x) + C
    """

    def __init__(self, c, C, x=None):
        self.c = to_nparray_or_None(c)
        self.C = C
        self.x = to_nparray_or_None(x)

    def __repr__(self):
        return f"LinearStructure{self.c, self.C, self.x}"


# -------------------------------------------------------
#   Problem Structures
# -------------------------------------------------------


class QpStructure:
    """Quadratic Programming Structure

    ::

      obj  1/2 x.T.dot(Q).dot(x) + c.T.dot(x) + C
      s.t. Gx <= h
           Ax == b
           lb <= x <= ub
    """

    def __init__(
        self,
        Q,
        c,
        C,
        G=None,
        h=None,
        A=None,
        b=None,
        lb=None,
        ub=None,
        types="Continuous",
        x=None,
    ):
        self.Q = to_nparray_or_None(Q)
        self.c = to_nparray_or_None(c)
        self.C = C
        self.G = to_nparray_or_None(G)
        self.h = to_nparray_or_None(h)
        self.A = to_nparray_or_None(A)
        self.b = to_nparray_or_None(b)
        self.lb = to_nparray_or_None(lb)
        self.ub = to_nparray_or_None(ub)
        self.types = types
        self.x = to_nparray_or_None(x)

    def numVariables(self):
        if self.x is not None:
            return len(self.x)
        elif self.G is not None:
            return self.G.shape[1]
        elif self.A is not None:
            return self.A.shape[1]

    @classmethod
    def fromFlopt(cls, prob, x=None, option=None, progress=False):
        """
        Parameters
        ----------
        prob : Problem
        x : None or list of VarElement family
        progress: bool
        option : {"all_neq", "all_eq"}

        Returns
        -------
        QpStructure
        """
        assert prob.obj.isQuadratic()
        assert all(const.isLinear() for const in prob.getConstraints())

        if x is None:
            x = VariableArray(list(prob.getVariables()), dtype=object)

        quadratic = prob.obj.toQuadratic(x)
        Q, c, C = quadratic.Q, quadratic.c, quadratic.C
        if Q is not None:
            num_x = Q.shape[0]
        elif c is not None:
            num_x = len(c)
        else:
            num_x = 0

        if progress:
            import tqdm

            def iter_wrapper(x, desc, *args, **kwargs):
                return tqdm.tqdm(x, desc=desc)

        else:

            def iter_wrapper(x, *args, **kwargs):
                return x

        # create G, h
        num_neq_consts = sum(
            const.type() == ConstraintType.Le for const in prob.getConstraints()
        )
        if num_neq_consts == 0:
            G = None
            h = None
        else:
            G = np.zeros((num_neq_consts, num_x), dtype=np_float)
            h = np.zeros((num_neq_consts,), dtype=np_float)
            i = 0
            for const in iter_wrapper(
                prob.getConstraints(), desc="convert neq constraints"
            ):
                if const.type() == ConstraintType.Le:
                    # c.T.dot(x) + C <= 0
                    linear = const.expression.toLinear(x)
                    G[i, :] = linear.c.T
                    h[i] = -linear.C
                    i += 1
            assert i == num_neq_consts

        # create A, b
        num_eq_consts = sum(
            const.type() == ConstraintType.Eq for const in prob.getConstraints()
        )
        if num_eq_consts == 0:
            A = None
            b = None
        else:
            A = np.zeros((num_eq_consts, num_x), dtype=np_float)
            b = np.zeros((num_eq_consts,), dtype=np_float)
            i = 0
            for const in iter_wrapper(
                prob.getConstraints(), desc="convert eq constraints"
            ):
                if const.type() == ConstraintType.Eq:
                    linear = const.expression.toLinear(x)
                    A[i, :] = linear.c.T
                    b[i] = -linear.C
                    i += 1
            assert i == num_eq_consts

        # create lb, ub
        lb = np.array([var.lowBound for var in x], dtype=np_float)
        ub = np.array([var.upBound for var in x], dtype=np_float)

        # create types
        type2str = {
            VariableType.Continuous: "Continuous",
            VariableType.Integer: "Integer",
            VariableType.Binary: "Binary",
            VariableType.Spin: "Spin",
        }
        types = [type2str[var.type()] for var in x]

        qp = cls(Q, c, C, G, h, A, b, lb, ub, types, x)

        if option == "all_neq":
            return qp.toAllNeq()
        elif option == "all_eq":
            return qp.toAllEq()
        else:
            return qp

    def toAllNeq(self):
        """convert all non eqaual constraint type

        ::

          obj  1/2 x.T.dot(Q).dot(x) + c.T.dot(x) + C
          s.t. [G; A; -A] x <= [h; b; -b]
               lb <= x <= ub

        Returns
        -------
        QpStructure
        """
        G = merge(np.vstack, [(self.G, 1), (self.A, 1), (self.A, -1)])
        h = merge(np.hstack, [(self.h, 1), (self.b, 1), (self.b, -1)])
        A = None
        b = None
        return QpStructure(
            self.Q, self.c, self.C, G, h, A, b, self.lb, self.ub, self.types, self.x
        )

    def toAllEq(self):
        """convert all eqaual constraint type

        ::

          obj  1/2 x.T.dot([Q, O; O, O]).dot([x; s]) + [c; O].T.dot([x; s]) + C
          s.t. [A, O; G, I] [x; s] == [b; h]
               lb <= x <= ub
               0 <= s

        """
        assert self.x is not None or self.types is not None
        if self.G is None:
            return self
        num_stack = len(self.G)
        num_var = self.numVariables()
        Q = np.zeros((num_var + num_stack, num_var + num_stack), dtype=np_float)
        Q[: self.Q.shape[0], : self.Q.shape[1]] = self.Q
        c = np.hstack([self.c, np.zeros((num_stack,), dtype=np_float)])
        A = np.zeros((self.A.shape[0] + num_stack, num_var + num_stack), dtype=np_float)
        A[: self.A.shape[0], : self.A.shape[1]] = self.A
        A[self.A.shape[0] :, : self.G.shape[1]] = self.G
        A[self.A.shape[0] :, self.G.shape[1] :] = np.identity(num_stack, dtype=np_float)
        b = np.hstack([self.b, self.h])
        if self.lb is not None:
            lb = np.hstack([self.lb, np.zeros((num_stack,), dtype=np_float)])
        else:
            lb = None
        if self.ub is not None:
            ub = np.hstack([self.ub, np.full((num_stack,), None, dtype=np_float)])
        else:
            ub = None
        if self.types is not None:
            types = self.types + ["Continuous"] * num_stack
        else:
            types = self.types
        if self.x is not None:
            with create_variable_mode():
                s = Variable.array("slack", num_stack, lowBound=0, cat="Continuous")
            x = np.hstack([self.x, s])
        else:
            x = self.x
        return QpStructure(Q, c, self.C, None, None, A, b, lb, ub, types, x)

    def boundsToNeq(self):
        """convert bounds constraints into neq constraints

        ::

          obj  1/2 x.T.dot(Q).dot(x) + c.T.dot(x) + C
          s.t. [G; -I; I] x <= [h; -lb; ub]
               A x == b

        Returns
        -------
        QpStructure
        """
        G = np.array(self.G) if self.G is not None else None
        h = np.array(self.h) if self.h is not None else None
        if self.lb is not None:
            I = np.identity(self.numVariables(), dtype=np_float)
            G = merge(np.vstack, [(G, 1), (I, -1)])
            h = merge(np.hstack, [(h, 1), (self.lb, -1)])
        if self.ub is not None:
            I = np.identity(self.numVariables(), dtype=np_float)
            G = merge(np.vstack, [(G, 1), (I, 1)])
            h = merge(np.hstack, [(h, 1), (self.ub, 1)])
        lb, ub = None, None
        return QpStructure(
            self.Q, self.c, self.C, G, h, self.A, self.b, lb, ub, self.types, self.x
        )

    def toFlopt(self, name=None):
        """
        Parameters
        ----------
        name : str
            name of problem

        Returns
        -------
        Problem
        """
        if self.x is not None:
            x = self.x
        else:
            x = Variable.array("x", len(self.Q), self.lb, self.ub, self.types)
        prob = Problem(name)
        prob += (0.5 * (x.T.dot(self.Q).dot(x)) + self.c.T.dot(x) + self.C).expand()
        if self.G is not None:
            for g, h_ in zip(self.G, self.h):
                prob += g.dot(x) <= h_
        if self.A is not None:
            for a, b_ in zip(self.A, self.b):
                prob += a.dot(x) == b_
        return prob

    def isLp(self):
        return self.Q is None or np.all(self.Q == 0)

    def toLp(self):
        """
        Returns
        -------
        LpStructure

        Raises
        ------
        ConversionError
            If this cannot be conversion to LpStructure
        """
        if self.Q is not None and not np.all(self.Q == 0):
            logger.info(f"linearization will be done because it is not linearize")
            prob = self.toFlopt()
            linearize(prob)
            if prob.obj.isLinear() and all(
                const.isLinear() for const in prob.getConstraints()
            ):
                return LpStructure.fromFlopt(prob)
            else:
                raise ConversionError()
        return LpStructure(
            self.c,
            self.C,
            self.G,
            self.h,
            self.A,
            self.b,
            self.lb,
            self.ub,
            self.types,
            self.x,
        )

    def toIsing(self):
        """
        ::

            QpStructure --> Problem (flopt) --> IsingStructure

        Returns
        -------
        IsingStructure
        """
        assert self.G is None and self.A is None
        return self.toFlopt().obj.toIsing()

    def toQubo(self):
        """
        ::

            QpStructure --> Problem (flopt) --> IsingStructure --> QuboStructure

        Returns
        -------
        QuboStructure
        """
        assert self.G is None and self.A is None
        return self.toIsing().toQubo()

    def show(self):
        s = f"QpStructure\n"
        s += f"obj  1/2 x.T.dot(Q).dot(x) + c.T.dot(x) + C\n"
        s += f"s.t. Gx <= h\n"
        s += f"     Ax == b\n"
        s += f"     lb <= x <= ub\n\n"
        s += f"#x\n{self.numVariables()}\n\n"
        s += f"Q\n{self.Q}\n\n"
        s += f"c\n{self.c}\n\n"
        s += f"C\n{self.C}\n\n"
        s += f"G\n{self.G}\n\n"
        s += f"h\n{self.h}\n\n"
        s += f"A\n{self.A}\n\n"
        s += f"b\n{self.b}\n\n"
        s += f"lb\n{self.lb}\n\n"
        s += f"ub\n{self.ub}\n\n"
        s += f"x\n{self.x}"
        return s

    def __repr__(self):
        return f"QpStructure{self.Q, self.c, self.C, self.G, self.h, self.A, self.b, self.lb, self.ub, self.types, self.x}"

    def __str__(self):
        s = f"QpStructure\n"
        s += f"  #x  {self.numVariables()}\n"
        s += f"  #Q  {shape(self.Q)}  (0-element {zero_percentage(self.Q)} %)\n"
        s += f"  #c  {shape(self.c)}\n"
        s += f"  #C  {self.C}\n"
        s += f"  #G  {shape(self.G)}  (0-element {zero_percentage(self.G)} %)\n"
        s += f"  #h  {shape(self.h)}\n"
        s += f"  #A  {shape(self.A)}  (0-element {zero_percentage(self.A)} %)\n"
        s += f"  #b  {shape(self.b)}\n"
        s += f"  #lb {len(self.lb) if self.lb is not None else None}\n"
        s += f"  #ub {len(self.ub) if self.ub is not None else None}"
        return s


class LpStructure:
    """Linear Programming Structure

    ::

      obj  c.T.dot(x) + C
      s.t. Gx <= h
           Ax == b
           lb <= x <= ub
    """

    def __init__(
        self,
        c,
        C,
        G=None,
        h=None,
        A=None,
        b=None,
        lb=None,
        ub=None,
        types="Continuous",
        x=None,
    ):
        self.c = to_nparray_or_None(c)
        self.C = C
        self.G = to_nparray_or_None(G)
        self.h = to_nparray_or_None(h)
        self.A = to_nparray_or_None(A)
        self.b = to_nparray_or_None(b)
        self.lb = to_nparray_or_None(lb)
        self.ub = to_nparray_or_None(ub)
        self.types = types
        self.x = to_nparray_or_None(x)

    def numVariables(self):
        if self.x is not None:
            return len(self.x)
        elif self.G is not None:
            return self.G.shape[1]
        elif self.A is not None:
            return self.A.shape[1]

    def toAllNeq(self):
        """
        Returns
        -------
        LpStructure
        """
        return self.toQp().toAllNeq().toLp()

    def toAllEq(self):
        """
        Returns
        -------
        LpStructure
        """
        return self.toQp().toAllEq().toLp()

    @classmethod
    def fromFlopt(cls, prob, x=None, option=None, progress=False):
        """
        ::

            Problem (flopt) --> QpStructure --> LpStructure

        Parameters
        ----------
        prob : Problem
        x : None or list of Variable family
        option : {"all_neq", "all_eq"}
        progress : bool

        Returns
        -------
        LpStructure
        """
        assert option is None or option in {
            "all_neq",
            "all_eq",
        }, f"option must be None, all_neq or all_eq, but got {option}"
        qp = QpStructure.fromFlopt(prob, x, progress=progress)
        if option == "all_neq":
            return qp.toAllNeq().toLp()
        elif option == "all_eq":
            return qp.toAllEq().toLp()
        else:
            return qp.toLp()

    def toFlopt(self):
        """
        ::

            LpStructure --> QpStructure --> Problem (flopt)

        Returns
        -------
        Problem
        """
        return self.toQp().toFlopt()

    def toQp(self):
        """
        Returns
        -------
        QpStructure
        """
        Q = np.zeros((len(self.c), len(self.c)), dtype=np_float)
        return QpStructure(
            Q,
            self.c,
            self.C,
            self.G,
            self.h,
            self.A,
            self.b,
            self.lb,
            self.ub,
            self.types,
            self.x,
        )

    def toIsing(self):
        """
        ::

            LpStructure --> Problem (flopt) --> IsingStructure

        Returns
        -------
        IsingStructure
        """
        assert self.G is None and self.A is None
        return self.toFlopt().obj.toIsing()

    def toQubo(self):
        """
        ::

            LpStructure --> Problem (flopt) --> IsingStructure --> QuboStructure

        Returns
        -------
        QuboStructure
        """
        assert self.G is None and self.A is None
        return self.toIsing().toQubo()

    def show(self):
        s = f"LpStructure\n"
        s += f"obj  c.T.dot(x) + C\n"
        s += f"s.t. Gx <= h\n"
        s += f"     Ax == b\n"
        s += f"     lb <= x <= ub\n\n"
        s += f"#x\n{self.numVariables()}\n\n"
        s += f"c\n{self.c}\n\n"
        s += f"C\n{self.C}\n\n"
        s += f"G\n{self.G}\n\n"
        s += f"h\n{self.h}\n\n"
        s += f"A\n{self.A}\n\n"
        s += f"b\n{self.b}\n\n"
        s += f"lb\n{self.lb}\n\n"
        s += f"ub\n{self.ub}\n\n"
        s += f"x\n{self.x}"
        return s

    def __repr__(self):
        return f"LpStructure{self.c, self.C, self.G, self.h, self.A, self.b, self.lb, self.ub, self.types, self.x}"

    def __str__(self):
        s = f"LpStructure\n"
        s += f"  #x  {self.numVariables()}\n"
        s += f"  #c  {shape(self.c)}\n"
        s += f"  #C  {self.C}\n"
        s += f"  #G  {shape(self.G)}  (0-element {zero_percentage(self.G)} %)\n"
        s += f"  #h  {shape(self.h)}\n"
        s += f"  #A  {shape(self.A)}  (0-element {zero_percentage(self.A)} %)\n"
        s += f"  #b  {shape(self.b)}\n"
        s += f"  #lb {len(self.lb) if self.lb is not None else None}\n"
        s += f"  #ub {len(self.ub) if self.ub is not None else None}"
        return s


class IsingStructure:
    """Ising Structure

    ..

      obj  - x.T.dot(J).dot(x) - h.T.dot(x) + C
      s.t. x in {-1, 1}^N
    """

    def __init__(self, J, h, C, x=None):
        self.J = to_nparray_or_None(J)
        self.h = to_nparray_or_None(h)
        self.C = C
        self.x = to_nparray_or_None(x)

    def numVariables(self):
        if self.x is not None:
            return len(self.x)
        elif self.J is not None:
            return self.J.shape[0]

    @classmethod
    def fromFlopt(cls, prob, x=None):
        return prob.obj.toIsing()

    def toFlopt(self):
        if self.x is not None:
            x = self.x
        else:
            x = Variable.array("x", len(self.J), cat="Spin")
        prob = Problem()
        prob += -x.T.dot(self.J).dot(x) - self.h.T.dot(x) + self.C
        return prob

    def toQp(self):
        """
        ::

            IsingStructure --> Problem (flopt) --> QpStructure

        Returns
        -------
        QpStructure
        """
        return QpStructure.fromFlopt(self.toFlopt())

    def toLp(self):
        """
        ::

            IsingStructure --> Problem (flopt) --> QpStructure --> LpStructure

        Returns
        -------
        LpStructure
        """
        return self.toQp().toLp()

    def toQubo(self):
        """
        Returns
        -------
        QuboStructure
        """
        num_x = len(self.J)

        # create Q
        Q = np.zeros((num_x, num_x), dtype=np_float)
        for i in range(num_x):
            for j in range(i + 1, num_x):
                Q[i, j] = -4 * self.J[i, j]
        for i in range(num_x):
            Q[i, i] = 2 * (self.J[:i, i].sum() + self.J[i, i + 1 :].sum() - self.h[i])

        # create C
        C = self.C - np.triu(self.J).sum() + self.h.sum()

        # create x
        if self.x is None:
            x = None
        else:
            for var in self.x:
                var.toBinary()
            x = np.array([var.binary for var in self.x], dtype=object)
        return QuboStructure(Q, C, x)

    def show(self):
        s = f"IsingStructure\n"
        s += f"- x.T.dot(J).dot(x) - h.T.dot(x) + C\n\n"
        s += f"#x\n{self.numVariables()}\n\n"
        s += f"J\n{self.J}\n\n"
        s += f"h\n{self.h}\n\n"
        s += f"C\n{self.C}\n\n"
        s += f"x\n{self.x}"
        return s

    def __repr__(self):
        return f"IsingStructure{self.J, self.h, self.C, self.x}"

    def __str__(self):
        s = f"IsingStructure\n"
        s += f"  #x  {self.numVariables()}\n"
        s += f"  #J  {shape(self.J)}  (0-element {zero_percentage(self.J)} %)\n"
        s += f"  #h  {shape(self.h)}\n"
        s += f"  #C  {self.C}\n"
        return s


class QuboStructure:
    """QUBO Structure
    ::

      obj  x.T.dot(Q).dot(x) + C
    """

    def __init__(self, Q, C, x=None):
        self.Q = to_nparray_or_None(Q)
        self.C = C
        self.x = to_nparray_or_None(x)

    def numVariables(self):
        if self.x is not None:
            return len(self.x)
        elif self.Q is not None:
            return self.Q.shape[0]

    @classmethod
    def fromFlopt(cls, prob, x=None):
        """
        ::

            Problem (flopt) --> IsingStructure --> QuboStructure
        """
        return IsingStructure.fromFlopt(prob, x).toQubo()

    def toFlopt(self):
        """
        Returns
        -------
        Problem
        """
        if self.x is not None:
            x = self.x
        else:
            x = Variable.array("x", len(self.Q), cat="Binary")
        prob = Problem()
        prob += (x.T.dot(self.Q).dot(x) + self.C).expand()
        return prob

    def toQp(self):
        """
        ::

            QuboStructure --> Problem (flopt) --> QpStructure

        Returns
        -------
        QpStructure
        """
        return QpStructure.fromFlopt(self.toFlopt())

    def toLp(self):
        """
        ::

            QuboStructure --> Problem (flopt) --> QuboStructure --> LpStructure

        Returns
        -------
        LpStructure
        """
        return self.toQp().toLp()

    def toIsing(self):
        """
        ::

            QuboStructure --> Problem (flopt) --> IsingStructure

        Returns
        -------
        IsingStructure
        """
        return self.toFlopt().obj.toIsing()

    def show(self):
        s = f"QuboStructure\n"
        s += f"x.T.dot(Q).dot(x) + C\n\n"
        s += f"#x\n{self.numVariables()}\n\n"
        s += f"Q\n{self.Q}\n\n"
        s += f"C\n{self.C}\n\n"
        s += f"x\n{self.x}"
        return s

    def __repr__(self):
        return f"QuboStructure{self.Q, self.C, self.x}"

    def __str__(self):
        s = f"QuboStructure\n"
        s += f"  #x  {self.numVariables()}\n"
        s += f"  #Q  {shape(self.Q)}  (0-element {zero_percentage(self.Q)} %)\n"
        s += f"  #C  {self.C}\n"
        return s
