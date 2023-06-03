import os
import glob
import random
import argparse
import itertools

import dill
import numpy as np

import flopt


random.seed(0)
np.random.seed(0)


class Model:
    def __init__(self, model):
        self.model = model

    def features(self, prob, solver):
        return [solver.timelimit, len(prob.getVariables())]

    def output(self, features):
        return self.model.predict(features)


def create_nonlinear_datasets(num_probs, cat, args):

    time_span = [1, 120]
    num_variables_span = [2, 1000]

    funcs = [
        "Ackley",
        "Ellipsoid",
        "Griewank",
        "Ktable",
        "Rastrigin",
        "Rosenbrock",
        "Schwefel",
        "Sphere",
        "SumDiffPower",
        "WeightedSphere",
        "XinShe",
        "Zahkarov",
    ]

    func_dataset = flopt.performance.get_dataset("func")

    if args.debug:
        time_span = [1, 5]
        num_variables_span = [2, 100]

    for i in range(num_probs + args.begin_ix):
        name = random.choice(funcs)
        timelimit = random.randint(time_span[0], time_span[1])
        n = random.randint(num_variables_span[0], num_variables_span[1])

        if i < args.begin_ix:
            continue

        # carete problem and custom dataset
        func_instance = func_dataset[name]
        prob = func_instance.createProblemFunc(n=n, cat=cat)
        cd = flopt.performance.CustomDataset(name="FuncLib", probs=[prob])

        yield (cd, {"name": name, "num_variables": n, "timelimit": timelimit})


def create_number_partitioning_datasets(num_probs, args):

    time_span = [1, 120]
    num_variables_span = [2, 1000]

    if args.debug:
        time_span = [1, 5]
        num_variables_span = [2, 100]

    for i in range(num_probs + args.begin_ix):
        timelimit = random.randint(time_span[0], time_span[1])
        n = random.randint(num_variables_span[0], num_variables_span[1])

        if i < args.begin_ix:
            continue

        # create problem and custom datasets
        A = [random.randint(0, 2**100) for _ in range(n)]
        s = flopt.Variable.array("s", len(A), cat="Spin")
        prob = flopt.Problem(f"number_partitioning_{n}elements")
        prob += flopt.Dot(s, A) ** 2
        cd = flopt.performance.CustomDataset(name="Number Partitioning", probs=[prob])

        yield (cd, {"num_variables": n, "timelimit": timelimit})


