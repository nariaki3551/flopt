from .Ackley       import create_objective as Ackley_co
from .Ackley       import create_variables as Ackley_cv
from .Ackley       import minimum_obj      as Ackley_mo
from .Beale        import create_objective as Beale_co
from .Beale        import create_variables as Beale_cv
from .Beale        import minimum_obj      as Beale_mo
from .Booth        import create_objective as Booth_co
from .Booth        import create_variables as Booth_cv
from .Booth        import minimum_obj      as Booth_mo
from .Bukin        import create_objective as Bukin_co
from .Bukin        import create_variables as Bukin_cv
from .Bukin        import minimum_obj      as Bukin_mo
from .Camel        import create_objective as Camel_co
from .Camel        import create_variables as Camel_cv
from .Camel        import minimum_obj      as Camel_mo
from .DeJongF3     import create_objective as DeJongF3_co
from .DeJongF3     import create_variables as DeJongF3_cv
from .DeJongF3     import minimum_obj      as DeJongF3_mo
from .Easom        import create_objective as Easom_co
from .Easom        import create_variables as Easom_cv
from .Easom        import minimum_obj      as Easom_mo
from .Eggholder    import create_objective as Eggholder_co
from .Eggholder    import create_variables as Eggholder_cv
from .Eggholder    import minimum_obj      as Eggholder_mo
from .FiveWell     import create_objective as FiveWell_co
from .FiveWell     import create_variables as FiveWell_cv
from .FiveWell     import minimum_obj      as FiveWell_mo
from .Ktable       import create_objective as Ktable_co
from .Ktable       import create_variables as Ktable_cv
from .Ktable       import minimum_obj      as Ktable_mo
from .Levi         import create_objective as Levi_co
from .Levi         import create_variables as Levi_cv
from .Levi         import minimum_obj      as Levi_mo
from .Matyas       import create_objective as Matyas_co
from .Matyas       import create_variables as Matyas_cv
from .Matyas       import minimum_obj      as Matyas_mo
from .McCormick    import create_objective as McCormick_co
from .McCormick    import create_variables as McCormick_cv
from .McCormick    import minimum_obj      as McCormick_mo
from .Goldstain    import create_objective as Goldstain_co
from .Goldstain    import create_variables as Goldstain_cv
from .Goldstain    import minimum_obj      as Goldstain_mo
from .Griewank     import create_objective as Griewank_co
from .Griewank     import create_variables as Griewank_cv
from .Griewank     import minimum_obj      as Griewank_mo
from .Rosenbrock   import create_objective as Rosenbrock_co
from .Rosenbrock   import create_variables as Rosenbrock_cv
from .Rosenbrock   import minimum_obj      as Rosenbrock_mo
from .Schaffer2    import create_objective as Schaffer2_co
from .Schaffer2    import create_variables as Schaffer2_cv
from .Schaffer2    import minimum_obj      as Schaffer2_mo
from .Schaffer4    import create_objective as Schaffer4_co
from .Schaffer4    import create_variables as Schaffer4_cv
from .Schaffer4    import minimum_obj      as Schaffer4_mo
from .Schwefel     import create_objective as Schwefel_co
from .Schwefel     import create_variables as Schwefel_cv
from .Schwefel     import minimum_obj      as Schwefel_mo
from .Michalewicz  import create_objective as Michalewicz_co
from .Michalewicz  import create_variables as Michalewicz_cv
from .Michalewicz  import minimum_obj      as Michalewicz_mo
from .Rastrigin    import create_objective as Rastrigin_co
from .Rastrigin    import create_variables as Rastrigin_cv
from .Rastrigin    import minimum_obj      as Rastrigin_mo
from .Sphere       import create_objective as Sphere_co
from .Sphere       import create_variables as Sphere_cv
from .Sphere       import minimum_obj      as Sphere_mo
from .SumDiffPower import create_objective as SumDiffPower_co
from .SumDiffPower import create_variables as SumDiffPower_cv
from .SumDiffPower import minimum_obj      as SumDiffPower_mo
from .WeitedSphere import create_objective as WeitedSphere_co
from .WeitedSphere import create_variables as WeitedSphere_cv
from .WeitedSphere import minimum_obj      as WeitedSphere_mo
from .XinShe       import create_objective as XinShe_co
from .XinShe       import create_variables as XinShe_cv
from .XinShe       import minimum_obj      as XinShe_mo
from .Shuberts     import create_objective as Shuberts_co
from .Shuberts     import create_variables as Shuberts_cv
from .Shuberts     import minimum_obj      as Shuberts_mo
from .SixHump      import create_objective as SixHump_co
from .SixHump      import create_variables as SixHump_cv
from .SixHump      import minimum_obj      as SixHump_mo
from .Zahkarov     import create_objective as Zahkarov_co
from .Zahkarov     import create_variables as Zahkarov_cv
from .Zahkarov     import minimum_obj      as Zahkarov_mo

