Solver Selector
----------------

AutoSearch
^^^^^^^^^^

.. autoclass:: flopt.solvers.AutoSearch


How solver is selected?
^^^^^^^^^^^^^^^^^^^^^^^

We give the priority of the solver in advance according to the problem and the setting of the solution.
The solver with the highest priority is selected from among the solvers that can solve the given problem.

The priorities are calculated using two problem sets.
One is `tsp` and the other is `func`.

tsp
---

For example, here are the results for tsp.
The instance of tsp is solved by solvers, and we calculate ranking by the result, the objective values solvers found.

From this result, for the permutation problem, the 2-Opt is set to have a higher priority than the RandomSearch.

.. code-block::

  tsp
  ===

   Instance     2-Opt RandomSearch
   --------     ----- ------------
     fl3795  1.67e+05     1.69e+05
      fri26   937.000     1140.000
      gr120  7691.000     4.03e+04
       gr24  1334.000     2188.000
  pa561.tsp  4540.000     4869.000
     pr1002  3.45e+05     3.49e+05
     rl5915  9.95e+06     1.01e+07
      test8  1346.000     1346.000

       #Win         8            0
    Ranking         1            2


This result was created by

.. code-block:: shell

   python compute_performance.py RandomSearch RandomSearch --datasets tsp  --params ./settings/default.param --log_level 10
   python compute_performance.py 2-Opt        2-Opt        --datasets tsp  --params ./settings/default.param --log_level 10
   python view_performance.py --dataset tsp

, and the contants of ./settings/defaualt.param is

.. code-block:: bash

   $ cat ../settings/default.param
   timelimit = 60

func
----

The results of `func` problem set are here.
We can see that RandomSearch gives better results when timelimit is short,
and OptunaCmaEsSearch gives better results when timelimit is somewhat long.
Based on the following ranking, we have created several solver priorities according to timelimit.


- timelimit = 5 sec

.. code-block::

  func
  ====

      Instance HyperoptTPESearch OptunaCmaEsSearch OptunaTPESearch RandomSearch      SFLA
      -------- ----------------- ----------------- --------------- ------------      ----
        Ackley             8.397             7.600          10.388        6.819     9.503
         Beale             0.022             0.001           0.039      0.00031     1.004
         Booth             0.115             0.004           0.027        0.003     0.258
         Bukin             3.051             2.477           6.950        0.412    13.478
         Camel             0.002           0.00002           0.009      0.00017     0.030
      DeJongF3           -24.000           -26.000         -22.000      -26.000   -17.000
         Easom            -0.010          -0.00000        -0.00000       -0.907    -0.460
     Eggholder          -890.387          -554.093        -798.652     -954.786  -885.129
     Goldstain             3.667             4.039           4.974        3.005    39.850
      Griewank            34.226            23.344          67.865       42.317    76.471
        Ktable          5.85e+04          1.86e+04        5.23e+04     1.44e+04  4.87e+04
          Levi             0.196             0.196           0.330        0.002     0.879
        Matyas           0.00002             0.002           0.019      0.00014     0.004
     McCormick            -1.905            -0.061          -1.913       -1.913    -1.895
   Michalewicz           0.00000           0.00000         0.00000      0.00000   0.00000
     Rastrigin            59.047            85.606          79.210       38.206    74.441
    Rosenbrock          2006.619          1279.050        1770.952     1256.650  5395.541
     Schaffer2             0.005           0.00015           0.275      0.00095     0.063
     Schaffer4             0.308             0.317           0.341        0.294     0.325
      Schwefel         -2203.938         -1166.584       -1290.843    -2514.410 -1000.876
      Shuberts          -171.213           -92.053         -58.648     -186.522   -97.734
       SixHump            -1.030            -0.993          -1.023       -1.031    -1.020
        Sphere          5.61e+19          2.85e+19        5.24e+19     3.22e+19  1.10e+20
  SumDiffPower             0.027             0.039           0.266        0.002     0.021
  WeitedSphere            74.027            21.937          34.578       36.692    59.224
        XinShe             0.034             0.050           0.033        0.005     0.036
      Zahkarov          1.18e+31          5.30e+32        5.32e+33     3.66e+22  2.16e+38

          #Win                 2                 6               0           19         0
       Ranking                 2                 3               4            1         5


- timelimit = 30 sec

