class SolverError(Exception):
    pass


class RearchLowerbound(Exception):
    """Notification for solver finds solution whose objective value is lower than lowerbound"""

    pass


class ConversionError(Exception):
    """error of conversion problem"""

    pass