benchmark_func = {
    'Ackley': {'co': Ackley_co, 'cv': Ackley_cv, 'mo': Ackley_mo},
    'Beale' : {'co': Beale_co,  'cv': Beale_cv , 'mo': Beale_mo},
    'Booth' : {'co': Booth_co,  'cv': Booth_cv , 'mo': Booth_mo},
    'Sphere': {'co': Sphere_co, 'cv': Sphere_cv, 'mo': Sphere_mo},
}

benchmark_func = {
    'Ackley'      : {'co': Ackley_co,       'cv': Ackley_cv      , 'mo': Ackley_mo},
    'Beale'       : {'co': Beale_co,        'cv': Beale_cv       , 'mo': Beale_mo},
    'Booth'       : {'co': Booth_co,        'cv': Booth_cv       , 'mo': Booth_mo},
    'Bukin'       : {'co': Bukin_co,        'cv': Bukin_cv       , 'mo': Bukin_mo},
    'Camel'       : {'co': Camel_co,        'cv': Camel_cv       , 'mo': Camel_mo},
    'DeJongF3'    : {'co': DeJongF3_co,     'cv': DeJongF3_cv    , 'mo': DeJongF3_mo},
    'Easom'       : {'co': Easom_co,        'cv': Easom_cv       , 'mo': Easom_mo},
    'Eggholder'   : {'co': Eggholder_co,    'cv': Eggholder_cv   , 'mo': Eggholder_mo},
    # 'FiveWell'    : {'co': FiveWell_co,     'cv': FiveWell_cv    , 'mo': FiveWell_mo},
    'Ktable'      : {'co': Ktable_co,       'cv': Ktable_cv      , 'mo': Ktable_mo},
    'Levi'        : {'co': Levi_co,         'cv': Levi_cv        , 'mo': Levi_mo},
    'Matyas'      : {'co': Matyas_co,       'cv': Matyas_cv      , 'mo': Matyas_mo},
    'McCormick'   : {'co': McCormick_co,    'cv': McCormick_cv   , 'mo': McCormick_mo},
    'Goldstain'   : {'co': Goldstain_co,    'cv': Goldstain_cv   , 'mo': Goldstain_mo},
    'Griewank'    : {'co': Griewank_co,     'cv': Griewank_cv    , 'mo': Griewank_mo},
    'Rosenbrock'  : {'co': Rosenbrock_co,   'cv': Rosenbrock_cv  , 'mo': Rosenbrock_mo},
    'Schaffer2'   : {'co': Schaffer2_co,    'cv': Schaffer2_cv   , 'mo': Schaffer2_mo},
    'Schaffer4'   : {'co': Schaffer4_co,    'cv': Schaffer4_cv   , 'mo': Schaffer4_mo},
    'Schwefel'    : {'co': Schwefel_co,     'cv': Schwefel_cv    , 'mo': Schwefel_mo},
    'Michalewicz' : {'co': Michalewicz_co,  'cv': Michalewicz_cv , 'mo': Michalewicz_mo},
    'Rastrigin'   : {'co': Rastrigin_co,    'cv': Rastrigin_cv   , 'mo': Rastrigin_mo},
    'Sphere'      : {'co': Sphere_co,       'cv': Sphere_cv      , 'mo': Sphere_mo},
    'SumDiffPower': {'co': SumDiffPower_co, 'cv': SumDiffPower_cv, 'mo': SumDiffPower_mo},
    'WeitedSphere': {'co': WeitedSphere_co, 'cv': WeitedSphere_cv, 'mo': WeitedSphere_mo},
    'XinShe'      : {'co': XinShe_co,       'cv': XinShe_cv      , 'mo': XinShe_mo},
    'Shuberts'    : {'co': Shuberts_co,     'cv': Shuberts_cv    , 'mo': Shuberts_mo},
    'SixHump'     : {'co': SixHump_co,      'cv': SixHump_cv     , 'mo': SixHump_mo},
    'Zahkarov'    : {'co': Zahkarov_co,     'cv': Zahkarov_cv    , 'mo': Zahkarov_mo},
}