def fitting_and_save_model(args):
    import seaborn
    import matplotlib.pyplot as plt
    import pandas
    import sklearn.model_selection
    import sklearn.tree
    import sklearn.ensemble
    import sklearn.naive_bayes

    folder = os.path.join(args.save_dir, args.problem_class)

    # collect data
    logfiles = glob.glob(os.path.join(folder, "logs_*.pickle"))

    times = list(np.linspace(1, 120))

    data = list()
    for logfile in logfiles:
        with open(logfile, "rb") as f:
            (instance, logs) = dill.load(f)

        sampled_times = random.sample(times, 3)
        for time in sampled_times:
            best_algos = list()
            best_obj_value = float("inf")
            best_obj_time = float("inf")
            for key, algo_log in logs.items():
                _, _, algo = key
                if algo == "auto":
                    continue
                obj_value = float("inf")
                for log in algo_log.logs:
                    if log["time"] < time:
                        obj_value = log["obj_value"]
                if obj_value < best_obj_value - 1e-5:
                    best_obj_value = obj_value
                    best_algos = [(algo, obj_value)]
                elif obj_value < best_obj_value + 1e-5:
                    best_algos += [(algo, obj_value)]

            for algo, obj_value in best_algos:
                data.append(
                    {
                        "algo": algo,
                        "timelimit": time,
                        "#variables": instance["num_variables"],
                        "obj_value": obj_value,
                    }
                )

    df = pandas.DataFrame(data)
    algos = [algo for algo in flopt.Solver_list() if any(df["algo"] == algo)]
    pallet = plt.get_cmap("tab10")
    color_pallet = {algo: pallet(i) for i, algo in enumerate(algos)}

    # visualize data
    df_plot = df.copy()
    jitter_size = 5
    df_plot["timelimit"] += jitter_size * np.random.random(len(df)) - 0.5 * jitter_size
    df_plot["#variables"] += jitter_size * np.random.random(len(df)) - 0.5 * jitter_size
    fig, ax = plt.subplots()
    for algo in algos:
        seaborn.scatterplot(
            data=df_plot[df["algo"] == algo],
            x="timelimit",
            y="#variables",
            color=color_pallet[algo],
            label=algo,
            ax=ax,
        )
    ax.grid("--")
    ax.legend(bbox_to_anchor=(1.01, 1.0), loc="upper left")
    fig.savefig(f"{args.problem_class}.training_data.png", bbox_inches="tight")
    plt.show()

    # split train and test data
    X_train, X_test, Y_train, Y_test = sklearn.model_selection.train_test_split(
        df[["timelimit", "#variables"]].to_numpy(),
        df[["algo"]].to_numpy(),
        random_state=0,
    )

    # fitting
    max_model = None
    max_score = -float("inf")
    skmodels = [
        sklearn.tree.DecisionTreeClassifier(),
        sklearn.neighbors.KNeighborsClassifier(),
        sklearn.ensemble.RandomForestClassifier(),
        sklearn.ensemble.GradientBoostingClassifier(),
        sklearn.svm.SVC(),
        sklearn.linear_model.SGDClassifier(),
        sklearn.naive_bayes.GaussianNB(),
    ]
    for skmodel in skmodels:
        num_predict_best = 0
        model = skmodel
        model.fit(
            X_train,
            Y_train.reshape(
                -1,
            ),
        )
        for x_test in X_test:
            predict = model.predict([x_test])
            idxs = (df["timelimit"] == x_test[0]) & (df["#variables"] == x_test[1])
            if predict in df[idxs]["algo"].unique():
                num_predict_best += 1
        print(
            f"{model.__str__():>30}: num_predict_best {num_predict_best} rate {num_predict_best/len(X_test)}"
        )
        if num_predict_best > max_score:
            max_model = model
            max_score = num_predict_best

    model = max_model

    # visualize result
    times = np.linspace(1, 120)
    num_variables = np.linspace(1, 1000)
    data = [
        {"timelimit": time, "#variables": num_variable}
        for time, num_variable in itertools.product(times, num_variables)
    ]
    df = pandas.DataFrame(data)
    df["algo"] = model.predict(df[["timelimit", "#variables"]].to_numpy())
    fig, ax = plt.subplots()
    for algo in algos:
        seaborn.scatterplot(
            data=df[df["algo"] == algo],
            x="timelimit",
            y="#variables",
            color=color_pallet[algo],
            label=algo,
            ax=ax,
        )
    ax.grid("--")
    ax.legend(bbox_to_anchor=(1.01, 1.0), loc="upper left")
    fig.savefig(f"{args.problem_class}.fitting_result.png", bbox_inches="tight")
    plt.show()

    # create selector
    model = Model(model)

    # save model
    save_path = os.path.join(args.save_dir, f"{args.problem_class}.model.pickle")
    with open(save_path, "wb") as f:
        dill.dump(model, file=f)
    print("save model as", save_path)


def main(args):

    if args.collect:
        if args.problem_class == "nonlinear":
            datasets_iter = create_nonlinear_datasets(args.samples, "Continuous", args)
        elif args.problem_class == "nonlinear_mip":
            datasets_iter = create_nonlinear_datasets(args.samples, "Integer", args)
        elif args.problem_class == "ising":
            datasets_iter = create_number_partitioning_datasets(args.samples, args)
        else:
            assert True

        folder = os.path.join(args.save_dir, args.problem_class)
        os.makedirs(folder, exist_ok=True)

        for i, (cd, instance) in enumerate(datasets_iter, start=args.begin_ix):
            print(cd)

            solvers = "all"
            logs = flopt.performance.compute(
                cd, solvers, timelimit=instance["timelimit"]
            )

            if args.debug:
                continue
            with open(os.path.join(folder, f"logs_{i}.pickle"), "wb") as pf:
                dill.dump((instance, logs), file=pf)

    elif not args.debug:
        fitting_and_save_model(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "problem_class", type=str, choices=["nonlinear", "nonlinear_mip", "ising"]
    )
    parser.add_argument("--samples", type=int, default=100)
    parser.add_argument("--begin_ix", type=int, default=0)
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--save_dir", type=str, default=os.path.join("flopt", "tuning"))
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    main(args)
