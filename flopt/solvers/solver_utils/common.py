from flopt.env import setup_logger
import flopt.constants


logger = setup_logger(__name__)


def start_solver_message(algo_name, param_str, solution):
    # stat about variables
    n_var = len(solution)
    n_binary_var = sum(
        var.getType() == 'VarBinary'
        for var in solution
    )
    n_int_var = sum(
        var.getType() == 'VarInteger'
        for var in solution)
    n_cont_var = sum(
        var.getType() == 'VarContinuous'
        for var in solution
    )
    n_perm_var = sum(
        var.getType() == 'VarPermutation'
        for var in solution
    )
    n_perm_var_elm = sum(
        len(var)
        for var in solution
        if var.getType() == 'VarPermutation'
    )

    message = (
        "\n",
        "Welcome to the flopt Solver\n",
        f"Version {flopt.constants.VERSION}\n",
        f"Date: {flopt.constants.DATE}\n",
        "\n",
        f"Algorithm: {algo_name}\n",
        f"Params: {param_str}\n",
        f"Number of variables {n_var} ",
        f"(continuous {n_cont_var} ",
        f", int {n_int_var}",
        f", binary {n_binary_var}",
        f", permutation {n_perm_var} ({n_perm_var_elm}))\n"
        "\n"
    )
    print(''.join(message))


def during_solver_message_header():
    header = '     Trial Incumbent    BestBd  Gap[%] Time[s]'
    line   = '----------------------------------------------'
    print(header)
    print(line)


def value2str(value):
    if value is None:
        return ' '*8 + '-'
    if abs(value) > 1e4:
        value_str = f'{value:9.2e}'
    elif abs(value) > 1e-3:
        value_str = f'{value:9.3f}'
    else:
        value_str = f'{value:9.5f}'
    return value_str


def calculate_gap(obj_value, best_bd):
    if obj_value is None or best_bd is None:
        return ' '*6 + '-'
    else:
        gap = (obj_value - best_bd) / (abs(obj_value)+1e-4) * 100
        if gap > 99.9:
            return ' '*7
        else:
            return f'{gap:7.2f}'


def during_solver_message(head, obj_value, best_bd, time, iteration):
    obj_value_str = value2str(obj_value)
    best_bd_str   = value2str(best_bd)
    gap_str = calculate_gap(obj_value, best_bd)
    message = (
        f'{head:2s}',
        f'{iteration:7d}',
        f'{obj_value_str}',
        f'{best_bd_str}',
        f'{gap_str}',
        f'{time:7.2f}'
    )
    print(' '.join(message))


def end_solver_message(status, obj_value, time):
    status_str = {
        flopt.constants.SOLVER_NORMAL_TERMINATE:    'normal termination',
        flopt.constants.SOLVER_TIMELIMIT_TERMINATE: 'timelimit termination',
        flopt.constants.SOLVER_INTERRUPT_TERMINATE: 'Ctrl-C termination',
        flopt.constants.SOLVER_ABNORMAL_TERMINATE:  'abnormal termination'
    }

    message = (
        "",
        f"Status: {status_str[status]}",
        f"Objective Value: {obj_value}",
        f"Time: {time}"
        ""
    )
    print('\n'.join(message))