.. code-block::

  func
  ====

      Instance HyperoptTPESearch OptunaCmaEsSearch OptunaTPESearch RandomSearch      SFLA
      -------- ----------------- ----------------- --------------- ------------      ----
        Ackley             5.432             2.183           6.717        7.207     3.723
         Beale             0.003           0.00000         0.00013      0.00000     0.068
         Booth             0.002           0.00000           0.008      0.00011   0.00000
         Bukin             2.244             0.039           1.094        0.179     0.197
         Camel             0.001           0.00000         0.00012      0.00008   0.00001
      DeJongF3           -27.000           -28.000         -26.000      -28.000   -21.000
         Easom            -0.707          -0.00000        -0.00000       -0.999    -0.921
     Eggholder          -958.299          -565.661        -894.462     -959.478  -785.222
     Goldstain             3.039             3.000           3.031        3.025     5.044
      Griewank             6.155             1.031          13.668       21.086     8.833
        Ktable          1.57e+04          1150.385        1537.118     1.01e+04  9334.235
          Levi             0.112           0.00000           0.033      0.00080     0.017
        Matyas           0.00012           0.00000         0.00001      0.00000   0.00000
     McCormick            -1.913             1.228          -1.913       -1.913    -1.912
   Michalewicz           0.00000           0.00000         0.00000      0.00000   0.00000
     Rastrigin            50.150            66.537          49.009       58.009    60.905
    Rosenbrock           338.643            29.162         195.618     1945.132   874.635
     Schaffer2           0.00007             0.012           0.002      0.00001   0.00003
     Schaffer4             0.294             0.412           0.293        0.293     0.293
      Schwefel         -2039.920         -2067.086       -2605.222    -2836.595 -1360.568
      Shuberts          -182.849          -173.501        -185.952     -186.714  -134.864
       SixHump            -1.030            -1.032          -1.032       -1.032    -1.032
        Sphere          7.25e+18          2.03e+16        1.94e+19     1.33e+19  4.43e+18
  SumDiffPower             0.006           0.00001           0.002        0.003   0.00002
  WeitedSphere            22.005             1.140          22.750       18.817    22.061
        XinShe             0.007             0.010           0.015        0.003     0.006
      Zahkarov          7.23e+30          1.26e+26        6.41e+27     1.51e+21  8.93e+37

          #Win                 1                16               1            9         0
       Ranking                 5                 1               3            2         4

- timelimit = 60 sec

.. code-block::

  func
  ====

      Instance HyperoptTPESearch OptunaCmaEsSearch OptunaTPESearch RandomSearch      SFLA
      -------- ----------------- ----------------- --------------- ------------      ----
        Ackley             5.006             1.214           3.808        5.714     3.135
         Beale           0.00016           0.00000         0.00039      0.00009     0.018
         Booth             0.004           0.00000         0.00079      0.00024   0.00000
         Bukin             2.485             0.014           3.871        0.206     0.032
         Camel           0.00034           0.00000         0.00009      0.00005   0.00000
      DeJongF3           -29.000           -29.000         -28.000      -28.000   -15.000
         Easom            -0.973          -0.00000          -0.929       -0.993    -1.000
     Eggholder          -959.073          -565.998        -894.312     -956.724  -924.998
     Goldstain             3.004             3.000           3.006        3.003     4.113
      Griewank             9.046             0.772          11.902       21.844     5.392
        Ktable          6649.503          3946.091        2751.980     1.02e+04  8004.489
          Levi             0.021             0.110           0.006        0.001   0.00000
        Matyas           0.00027           0.00000         0.00003      0.00001   0.00000
     McCormick            -1.913            -1.913          -1.913       -1.913    -1.913
   Michalewicz           0.00000           0.00000         0.00000      0.00000   0.00000
     Rastrigin            51.091            59.827          57.966       45.241    65.340
    Rosenbrock           123.030             9.670         156.400     1487.982   339.608
     Schaffer2             0.003           0.00000         0.00041      0.00000   0.00000
     Schaffer4             0.294             0.337           0.293        0.293     0.295
      Schwefel         -2475.299         -2146.564       -3095.918    -2805.610 -1329.855
      Shuberts          -182.165          -176.260        -178.960     -186.713  -140.650
       SixHump            -1.031            -1.032          -1.031       -1.032    -1.032
        Sphere          8.76e+18          2.45e+14        4.06e+18     2.24e+19  5.36e+18
  SumDiffPower             0.001           0.00000           0.002      0.00085   0.00032
  WeitedSphere             9.760             0.014          27.898       30.419     5.723
        XinShe             0.006             0.007           0.005        0.003     0.006
      Zahkarov          1.61e+27          2.20e+27        6.44e+30     6.55e+19  1.30e+31

          #Win                 3                15               2            5         2
       Ranking                 4                 1               5            2         3




.. code-block:: shell

  python compute_performance.py RandomSearch      RandomSearch      --datasets func --params ./settings/default.param --log_level 10
  python compute_performance.py OptunaTPESearch   OptunaTPESearch   --datasets func --params ./settings/default.param --log_level 10
  python compute_performance.py HyperoptTPESearch HyperoptTPESearch --datasets func --params ./settings/default.param --log_level 10
  python compute_performance.py OptunaCmaEsSearch OptunaCmaEsSearch --datasets func --params ./settings/default.param --log_level 10
  python compute_performance.py SFLA              SFLA              --datasets func --params ./settings/default.param --log_level 10
  python compute_performance.py ScipySearch       ScipySearch       --datasets func --params ./settings/default.param --log_level 10
  python view_performance.py --dataset func


