import matplotlib.pyplot as plt

class Log:
    def __init__(self):
        self.solutions = list()
    
    def append(self, log_dict):
        self.solutions.append(log_dict)
    
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
        X = [sol[xitem] for sol in self.solutions]
        Y = [sol[yitem] for sol in self.solutions]
        
        ax.plot(X, Y, linestyle=linestyle, marker=marker, label=label)
        ax.legend()

        if show:
            plt.show()

        return fig, ax
