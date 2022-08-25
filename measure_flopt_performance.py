import re
import time
import itertools
import subprocess

import tqdm
import pulp
import pandas
import numpy as np
import memory_profiler

import flopt
import flopt.convert
import flopt.performance

np.random.seed(0)


def main():
    count = 10
    data = list()
    data += measure_import(count)
    data += measure_build_LpStructure(count)
    data += measure_build_QpStructure(count)
    data += measure_create_quadratic_expression(count)
    data += measure_set_polynomial(count)
    data += measure_sum_operation(count)

    # count = 5
    data += measure_func(count)

    df = pandas.DataFrame(data)
    print(df.drop("count", axis=1).groupby("name").describe())

    save_file_name = "measure.csv"
    df.to_csv(save_file_name)
    print("statistic file is saved as", save_file_name)


def measure_import(count):
    measure_name = "import"
    data = list()
    for i in tqdm.tqdm(range(count), desc="[ " + measure_name + " ]"):
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
                        "name": measure_name,
                        "value": float(m.groupdict()["cumulative"]),
                        "unit": "s",
                        "count": 1,
                    }
                )
    return data


def measure_build_LpStructure(count, prob=None):
    measure_name = "build_LpStructure"
    data = list()
    if prob is None:
        mip_storage = "./datasets/mipLib"
        mps_file = f"{mip_storage}/30n20b8.mps"
        _, pulp_prob = pulp.LpProblem.fromMPS(mps_file)
        prob = flopt.convert.pulp_to_flopt(pulp_prob)

        # set polynomial
        prob.obj.setPolynomial()
        for const in prob.constraints:
            const.expression.setPolynomial()

    for i in tqdm.tqdm(range(count), desc="[ " + measure_name + " ]"):
        start_time = time.time()
        lp = flopt.convert.LpStructure.fromFlopt(prob)
        data.append(
            {
                "name": measure_name,
                "value": time.time() - start_time,
                "unit": "s",
                "count": 1,
            }
        )
    return data


def memory_build_LpStructure(count):
    measure_name = "memory_build_LpStructure"
    data = list()
    mip_storage = "./datasets/mipLib"
    mps_file = f"{mip_storage}/30n20b8.mps"
    _, pulp_prob = pulp.LpProblem.fromMPS(mps_file)
    prob = flopt.convert.pulp_to_flopt(pulp_prob)

    # set polynomial
    prob.expression.setPolynomial()
    for const in prob.constraints:
        const.expression.setPolynomial()

    for i in tqdm.tqdm(range(count), desc="[ " + measure_name + " ]"):
        memory = max(
            memory_profiler.memory_usage((measure_build_LpStructure, (1, prob)))
        )
        data.append(
            {
                "name": measure_name,
                "value": memory,
                "unit": "MB",
                "count": 1,
            }
        )
    return data


def measure_build_QpStructure(count):
    measure_name = "build_QpStructure"
    data = list()
    scales = [1, 100]
    Ns = [400]
    cats = ["Continuous", "Integer", "Binary"]

    for scale, N, cat in itertools.product(scales, Ns, cats):
        _measure_name = measure_name + f"_scale{scale}_N{N}_cat{cat}"

        # sampling Q matrix
        Q = np.random.normal(scale=scale, size=(N, N)).astype(np.int8)

        # create quadratic expression
        x = flopt.Variable.array("x", N, cat=cat)
        q = x.T.dot(Q).dot(x)

        # set polynomial
        q.setPolynomial()

        # execute Expression.toQuadratic()
        for i in tqdm.tqdm(range(count), desc="[ " + _measure_name + " ]"):
            start_time = time.time()
            q.toQuadratic()
            data.append(
                {
                    "name": _measure_name,
                    "value": time.time() - start_time,
                    "unit": "s",
                    "count": 1,
                }
            )
    return data


def memory_build_QpStructure(count):
    measure_name = "memory_build_QpStructure"
    data = list()
    for i in tqdm.tqdm(range(count), desc="[ " + measure_name + " ]"):
        memory = max(memory_profiler.memory_usage((measure_build_QpStructure, (1,))))
        data.append(
            {
                "name": measure_name,
                "value": memory,
                "unit": "MB",
                "count": 1,
            }
        )
    return data


