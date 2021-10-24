# flopt

1. Add New Solvers
    - CvxoptQpSearch
      - It can solve the Quadratic Problem
    - AmplifySearch
        - It can solve the Ising model with constraints

2. Add some formulation structure
    - We can convert between any formulation structure pair
    - Faster conversion
        - by developing polynomial class

3. Add linearize function
    - A problem can be linearized as possible as

4. Add utility functions for variable and expression
    - Variable.array, Variable.dict, Variable.matrix
    - Sum, Dot, Prod

5. Add some case studies to document

6. Update some internal classes and performance
    - VarConst + ExpressionConst → Const
    - Manage type of Variable, Expression, and SolverState from str to int of Enum



### version 0.4 (August, 2021)

**Update**

1. Add convert functions between `flopt.Problem` and `Lp`, `Ising`, `Qubo`, `Pulp`
2. Change the structure of `flopt.Expression` so that it is simple when it is generated
3. Multiple top solutions can now be retrieved
4. Add new solver `ScipyLpSearch ` for LP.
5. Improve the performance of the `SFLA` solver by improving the operation functions of `flopt.Solution`
6. Add simplify and expand functions for `flopt.Expression`
7. Fix some bugs



### version 0.3 (3 July, 2021)

**Update**

1. available() and allAvailableSolvers() can be useable
   1. `solver.available(prob)`
   2. `allAvailableSolvers(prob)`
2. Add new solvers
   1. `AutoSearch`
      1. Select appropriate solvers for the problem and setting
3. Add `isLinear` `isIsing` `toIsing` `maxDegree` function in Problem
4. `import flopt` is about 4 times faster
5. Fix some bugs about `view_performance.py`



### version 0.2 (30 May, 2020)

**Update**

1. Constraints can be useable
   1. `prob += a + b <= c + 2`
2. Add new solvers
   1. `PulpSearch`
      1. PulpSearch can solve LP with constraints.
   2. `ScipySearch`
      1. ScipySearch can solve non-linear programming with constraints, and black-box optimization problem with constraints.
3. Update the performance viewing
4. Add a lot of benchmarking functions
5. Add logging function
   1. change log level by `flopt.env.setLevel(10)`.

**API Change**

#### API Change

1. CustomObject → CustomExpression



### version0.1 (30 Apr, 2020)

1. Available Solvers are RandomSearch, 2-Opt, OptunaTPESearch, OptunaCmaEsSearch, HyperoptTPESearch

