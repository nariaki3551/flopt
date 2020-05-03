from .Ackley       import create_objective as Ackley_co
from .Ackley       import create_variables as Ackley_cv
from .Beale        import create_objective as Beale_co
from .Beale        import create_variables as Beale_cv
from .Booth        import create_objective as Booth_co
from .Booth        import create_variables as Booth_cv
from .Bukin        import create_objective as Bukin_co
from .Bukin        import create_variables as Bukin_cv
from .Camel        import create_objective as Camel_co
from .Camel        import create_variables as Camel_cv
from .DeJongF3     import create_objective as DeJongF3_co
from .DeJongF3     import create_variables as DeJongF3_cv
from .Easom        import create_objective as Easom_co
from .Easom        import create_variables as Easom_cv
from .Eggholder    import create_objective as Eggholder_co
from .Eggholder    import create_variables as Eggholder_cv
from .FiveWell     import create_objective as FiveWell_co
from .FiveWell     import create_variables as FiveWell_cv
from .Ktable       import create_objective as Ktable_co
from .Ktable       import create_variables as Ktable_cv
from .Levi         import create_objective as Levi_co
from .Levi         import create_variables as Levi_cv
from .Matyas       import create_objective as Matyas_co
from .Matyas       import create_variables as Matyas_cv
from .McCormick    import create_objective as McCormick_co
from .McCormick    import create_variables as McCormick_cv
from .Goldstain    import create_objective as Goldstain_co
from .Goldstain    import create_variables as Goldstain_cv
from .Griewank     import create_objective as Griewank_co
from .Griewank     import create_variables as Griewank_cv
from .Rosenbrock   import create_objective as Rosenbrock_co
from .Rosenbrock   import create_variables as Rosenbrock_cv
from .Schaffer2    import create_objective as Schaffer2_co
from .Schaffer2    import create_variables as Schaffer2_cv
from .Schaffer4    import create_objective as Schaffer4_co
from .Schaffer4    import create_variables as Schaffer4_cv
from .Schwefel     import create_objective as Schwefel_co
from .Schwefel     import create_variables as Schwefel_cv
from .Michalewicz  import create_objective as Michalewicz_co
from .Michalewicz  import create_variables as Michalewicz_cv
from .Rastrigin    import create_objective as Rastrigin_co
from .Rastrigin    import create_variables as Rastrigin_cv
from .Sphere       import create_objective as Sphere_co
from .Sphere       import create_variables as Sphere_cv
from .SumDiffPower import create_objective as SumDiffPower_co
from .SumDiffPower import create_variables as SumDiffPower_cv
from .WeitedSphere import create_objective as WeitedSphere_co
from .WeitedSphere import create_variables as WeitedSphere_cv
from .XinShe       import create_objective as XinShe_co
from .XinShe       import create_variables as XinShe_cv
from .Shuberts     import create_objective as Shuberts_co
from .Shuberts     import create_variables as Shuberts_cv
from .SixHump      import create_objective as SixHump_co
from .SixHump      import create_variables as SixHump_cv
from .Zahkarov     import create_objective as Zahkarov_co
from .Zahkarov     import create_variables as Zahkarov_cv

benchmark_func = {
    'Ackley': {'co': Ackley_co, 'cv': Ackley_cv},
    'Beale' : {'co': Beale_co,  'cv': Beale_cv},
    'Booth' : {'co': Booth_co,  'cv': Booth_cv},
    'Sphere': {'co': Sphere_co, 'cv': Sphere_cv},
}

benchmark_func = {
    'Ackley'      : {'co': Ackley_co,       'cv': Ackley_cv},
    'Beale'       : {'co': Beale_co,        'cv': Beale_cv},
    'Booth'       : {'co': Booth_co,        'cv': Booth_cv},
    'Bukin'       : {'co': Bukin_co,        'cv': Bukin_cv},
    'Camel'       : {'co': Camel_co,        'cv': Camel_cv},
    'DeJongF3'    : {'co': DeJongF3_co,     'cv': DeJongF3_cv},
    'Easom'       : {'co': Easom_co,        'cv': Easom_cv},
    'Eggholder'   : {'co': Eggholder_co,    'cv': Eggholder_cv},
    'FiveWell'    : {'co': FiveWell_co,     'cv': FiveWell_cv},
    'Ktable'      : {'co': Ktable_co,       'cv': Ktable_cv},
    'Levi'        : {'co': Levi_co,         'cv': Levi_cv},
    'Matyas'      : {'co': Matyas_co,       'cv': Matyas_cv},
    'McCormick'   : {'co': McCormick_co,    'cv': McCormick_cv},
    'Goldstain'   : {'co': Goldstain_co,    'cv': Goldstain_cv},
    'Griewank'    : {'co': Griewank_co,     'cv': Griewank_cv},
    'Rosenbrock'  : {'co': Rosenbrock_co,   'cv': Rosenbrock_cv},
    'Schaffer2'   : {'co': Schaffer2_co,    'cv': Schaffer2_cv},
    'Schaffer4'   : {'co': Schaffer4_co,    'cv': Schaffer4_cv},
    'Schwefel'    : {'co': Schwefel_co,     'cv': Schwefel_cv},
    'Michalewicz' : {'co': Michalewicz_co,  'cv': Michalewicz_cv},
    'Rastrigin'   : {'co': Rastrigin_co,    'cv': Rastrigin_cv},
    'Sphere'      : {'co': Sphere_co,       'cv': Sphere_cv},
    'SumDiffPower': {'co': SumDiffPower_co, 'cv': SumDiffPower_cv},
    'WeitedSphere': {'co': WeitedSphere_co, 'cv': WeitedSphere_cv},
    'XinShe'      : {'co': XinShe_co,       'cv': XinShe_cv},
    'Shuberts'    : {'co': Shuberts_co,     'cv': Shuberts_cv},
    'SixHump'     : {'co': SixHump_co,      'cv': SixHump_cv},
    'Zahkarov'    : {'co': Zahkarov_co,     'cv': Zahkarov_cv},
}
