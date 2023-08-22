from .Ackley import Ackley
from .Beale import Beale
from .Booth import Booth
from .Bukin import Bukin
from .Camel import Camel
from .DeJongF3 import DeJongF3
from .Easom import Easom
from .Eggholder import Eggholder
from .Ellipsoid import Ellipsoid
from .FiveWell import FiveWell
from .Goldstain import Goldstain
from .Griewank import Griewank
from .Ktable import Ktable
from .Levi import Levi
from .Matyas import Matyas
from .McCormick import McCormick
from .Rosenbrock import Rosenbrock
from .Schaffer2 import Schaffer2
from .Schaffer4 import Schaffer4
from .Schwefel import Schwefel
from .Michalewicz import Michalewicz
from .Rastrigin import Rastrigin
from .Sphere import Sphere
from .SumDiffPower import SumDiffPower
from .Shuberts import Shuberts
from .SixHump import SixHump
from .WeightedSphere import WeightedSphere
from .XinShe import XinShe
from .Zahkarov import Zahkarov


benchmark_func = {
    "Ackley": Ackley,
    "Beale": Beale,
    "Booth": Booth,
    "Bukin": Bukin,
    "Camel": Camel,
    "DeJongF3": DeJongF3,
    "Easom": Easom,
    "Eggholder": Eggholder,
    "Ellipsoid": Ellipsoid,
    # 'FiveWell'    : FiveWell,
    "Goldstain": Goldstain,
    "Griewank": Griewank,
    "Ktable": Ktable,
    "Levi": Levi,
    "Matyas": Matyas,
    "McCormick": McCormick,
    "Michalewicz": Michalewicz,
    "Rastrigin": Rastrigin,
    "Rosenbrock": Rosenbrock,
    "Schaffer2": Schaffer2,
    "Schaffer4": Schaffer4,
    "Schwefel": Schwefel,
    "Sphere": Sphere,
    "SumDiffPower": SumDiffPower,
    "Shuberts": Shuberts,
    "SixHump": SixHump,
    "WeightedSphere": WeightedSphere,
    "XinShe": XinShe,
    "Zahkarov": Zahkarov,
}
