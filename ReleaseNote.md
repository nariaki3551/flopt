# flopt


### version 0.5.5 (Oct, 2022)

#### Update

1. Improve the performance of AutoSearch
    - train the selection model, and provode in https://github.com/nariaki3551/flopt_trained_model/releases
    - simplify the estimation of the problem type and checking which solver can handle user defined problem

2. If-then constraints
    - add if-then (A => B) constraint api; B must be satisfied when only A is satisfied
    - ```python
      import flopt
      a = flopt.Value("a", lowBound=1, upBound=4)
      b = flopt.Value("b", lowBound=2, upBound=5)
      prob = flopt.Problem()
      # (a+3*b) >= 0 must be satisfied when only (a+b) <= 4 is satisfied
      prob += (a + b <= 4) >> (a + 3 * b >= 0)
      ```
2. Improve the other solver
    - refactor the SFLA search code to speed up and register solutions early
    - add hard time limit to the optuna based solvers

3. Add case studies
    - maximum-cut

4. Add apis
    - add .max() and .min() in ExpressionElement class
        - ```python
          import flopt
          a = flopt.Value("a", lowBound=1, upBound=4)
          b = flopt.Value("b", lowBound=2, upBound=5)
          (a + b).max()
          >>> 9
          (a + b).min()
          >>> 3
          ```

5. Fix some bugs
    - fix (critical) memory leak about Const object
    - fix error of Cvxopt, `ValueError: Rank(A) < p or Rank([P; A; G]) < n`
    - fix bug for flopt.convert.linearize

6. Others
    - Variable.array name becomes 0-filled. Variable names are sorted more cleanly.
    - Add add operation into Log
        - ```python
          status1, log1 = prob.solve(solver)
          status2, log2 = prob.solve(solver)
          log = log1 + log2
          log.plot()
          ```

#### API Change

1. Setting default solver to AutoSolver
  - ```python
    prob.solve(timelimit=0.1)  # AutoSolver used in this solve
    ```


### version 0.5.4 (Sep, 2022)

#### Update

1. Improvement the overall performance of flopt
    - add performance measurement script
    - deley to set the polynominal in expression
    - 2.5x faster import flopt
    - 2.5x faster create expression
    - 2.0x faster calculate the value of functions
    - 1.25x faster build QpStructure
    - 1.25x faster sum, prod operation

2. Add new api
    - flopt.Problem.removeDuplicatedConstraints()
        - remove the duplicated constraints in problem
    - flopt.get_dot_graph(expression)
        - visualize the calculation graph
    - flopt.constants
        - flopt.VarCOntinuous, flopt.VarInteger, flopt.VarBinary, flopt.VarSpin, flopt.VerPermutation
        - flopt.Minimize, flopt.Maximize

3. Simplifize implementations of solvers
    - flopt.solvers.base.registerSolution(solution)
        - check and update incumbent solution

4. Manage dummy variable names to avoid duplication name
    - flopt.env create_variable_mode, is_create_variable_mode, get_variable_id


### version 0.5.3 (Aug, 2022)

**Update**

1. Speed up to build LpStructure and QpStructure

2. Fix bugs for CustomExpression


### version 0.5.2 (Aug, 2022)

**Update**

1. Add New Solvers
    - ScipyMilpSearch
        - Mixed-Interger programming problem solver
        - Engine is HIGHS solver

2. Add mipLib to measure the performance of LP, MIP solvers

3. Fixed some bugs


### version 0.5 (Oct, 2021)

**Update**

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



### version 0.4 (Aug, 2021)

**Update**

1. Add convert functions between `flopt.Problem` and `Lp`, `Ising`, `Qubo`, `Pulp`
2. Change the structure of `flopt.Expression` so that it is simple when it is generated
3. Multiple top solutions can now be retrieved
4. Add new solver `ScipyLpSearch ` for LP.
5. Improve the performance of the `SFLA` solver by improving the operation functions of `flopt.Solution`
6. Add simplify and expand functions for `flopt.Expression`
7. Fix some bugs



### version 0.3 (Jul, 2021)

#### Update

1. available() and allAvailableSolvers() can be useable
   1. `solver.available(prob)`
   2. `allAvailableSolvers(prob)`
2. Add new solvers
   1. `AutoSearch`
      1. Select appropriate solvers for the problem and setting
3. Add `isLinear` `isIsing` `toIsing` `maxDegree` function in Problem
4. `import flopt` is about 4 times faster
5. Fix some bugs about `view_performance.py`



### version 0.2 (May, 2020)

#### Update

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


#### API Change

1. CustomObject → CustomExpression



### version0.1 (Apr, 2020)

1. Available Solvers are RandomSearch, 2-Opt, OptunaTPESearch, OptunaCmaEsSearch, HyperoptTPESearch

