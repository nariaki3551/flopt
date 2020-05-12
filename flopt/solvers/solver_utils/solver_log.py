import matplotlib.pyplot as plt
from flopt.env import setup_logger


logger = setup_logger(__name__)


class Log:
    def __init__(self):
        self.logs = list()
    
    def append(self, log_dict):
        self.logs.append(log_dict)
    
    def plot(self, show=True, title=None, label=None,
        xitem='time', xlabel='Time [s]',
        yitem='obj_value', ylabel='Objective value',
        xscale='linear', yscale='linear',
        linestyle='-', marker=None,
        fig=None, ax=None):
        if ax is None:
            fig, ax = plt.subplots()
            ax.grid(ls='--')
            ax.set_title(title)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.set_xscale(xscale)
            ax.set_yscale(yscale)
        X = [log[xitem] for log in self.logs]
        Y = [log[yitem] for log in self.logs]
        
        ax.plot(X, Y, linestyle=linestyle, marker=marker, label=label)
        ax.legend()

        if show:
            plt.show()

        return fig, ax

    def __getitem__(self, k):
        return self.logs[k]
