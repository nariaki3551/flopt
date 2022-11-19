import operator
import functools

from flopt.constants import VariableType


class Monomial:
    """
    Parameters
    ----------
    terms : dict(Variable=exponentiation)
        this monomial is represented as
        coeff * prod( var_i ^ {exp_i} for var_i, exp_i in terms.items() ),
        where exp_i is positive integer.
    coeff : int or float
        coefficient of monomial

    Notes
    -----
    If terms is empty dictionary, then this monomial is constant whose value is self.coeff
    """

    def __init__(self, terms={}, coeff=1):
        self.terms = terms
        self.coeff = coeff
        self.max_degree = None
        self.is_linear = None
        self._hash = None

    def clone(self):
        """
        Returns
        -------
        Monomial
        """
        return Monomial(dict(self.terms), self.coeff)

    def value(self):
        return self.coeff * functools.reduce(
            operator.mul,
            (var.value() ** exponent for var, exponent in self.terms.items()),
        )

    def maxDegree(self):
        """
        Returns
        -------
        int
            maximum degree of variables
        """
        if self.max_degree is None:
            self.max_degree = max([0] + [exp for val, exp in self.terms.items()])
        return self.max_degree

    def diff(self, x):
        """
        Parameters
        ----------
        x : VarElement family

        Returns
        -------
        Monomial
            the monomial differentiated by x
        """
        if not x in self.terms:
            return Monomial(coeff=0)
        else:
            terms = dict(self.terms)
            coeff = self.coeff * terms[x]
            terms[x] -= 1
            if terms[x] == 0:
                del terms[x]
            return Monomial(terms, coeff)

    def isConstant(self):
        """
        Returns
        -------
        bool
            return True if it is constant else False
        """
        return len(self.terms) == 0

    def isLinear(self):
        """
        Returns
        -------
        bool
            Return True if it is linear else False
        """
        if self.is_linear is None:
            self.is_linear = self.maxDegree() <= 1 and len(self.terms) <= 1
        return self.is_linear

    def isQuadratic(self):
        """
        Returns
        -------
        bool
            Return True if it is quadratic else False
        """
        return sum(self.terms.values()) <= 2

    def toPolynomial(self):
        """
        Returns
        -------
        Polynomial
        """
        if self.terms:
            return Polynomial({Monomial(self.terms): self.coeff})
        return Polynomial(constant=self.coeff)

    def toExpression(self):
        """
        Returns
        -------
        Expression
        """
        expression = self.coeff
        for var, exponent in self.terms.items():
            expression *= var**exponent
        return expression

    def simplify(self):
        """Simplify this monomial

        Returns
        -------
        Monomial
        """
        terms = {}
        for x in self.terms:
            if x.type() == VariableType.Binary:
                terms[x] = 1  # x * x = x
            elif x.type() == VariableType.Spin:
                if self.terms[x] % 2 == 1:
                    terms[x] = 1  # x * x = 1 --> x^{2n+1} = x
                else:
                    pass  # x * x = 1 --> x^{2n} = 1 (become constant 1)
            else:
                terms[x] = self.terms[x]
        return Monomial(terms, self.coeff)

    def __mul__(self, other):
        mono = self.clone()
        mono *= other
        return mono

    def __rmul__(self, other):
        return self * other

    def __imul__(self, other):
        if isinstance(other, (int, float)):
            self.coeff *= other
        elif isinstance(other, Monomial):
            for x in other.terms:
                if x in self.terms:
                    self.terms[x] += other[x]
                else:
                    self.terms[x] = other[x]
            self.coeff *= other.coeff
            self.max_degree = None
            self.is_linear = None
        else:
            return NotImplemented
        self._hash = None
        return self

    def __pow__(self, other):
        assert isinstance(other, int)
        terms = {x: exp * other for x, exp in self.terms.items()}
        return Monomial(terms, self.coeff**other)

    def __iter__(self):
        return iter(self.terms.items())

    def __getitem__(self, item):
        return self.terms[item]

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(
                tuple(
                    sorted([(x.name, exp) for x, exp in self.terms.items()])
                    + [self.coeff]
                )
            )
        return self._hash

    def __eq__(self, other):
        if isinstance(other, Monomial):
            return hash(self) == hash(other)

    def __str__(self):
        s = ""
        for x, exp in self.terms.items():
            if exp == 1:
                s += "*" + f"{x.name}"
            else:
                s += "*" + f"{x.name}^{exp}"
        if self.coeff == 1:
            if s:
                return s[1:]
            else:
                return "1"
        else:
            return f"{self.coeff}" + s

    def __repr__(self):
        return str(self)


