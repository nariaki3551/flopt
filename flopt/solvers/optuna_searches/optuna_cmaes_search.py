from .base_optuna import OptunaSearch

class OptunaCmaEsSearch(OptunaSearch):
    """
    CmaEsSearch of Optuna.
    https://optuna.readthedocs.io/en/latest/reference/samplers.html#optuna.samplers.CmaEsSampler

    Parameters
    ----------
    x0
    sigma0
    n_startup_trials
    independent_sampler
    warn_independe_sampling
    seed
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
        from optuna.study import create_study
        from optuna.samplers import CmaEsSampler
        from optuna.logging import disable_default_handler
        disable_default_handler()
        # initial value
        x0 = {var.name: var.value() for var in self.solution}
        sampler = CmaEsSampler(
            x0 = x0,
            sigma0 = self.sigma0,
            n_startup_trials = self.n_startup_trials,
            independent_sampler = self.independent_sampler,
            warn_independent_sampling = self.warn_independent_sampling,
            seed = self.seed
        )
        self.study = create_study(sampler=sampler)

