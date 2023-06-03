import flopt


class G1:
    @staticmethod
    def create_objective():
        obj = lambda x: 5 * sum(x[i] - x[i] ** 2 for i in range(4)) - sum(
            x[i] for i in range(5, 13)
        )

        return obj

    @staticmethod
    def create_constraints():
        constraints = [
            lambda x: 2 * x[0] + 2 * x[1] + x[9] + x[10] - 10 <= 0,
            lambda x: 2 * x[0] + 2 * x[2] + x[9] + x[11] - 10 <= 0,
            lambda x: 2 * x[1] + 2 * x[2] + x[10] + x[11] - 10 <= 0,
            lambda x: -8 * x[0] + x[9] <= 0,
            lambda x: -8 * x[1] + x[10] <= 0,
            lambda x: -8 * x[2] + x[11] <= 0,
            lambda x: -2 * x[3] - x[4] + x[9] <= 0,
            lambda x: -2 * x[5] - x[6] + x[10] <= 0,
            lambda x: -2 * x[7] - x[8] + x[11] <= 0,
        ]
        return constraints

    @staticmethod
    def create_variables(cat="Continuous"):
        variables = flopt.Variable.array("x", 13, lowBound=0, upBound=1, cat=cat)
        return variables

    @staticmethod
    def minimum_obj():
        return -15