class Polynomial:
    """
    Parameters
    ----------
    terms : dict(Monomial=coeff)
        sum( coeff_i * mono_i for mono_i, coeff_i in terms.items() ) + constant
    constant : int of float
        constant of polynomial
    """

    def __init__(self, terms={}, constant=0):
        self.terms = terms
        self._constant = constant

    def value(self):
        return (
            sum(coeff * mono.value() for mono, coeff in terms.items()) + self.constant()
        )

    def coeff(self, *args):
        """
        Returns
        -------
        int or float
            coefficient of monomial

        Examples
        --------

        .. code-block:: python

            from flopt import Variable
            x = Variable('x')
            y = Variable('y')
            e = x ** 2 + 3 * y ** 3
            e.polynomial
            >>> x^2+3*y^3+0

        get coefficient of `x^2` term

        .. code-block:: python

            e.polynomial.coeff(x, x)
            >>> 1

        get coefficient of `x` term, it is 0

        .. code-block:: python

            e.polynomial.coeff(x)
            >>> 0

        get coefficient of `y^3` term, it is 0

        .. code-block:: python

            e.polynomial.coeff(y**3)
            >>> 3
        """
        mono = args[0].toMonomial()
        if len(args) > 1:
            mono = mono.clone()
            for elm in args[1:]:
                mono *= elm.toMonomial()
        if mono in self.terms:
            return self.terms[mono]
        return 0

    def constant(self):
        """
        Returns
        -------
        int or float
        """
        return self._constant

    def isConstant(self):
        """
        Returns
        -------
        bool
            return True if it is constant else False
        """
        return len(self.terms) == 0

    def isMonomial(self):
        """
        Returns
        -------
        bool
            return True if it is monomial else False
        """
        return len(self.terms) == 0 or (len(self.terms) == 1 and self._constant == 0)

    def toMonomial(self):
        """
        Returns
        -------
        Monomial
        """
        assert self.isMonomial()
        if len(self.terms) == 0:
            return Monomial(coeff=self._constant)
        else:
            mono = list(self.terms.keys())[0]
            return Monomial(mono.terms, self.terms[mono])

    def diff(self, x):
        """
        Returns
        -------
        Polynomial
            return polynomial differentiated by x
        """
        poly = Polynomial(constant=0)
        for mono, coeff in self:
            poly += coeff * mono.diff(x)
        return poly

    def maxDegree(self):
        """
        Returns
        -------
        int
        """
        return max(mono.maxDegree() for mono in self.terms)

    def isLinear(self):
        """
        Returns
        -------
        bool
            return True if it is linear else False
        """
        return all(mono.isLinear() for mono in self.terms)

    def isQuadratic(self):
        """
        Returns
        -------
        bool
            return True if it is quadratic else False
        """
        return all(mono.isQuadratic() for mono in self.terms)

    def simplify(self):
        """
        Returns
        -------
        Polynomial
            return simplified self polynomial
        """
        terms = {}
        constant = 0
        for mono in self.terms.keys():
            _mono = mono.simplify()
            if _mono.isConstant():
                constant += _mono.coeff
            else:
                terms[_mono] = self.terms[mono]
        return Polynomial(terms, constant + self._constant)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Polynomial(self.terms, self._constant + other)
        elif isinstance(other, Monomial):
            return self + other.toPolynomial()
        elif isinstance(other, Polynomial):
            terms = dict(self.terms)
            for mono, coeff in other:
                if mono in terms:
                    terms[mono] += coeff
                else:
                    terms[mono] = coeff
                # clean up
                if terms[mono] == 0:
                    del terms[mono]
            constant = self._constant + other._constant
            return Polynomial(terms, constant)
        return NotImplemented

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            terms = {mono: coeff * other for mono, coeff in self}
            return Polynomial(terms, self._constant * other)
        elif isinstance(other, Monomial):
            return self * other.toPolynomial()
        elif isinstance(other, Polynomial):
            terms = {}
            for mono, coeff in other:
                for mono_, coeff_ in self:
                    mono__ = mono * mono_
                    if mono__ in terms:
                        terms[mono__] += coeff * coeff_
                    else:
                        terms[mono__] = coeff * coeff_
                    # clean up
                    if terms[mono__] == 0:
                        del terms[mono__]
            for mono, coeff in self:
                if mono in terms:
                    terms[mono] += other._constant * coeff
                else:
                    terms[mono] = other._constant * coeff
                # clean up
                if terms[mono] == 0:
                    del terms[mono]
            for mono, coeff in other:
                if mono in terms:
                    terms[mono] += self._constant * coeff
                else:
                    terms[mono] = self._constant * coeff
                # clean up
                if terms[mono] == 0:
                    del terms[mono]
            constant = self._constant * other._constant
            return Polynomial(terms, constant)
        return NotImplemented

    def __rmul__(self, other):
        return self * other

    def __pow__(self, other):
        assert isinstance(other, int)
        poly = Polynomial(constant=1)
        for _ in range(other):
            poly *= self
        return poly

    def __neg__(self):
        terms = {mono: -coeff for mono, coeff in self.terms.items()}
        return Polynomial(terms, -self._constant)

    def __iter__(self):
        return iter(self.terms.items())

    def __getitem__(self, item):
        return self.coeff(item)

    def __hash__(self):
        return hash(
            tuple(sorted([(hash(x), coeff) for x, coeff in self.terms.items()]))
        )

    def __eq__(self, other):
        if isinstance(other, Polynomial):
            return hash(self) == hash(other)

    def __str__(self):
        s = ""
        for mono, coeff in self.terms.items():
            if coeff == 1:
                s += f"{mono}+"
            elif coeff > 0:
                s += f"{coeff}*{mono}+"
            else:
                s += f"({coeff}*{mono})+"
        return s + f"{self._constant}"

    def __repr__(self):
        return str(self)
