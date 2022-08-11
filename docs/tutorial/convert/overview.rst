Conversion Graph
----------------

.. mermaid::

  graph LR

  flopt([flopt.Problem])
  style flopt fill:#fff,stroke:#000,stroke-width:1px

  QpStructure[QpStructure]
  LpStructure[LpStructure]
  IsingStructure[IsingStructure]
  QuboStructure[QuboStructure]

  flopt --> QpStructure
  QpStructure --> flopt

  flopt --> IsingStructure
  IsingStructure --> flopt

  QpStructure --> LpStructure
  LpStructure --> QpStructure

  IsingStructure --> QuboStructure
  QuboStructure --> flopt


This is the `Conversion Graph` of flopt.
Vertexes represent optimization problem structures, and tail problem of a edge can be convertable to head one.
There exists paths connected any vertex pairs, so these optimization problem structures are convertabled to each other.

For example, when we convert Lp to Qubo, flopt executes LpStructure.toQubo(), and the conversion chain is as follows, internally.

.. mermaid::

  graph LR

  flopt([flopt.Problem])
  style flopt fill:#fff,stroke:#000,stroke-width:1px

  QpStructure[QpStructure]
  LpStructure[LpStructure]
  IsingStructure[IsingStructure]
  QuboStructure[QuboStructure]

  LpStructure --> QpStructure --> flopt --> IsingStructure --> QuboStructure


Some solvers input a structure, and the Conversion Graph includes solvers and modelers is as follows.

.. mermaid::

  graph LR

  flopt([flopt.Problem])
  style flopt fill:#fff,stroke:#000,stroke-width:1px
  CVXOPT(CVXOPT)
  style CVXOPT fill:#fff,stroke:#000,stroke-width:1px
  Scipy.optimize.linprog(Scipy.optimize.linprog)
  style Scipy.optimize.linprog fill:#fff,stroke:#000,stroke-width:1px
  Scipy.optimize.milp(Scipy.optimize.milp)
  style Scipy.optimize.milp fill:#fff,stroke:#000,stroke-width:1px
  Scipy.optimize.minimize(Scipy.optimize.minize)
  style Scipy.optimize.minimize fill:#fff,stroke:#000,stroke-width:1px
  PuLP([PuLP])
  style PuLP fill:#fff,stroke:#000,stroke-width:1px
  Hyperopt(Hyperopt)
  style Hyperopt fill:#fff,stroke:#000,stroke-width:1px
  Optuna(Optuna)
  style Optuna fill:#fff,stroke:#000,stroke-width:1px
  Amplify(Amplify)
  style Amplify fill:#fff,stroke:#000,stroke-width:1px
  SolversInFlopt(Solvers in flopt)
  style SolversInFlopt fill:#fff,stroke:#000,stroke-width:1px

  QpStructure[QpStructure]
  LpStructure[LpStructure]
  IsingStructure[IsingStructure]
  QuboStructure[QuboStructure]

  flopt --> QpStructure
  QpStructure --> flopt

  flopt --> IsingStructure
  IsingStructure --> flopt

  QpStructure --> LpStructure
  LpStructure --> QpStructure

  IsingStructure --> Amplify
  IsingStructure --> QuboStructure
  QuboStructure --> flopt

  QpStructure --> CVXOPT
  LpStructure --> Scipy.optimize.linprog
  LpStructure --> Scipy.optimize.milp


  flopt --> PuLP
  PuLP --> flopt
  flopt --> Hyperopt
  flopt --> Optuna
  flopt --> Scipy.optimize.minimize
  flopt --> SolversInFlopt


