from flopt.env import setup_logger
from flopt.constants import VERSION, DATE, VariableType, SolverTerminateState


logger = setup_logger(__name__)


def start_solver_message(algo_name, param_str, solution):
    # stat about variables
    n_var = len(solution)
    n_binary_var = sum(var.type() == VariableType.Binary for var in solution)
    n_spin_var = sum(var.type() == VariableType.Spin for var in solution)
    n_int_var = sum(var.type() == VariableType.Integer for var in solution)
    n_cont_var = sum(var.type() == VariableType.Continuous for var in solution)
    n_perm_var = sum(var.type() == VariableType.Permutation for var in solution)
    n_perm_var_elm = sum(
        len(var) for var in solution if var.type() == VariableType.Permutation
    )

    message = (
        "\n",
        f"# - - - - - - - - - - - - - - #\n",
        f"  Welcome to the flopt Solver\n",
        f"  Version {VERSION}\n",
        f"  Date: {DATE}\n",
        f"# - - - - - - - - - - - - - - #\n",
        "\n",
        f"Algorithm: {algo_name}\n",
        f"Params: {param_str}\n",
        f"Number of variables {n_var} ",
        f"(continuous {n_cont_var} ",
        f", int {n_int_var}",
        f", binary {n_binary_var}",
        f", spin {n_spin_var}",
        f", permutation {n_perm_var} ({n_perm_var_elm}))\n" "\n",
    )
    print("".join(message))


def during_solver_message_header():
    header1 = "                               relative  absolute"
    header2 = "     Trial Incumbent    BestBd   Gap[%]       Gap Time[s]"
    line = "---------------------------------------------------------"
    print(header1)
    print(header2)
    print(line)


def value2str(value):
    if value is None:
        return " " * 8 + "-"
    if abs(value) > 1e4:
        value_str = f"{value:9.2e}"
    elif abs(value) > 1e-3:
        value_str = f"{value:9.3f}"
    else:
        value_str = f"{value:9.5f}"
    return value_str


def calculate_relative_gap(obj_value, best_bound):
    if obj_value is None or best_bound is None:
        return " " * 7 + "-"
    else:
        gap = (obj_value - best_bound) / (abs(obj_value) + 1e-4) * 100
        if gap > 99.9:
            return " " * 8
        else:
            return f"{gap:8.3f}"


def calculate_abs_gap(obj_value, best_bound):
    if obj_value is None or best_bound is None:
        return " " * 8 + "-"
    else:
        gap = obj_value - best_bound
        if gap > 10:
            return " " * 9
        else:
            return f"{gap:9.6f}"


def during_solver_message(head, obj_value, best_bound, time, iteration):
    obj_value_str = value2str(obj_value)
    best_bound_str = value2str(best_bound)
    relative_gap_str = calculate_relative_gap(obj_value, best_bound)
    abs_gap_str = calculate_abs_gap(obj_value, best_bound)
    message = (
        f"{head:2s}",
        f"{iteration:7d}",
        f"{obj_value_str}",
        f"{best_bound_str}",
        f"{relative_gap_str}",
        f"{abs_gap_str}",
        f"{time:7.2f}",
    )
    print(" ".join(message))


def end_solver_message(status, obj_value, build_time, elapsed_time, num_trials):
    message = (
        "",
        f"Status: {status.__str__()}",
        f"Objective Value: {obj_value}",
        f"Time: {elapsed_time}",
        f"    Build Time: {build_time}",
        f"    Search Time: {elapsed_time - build_time}",
        f"Trials: {num_trials}",
    )
    print("\n".join(message))
