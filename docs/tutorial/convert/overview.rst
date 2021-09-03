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
Vertex represents a optimization problem structure, and tail of a edge can be convertable to head.
There exists paths connected any vertex pairs, so these optimization problem structures are convertabled to each other.

For example, we want to convert Lp to Qubo, execute LpStructure.toQubo(), and the conversion chain is as follows, internally.

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


  flopt --> PuLP
  PuLP --> flopt
  flopt --> Hyperopt
  flopt --> Optuna
  flopt --> Scipy.optimize.minimize


