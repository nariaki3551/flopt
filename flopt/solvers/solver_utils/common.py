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
        "Version 0.0\n",
        "Build Date: Mar 28 2020\n",
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
    header = '     Trial  ObjValue Time[s]'
    line   = '----------------------------'
    print(header)
    print(line)

def during_solver_message(head, obj_value, time, iteration):
    print(f'{head:2s} {iteration:7d} {obj_value:9.3f} {time:7.2f}')


def end_solver_message(status, obj_value, time):
    status_str = {
        0: 'normal termination',
        1: 'timelimit termination',
        2: 'Ctrl-C termination',
        3: 'abnormal termination'
    }
    
    message = (
        "",
        f"Status: {status_str[status]}",
        f"Objective Value: {obj_value}",
        f"Time: {time}"
        ""
    )
    print('\n'.join(message))