def measure_create_quadratic_expression(count):
    measure_name = "create_quadratic_expression"
    data = list()

    scales = [1, 100]
    Ns = [250]
    cats = ["Continuous", "Integer", "Binary"]

    for scale, N, cat in itertools.product(scales, Ns, cats):
        _measure_name = measure_name + f"_scale{scale}_N{N}_cat{cat}"

        # sampling Q matrix
        Q = np.random.normal(scale=scale, size=(N, N)).astype(np.int8)

        # create quadratic expression
        x = flopt.Variable.array("x", N, cat=cat)
        for i in tqdm.tqdm(range(count), desc="[ " + _measure_name + " ]"):
            start_time = time.time()
            q = x.T.dot(Q).dot(x)
            data.append(
                {
                    "name": _measure_name,
                    "value": time.time() - start_time,
                    "unit": "s",
                    "count": 1,
                }
            )
    return data


def memory_create_quadratic_expression(count):
    measure_name = "memory_create_quadratic_expression"
    data = list()
    for i in tqdm.tqdm(range(count), desc="[ " + measure_name + " ]"):
        memory = max(
            memory_profiler.memory_usage((measure_create_quadratic_expression, (1,)))
        )
        data.append(
            {
                "name": measure_name,
                "value": memory,
                "unit": "MB",
                "count": 1,
            }
        )
    return data


def measure_set_polynomial(count):
    measure_name = "set_polynomial"
    data = list()

    scales = [1, 100]
    Ns = [250]
    cats = ["Continuous", "Integer", "Binary"]

    for scale, N, cat in itertools.product(scales, Ns, cats):
        _measure_name = measure_name + f"_scale{scale}_N{N}_cat{cat}"

        # sampling Q matrix
        Q = np.random.normal(scale=scale, size=(N, N)).astype(np.int8)

        # create quadratic expression
        x = flopt.Variable.array("x", N, cat=cat)
        for i in tqdm.tqdm(range(count), desc="[ " + _measure_name + " ]"):
            q = x.T.dot(Q).dot(x)
            start_time = time.time()
            q.setPolynomial()
            data.append(
                {
                    "name": _measure_name,
                    "value": time.time() - start_time,
                    "unit": "s",
                    "count": 1,
                }
            )
    return data


def measure_func(count):
    measure_name = "func"
    data = list()

    dataset = flopt.performance.get_dataset("func")
    instances = {"Ackley", "Goldstain", "Rosenbrock ", "WeitedSphere"}
    for instance in dataset:
        if instance.name not in instances:
            continue
        _measure_name = measure_name + "_" + instance.name
        random_search = flopt.Solver("RandomSearch")
        formulatable, prob = instance.createProblem(random_search)
        random_search.reset()
        solution = random_search.solution

        for i in tqdm.tqdm(range(count), desc="[ " + _measure_name + " ]"):
            start_time = time.time()
            if instance == {"Ackley", "WeitedSphere"}:
                _count = 10000
            else:
                _count = 2000
            for j in range(_count):
                obj_value = prob.obj.value(solution)
            data.append(
                {
                    "name": _measure_name,
                    "value": time.time() - start_time,
                    "unit": "s",
                    "count": _count,
                }
            )
    return data


def memory_func(count):
    measure_name = "memory_func"
    data = list()
    for i in tqdm.tqdm(range(count), desc="[ " + measure_name + " ]"):
        memory = max(memory_profiler.memory_usage((measure_func, (1,))))
        data.append(
            {
                "name": measure_name,
                "value": memory,
                "unit": "MB",
                "count": 1,
            }
        )
    return data


def measure_sum_operation(count):
    measure_name = "sum_operation"
    data = list()

    sizes = [100, 1000, 10000]

    for size in sizes:
        x = flopt.Variable.array("x", size)
        y = flopt.Sum(x)
        solution = flopt.Solution("tmp", [y])

        _measure_name = measure_name + f"_size{size}"
        for i in tqdm.tqdm(range(count), desc="[ " + _measure_name + " ]"):
            _count = int(10000000 / size)
            for j in range(_count):
                start_time = time.time()
                y.value(solution)
                data.append(
                    {
                        "name": _measure_name,
                        "value": time.time() - start_time,
                        "unit": "s",
                        "count": _count,
                    }
                )
    return data


if __name__ == "__main__":
    main()
