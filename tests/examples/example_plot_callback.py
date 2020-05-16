import numpy as np
import matplotlib.pyplot as plt

class Plot2DFunc:
    def __init__(self, func):
        self.ix = 0
        self.func = func
    
    def plotFunc(self, ax):
        # X, Y, Z
        interval = 0.1
        x = np.arange(-10, 10+interval, interval)
        y = np.arange(-10, 10+interval, interval)
        Z = np.zeros((len(x), len(y)))
        for x_ix in range(len(x)):
            for y_ix in range(len(y)):
                Z[x_ix, y_ix] = self.func(x[x_ix], y[y_ix])
        X, Y = np.meshgrid(x, y)
        ax.contour(X, Y, Z)
        return ax
    
    def plot(self, solutions, best_solution, best_obj_value, ax):
        # functioin
        ax = self.plotFunc(ax)
        
        # solution
        x = [solution[0] for solution in solutions]
        y = [solution[1] for solution in solutions]
        ax.plot(x, y, 'o', label='curr solution')

        # best_solution
        x, y = best_solution[0], best_solution[1]
        ax.plot(x, y, 'o', label='best solution')

        ax.legend()

    
    def __call__(self, solutions, best_solution, best_obj_value):
        fig, ax = plt.subplots()
        self.plot(solutions, best_solution, best_obj_value, ax)
        plt.show()


if __name__ == '__main__':

    from flopt import Variable, Problem, Solver, CustomExpression

    def test_func(x, y):
        return (1.5-x+x*y)**2 + (2.25-x+x*y*y)**2 + (2.625-x+x*y*y*y)**2
    
    plot_2d_func = Plot2DFunc(test_func)

    x = Variable('x', lowBound=-10, upBound=10, cat='Continuous')
    y = Variable('y', lowBound=-10, upBound=10, cat='Continuous')

    obj = CustomExpression(test_func, [x, y])

    prob = Problem('plot test')
    prob += obj

    solver = Solver(algo='SFLA')
    solver.setParams(n_trial=10, callbacks=[plot_2d_func])
    prob.solve(solver, msg=True)
