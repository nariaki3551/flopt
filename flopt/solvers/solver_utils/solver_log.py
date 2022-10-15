import heapq

from flopt.env import setup_logger


logger = setup_logger(__name__)


class Log:
    def __init__(self):
        self.logs = list()
        self.solutions = list()
        heapq.heapify(self.solutions)

    def append(self, log_dict):
        self.logs.append(log_dict)

    def appendSolution(self, solution, obj_value, max_k):
        if len(self.solutions) < max_k:
            heapq.heappush(self.solutions, (obj_value, solution))
        else:
            heapq.heappushpop(self.solutions, (obj_value, solution))

    def getLog(self, time=None, iteration=None):
        if time is None and iteration is None:
            return self.logs[-1]
        for pre_log, log in zip(self.logs[:], self.logs[1:]):
            if time is not None:
                if log["time"] > time:
                    return pre_log
            if iteration is not None:
                if log["iteration"] > iteration:
                    return pre_log
        return self.logs[-1]

    def getSolution(self, k=1):
        """get the k-top solutions"""
        self.solutions.sort()
        return self.solutions[k - 1][1]

    def plot(
        self,
        show=True,
        title=None,
        xitem="time",
        xlabel="Time [s]",
        yitem="obj_value",
        ylabel="Objective value",
        xscale="linear",
        yscale="linear",
        fig=None,
        ax=None,
        *args,
        **kwargs
    ):
        import matplotlib.pyplot as plt

        if ax is None:
            fig, ax = plt.subplots()
            ax.grid(ls="--")
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.set_xscale(xscale)
            ax.set_yscale(yscale)
        X = [log[xitem] for log in self.logs]
        Y = [log[yitem] for log in self.logs]

        ax.plot(X, Y, *args, **kwargs)
        if "label" in kwargs:
            ax.legend()

        if show:
            plt.show()

        return fig, ax

    def __getitem__(self, k):
        return self.logs[k]

    def __len__(self):
        return len(self.logs)

    def __iadd__(self, other):
        assert isinstance(other, Log)
        if self.logs:
            last_time = self.logs[-1]["time"]
        else:
            last_time = 0.0
        logs = list(other.logs)
        for log in logs:
            log["time"] += last_time
        self.logs += logs
        return self

    def __add__(self, other):
        assert isinstance(other, Log)
        solver_log = Log()
        solver_log += self
        solver_log += other
        return solver_log
