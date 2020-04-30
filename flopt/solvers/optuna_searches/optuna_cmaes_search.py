import optuna
from optuna.samplers import CmaEsSampler
from .base_optuna import OptunaSearch

class OptunaCmaEsSearch(OptunaSearch):
    """
    CmaEsSearch with Optuna.
    """
    def __init__(self):
        super().__init__()
        self.name = 'OptunaCmaEsSearch'
        self.can_solve_problems = ['blackbox']
        self.x0 = None
        self.sigma0 = None
        self.n_startup_trials = 1
        self.independent_sampler = None
        self.warn_independent_sampling = True
        self.seed = None

    def createStudy(self):
        sampler = CmaEsSampler(
            x0 = self.x0,
            sigma0 = self.sigma0,
            n_startup_trials = self.n_startup_trials,
            independent_sampler = self.independent_sampler,
            warn_independent_sampling = self.warn_independent_sampling,
            seed = self.seed
        )
        self.study = optuna.study.create_study(sampler=sampler)
