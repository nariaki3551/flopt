from .base_optuna import OptunaSearch

class OptunaTPESearch(OptunaSearch):
    """
    Tree-structured Parzen Estimator (TPE) Sampling Search of Optuna.
    https://optuna.readthedocs.io/en/latest/reference/samplers.html#optuna.samplers.TPESampler


    Parameters
    ----------
    name : str
        name
    consider_prior : bool
    consider_magic_clip : bool
    consider_endpoints : bool
    n_startup_trials : int
    n_ei_candidates : int
    seed : float
        seed of random generater
    """
    def __init__(self):
        super().__init__()
        self.name = 'OptunaTPESearch'
        self.can_solve_problems = ['blackbox']
        self.consider_prior = True
        self.prior_weight = 1.0
        self.consider_magic_clip = True
        self.consider_endpoints = False
        self.n_startup_trials = 10
        self.n_ei_candidates = 24
        self.seed = None


    def createStudy(self):
        """
        create sampler and create Study object
        """
        from optuna.study import create_study
        from optuna.samplers import TPESampler
        from optuna.logging import disable_default_handler
        disable_default_handler()
        sampler = TPESampler(
            consider_prior = self.consider_prior,
            prior_weight = self.prior_weight,
            consider_magic_clip = self.consider_magic_clip,
            consider_endpoints = self.consider_endpoints,
            n_startup_trials = self.n_startup_trials,
            n_ei_candidates = self.n_ei_candidates,
            seed = self.seed
        )
        self.study = create_study(sampler=sampler)

