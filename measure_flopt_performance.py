import re
import time
import itertools
import subprocess

import tqdm
import pulp
import pandas
import numpy as np

import flopt
import flopt.convert
import flopt.performance

np.random.seed(0)


def main():
    count = 10
    data = list()
    data += speed_import(count)
    data += speed_build_LpStructure(count)
    data += speed_build_QpStructure(count)
    data += speed_create_quadratic_expression(count)
    data += speed_set_polynomial(count)
    data += speed_quadratic_expression_value(count)
    data += speed_sum_operation(count)
    data += speed_func_ce_value(count)

    df = pandas.DataFrame(data)
    print(df.drop("count", axis=1).groupby("name").describe())

    save_file_name = "measure.csv"
    df.to_csv(save_file_name)
    print("statistic file is saved as", save_file_name)


def speed_import(count):
    name = "import"
    data = list()
    for i in tqdm.tqdm(range(count), desc="[ " + name + " ]"):
        output = subprocess.run(
            "python3 -X importtime -c 'import flopt'",
            shell=True,
            capture_output=True,
            text=True,
        )
        flopt_pattern = re.compile(
            "import time:\s+(?P<self>\d*)\s+\|\s+(?P<cumulative>\d*)\s+\| flopt"
        )
        for line in output.stderr.split("\n"):
            m = flopt_pattern.match(line)
            if m is not None:
                data.append(
                    {
                        "name": name,
                        "value": float(m.groupdict()["cumulative"]),
                        "unit": "s",
                        "count": 1,
                    }
                )
    return data


def speed_build_LpStructure(count, prob=None):
    name = "build_LpStructure"
    data = list()
    if prob is None:
        mip_storage = "./datasets/mipLib"
        mps_file = f"{mip_storage}/30n20b8.mps"
        _, pulp_prob = pulp.LpProblem.fromMPS(mps_file)
        prob = flopt.convert.pulp_to_flopt(pulp_prob)

        # set polynomial
        prob.obj.setPolynomial()
        for const in prob.getConstraints():
            const.expression.setPolynomial()

    for i in tqdm.tqdm(range(count), desc="[ " + name + " ]"):
        start_time = time.time()
        lp = flopt.convert.LpStructure.fromFlopt(prob)
        data.append(
            {
                "name": name,
                "value": time.time() - start_time,
                "unit": "s",
                "count": 1,
            }
        )
    return data


def speed_build_QpStructure(count):
    name = "build_QpStructure"
    data = list()
    scales = [1, 100]
    Ns = [400]
    cats = ["Continuous", "Integer", "Binary"]

    for scale, N, cat in itertools.product(scales, Ns, cats):
        _name = name + f"_scale{scale}_N{N}_cat{cat}"

        # sampling Q matrix
        Q = np.random.normal(scale=scale, size=(N, N)).astype(np.int8)

        # create quadratic expression
        x = flopt.Variable.array("x", N, cat=cat)
        q = flopt.Dot(x.T.dot(Q), x)

        # set polynomial
        q.setPolynomial()

        # execute Expression.toQuadratic()
        for i in tqdm.tqdm(range(count), desc="[ " + _name + " ]"):
            start_time = time.time()
            q.toQuadratic()
            data.append(
                {
                    "name": _name,
                    "value": time.time() - start_time,
                    "unit": "s",
                    "count": 1,
                }
            )
    return data


def speed_create_quadratic_expression(count):
    name = "create_quadratic_expression"
    data = list()

    scales = [1, 100]
    Ns = [250]
    cats = ["Continuous", "Integer", "Binary"]

    for scale, N, cat in itertools.product(scales, Ns, cats):
        _name = name + f"_scale{scale}_N{N}_cat{cat}"

        # sampling Q matrix
        Q = np.random.normal(scale=scale, size=(N, N)).astype(np.int8)

        # create quadratic expression
        x = flopt.Variable.array("x", N, cat=cat)
        for i in tqdm.tqdm(range(count), desc="[ " + _name + " ]"):
            start_time = time.time()
            q = x.T.dot(Q).dot(x)
            data.append(
                {
                    "name": _name,
                    "value": time.time() - start_time,
                    "unit": "s",
                    "count": 1,
                }
            )
    return data


def speed_set_polynomial(count):
    name = "set_polynomial"
    data = list()

    scales = [100]
    Ns = [250]
    cats = ["Continuous"]

    for scale, N, cat in itertools.product(scales, Ns, cats):
        _name = name + f"_scale{scale}_N{N}_cat{cat}"

        # sampling Q matrix
        Q = np.random.normal(scale=scale, size=(N, N)).astype(np.int8)

        # create quadratic expression
        x = flopt.Variable.array("x", N, cat=cat)
        for i in tqdm.tqdm(range(count), desc="[ " + _name + " ]"):
            q = flopt.Dot(x.T.dot(Q), x)
            start_time = time.time()
            q.setPolynomial()
            data.append(
                {
                    "name": _name,
                    "value": time.time() - start_time,
                    "unit": "s",
                    "count": 1,
                }
            )
    return data


def speed_quadratic_expression_value(count):
    name = "quadratic_expression_value"
    data = list()

    scales = [1, 100]
    Ns = [40]
    cats = ["Continuous", "Integer", "Binary"]

    for scale, N, cat in itertools.product(scales, Ns, cats):
        _name = name + f"_scale{scale}_N{N}_cat{cat}"

        # sampling Q matrix
        Q = np.random.normal(scale=scale, size=(N, N)).astype(np.int8)

        # create quadratic expression
        x = flopt.Variable.array("x", N, cat=cat, ini_value=1.0)
        q = x.T.dot(Q).dot(x).expand()

        for i in tqdm.tqdm(range(count), desc="[ " + _name + " ]"):
            start_time = time.time()
            _count = 1000
            for j in range(_count):
                q.value()
            data.append(
                {
                    "name": _name,
                    "value": time.time() - start_time,
                    "unit": "s",
                    "count": 1,
                }
            )
    return data


def speed_func_ce_value(count):
    """custome expression value
    """
    name = "func"
    data = list()

    dataset = flopt.performance.get_dataset("func")
    instances = {"Ackley", "Goldstain", "Rosenbrock ", "WeitedSphere"}
    for instance in dataset:
        if instance.name not in instances:
            continue
        _name = name + "_" + instance.name
        random_search = flopt.Solver("RandomSearch")
        formulatable, prob = instance.createProblem(random_search)
        random_search.reset()
        prob.solve(solver=random_search, n_trial=2)
        solution = random_search.best_solution

        for i in tqdm.tqdm(range(count), desc="[ " + _name + " ]"):
            start_time = time.time()
            if instance == {"Ackley", "WeitedSphere"}:
                _count = 1000000
            else:
                _count = 200000
            for j in range(_count):
                obj_value = prob.obj.value(solution)
            data.append(
                {
                    "name": _name,
                    "value": time.time() - start_time,
                    "unit": "s",
                    "count": _count,
                }
            )
    return data


def speed_sum_operation(count):
    name = "sum_operation"
    data = list()

    sizes = [100, 1000, 10000]

    for size in sizes:
        x = flopt.Variable.array("x", size)
        y = flopt.Sum(x)
        solution = flopt.Solution([y])

        _name = name + f"_size{size}"
        for i in tqdm.tqdm(range(count), desc="[ " + _name + " ]"):
            _count = int(10000000 / size)
            for j in range(_count):
                start_time = time.time()
                y.value(solution)
                data.append(
                    {
                        "name": _name,
                        "value": time.time() - start_time,
                        "unit": "s",
                        "count": _count,
                    }
                )
    return data


if __name__ == "__main__":
    main()
