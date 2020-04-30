from .Ackley import create_objective as Ackley_co
from .Ackley import create_variables as Ackley_cv
from .Beale  import create_objective as Beale_co
from .Beale  import create_variables as Beale_cv
from .Booth  import create_objective as Booth_co
from .Booth  import create_variables as Booth_cv
from .Sphere import create_objective as Sphere_co
from .Sphere import create_variables as Sphere_cv

benchmark_func = {
    'Ackley': {'co': Ackley_co, 'cv': Ackley_cv},
    'Beale' : {'co': Beale_co,  'cv': Beale_cv},
    'Booth' : {'co': Booth_co,  'cv': Booth_cv},
    'Sphere': {'co': Sphere_co, 'cv': Sphere_cv},
}
