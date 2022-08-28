Solver Selector
---------------

AutoSearch
^^^^^^^^^^

.. autoclass:: flopt.solvers.auto_search.AutoSearch


How solver is selected?
^^^^^^^^^^^^^^^^^^^^^^^

We give the priority of the solver in advance according to the problem and the setting of the solution.
The solver with the highest priority is selected from among the solvers that can solve the given problem.

The priorities are calculated using two problem sets.
One is `tsp` and the other is `func`.

tsp
+++

For example, here are the results for tsp.
The instance of tsp is solved by solvers, and we calculate ranking by the result, the objective values solvers found.

From this result, for the permutation problem, the 2-Opt is set to have a higher priority than the RandomSearch.

::

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
++++

The results of `func` problem set are here.
We can see that RandomSearch gives better results when timelimit is short,
and OptunaCmaEsSearch gives better results when timelimit is somewhat long.
Based on the following ranking, we have created several solver priorities according to timelimit.


- timelimit = 5 sec

::

  func
  ====

      Instance HyperoptTPESearch OptunaCmaEsSearch OptunaTPESearch RandomSearch      SFLA ScipySearch
      -------- ----------------- ----------------- --------------- ------------      ---- -----------
        Ackley             7.771             5.012           8.703        8.370     6.995      14.662
         Beale             0.002           0.00005           0.011      0.00099     0.036     0.00000
         Booth             0.098           0.00018           0.263      0.00067     0.002     0.00000
         Bukin             5.757             4.606           3.038        0.303     0.606       0.016
         Camel           0.00071           0.00008           0.018      0.00071   0.00007       0.299
      DeJongF3           -24.000           -26.000         -23.000      -28.000   -15.000     0.00000
         Easom          -0.00006          -0.00000        -0.00000       -0.830  -0.00002     0.00000
     Eggholder          -951.265          -557.358        -714.215     -954.925  -909.498    -507.874
     Goldstain             3.278             3.003           3.006        3.094    13.186      84.000
      Griewank            37.103            27.157          35.639       29.185    21.136       0.037
        Ktable          2.54e+04          5.14e+04        3.32e+04     4.03e+04  6767.418     0.00000
          Levi             0.309             0.004           0.263        0.004     0.025       0.110
        Matyas           0.00092           0.00000           0.001      0.00005   0.00000     0.00000
     McCormick            -1.911             1.228          -1.913       -1.913    -1.913      -1.913
   Michalewicz           0.00000           0.00000         0.00000      0.00000   0.00000     0.00000
     Rastrigin            74.833            52.534          79.075       60.601    86.871     113.424
    Rosenbrock          4879.164          2154.848        2016.471     2966.670  2038.877     0.00000
     Schaffer2             0.017             0.009           0.052        0.002   0.00000       0.495
     Schaffer4             0.297             0.325           0.298        0.293     0.306       0.492
      Schwefel         -1814.323         -1429.060       -1714.227    -2570.812 -1560.051   -2628.825
      Shuberts          -179.314          -111.088        -155.830     -185.864  -143.037      -1.638
       SixHump            -1.026            -1.032          -1.026       -1.031    -1.004      -1.032
        Sphere          2.25e+19          1.88e+19        8.69e+19     3.69e+19  3.23e+18     0.00000
  SumDiffPower             0.013             0.010           0.057        0.002   0.00013     0.00000
  WeitedSphere            45.161            26.563          24.471       60.341    25.514     0.00000
        XinShe             0.018             0.036           0.059        0.003     0.006       0.003
      Zahkarov          8.74e+34          7.89e+29        5.32e+30     1.96e+25  3.32e+32    7.04e+08

          #Win                 1                 4               1            7         3          16
         Score                80                64              86           47        60          53
       Ranking                 5                 4               6            1         3           2



- timelimit = 30 sec

::

  func
  ====

      Instance HyperoptTPESearch OptunaCmaEsSearch OptunaTPESearch RandomSearch      SFLA ScipySearch
      -------- ----------------- ----------------- --------------- ------------      ---- -----------
        Ackley            10.528             1.878          10.416        9.726    10.692      12.260
         Beale             0.115           0.00000           0.002        0.001     0.475     0.00000
         Booth             0.682           0.00000           0.005        0.008     0.024     0.00000
         Bukin             9.246             0.037           2.705        0.153     9.778       0.010
         Camel             0.047           0.00000           0.004        0.001     0.016     0.00000
      DeJongF3           -23.000           -27.000         -25.000      -26.000   -12.000     0.00000
         Easom          -0.00004            -1.000        -0.00002       -0.972  -0.00000     0.00000
     Eggholder          -823.579          -894.579        -857.638     -950.833  -882.299    -419.312
     Goldstain             4.482             3.000           3.064        3.042    34.754      30.000
      Griewank            82.954             1.048          69.474       61.636    52.647       0.042
        Ktable          1.40e+05            53.249        7.94e+04     4.58e+04  7.79e+04     0.00000
          Levi             0.291           0.00000           0.141        0.030     0.419     121.414
        Matyas             0.033           0.00000         0.00018      0.00056     0.094     0.00000
     McCormick            -1.908            -1.913          -1.910       -1.913    -1.445       1.228
   Michalewicz           0.00000           0.00000         0.00000      0.00000   0.00000     0.00000
     Rastrigin            89.493            38.397         113.159       58.034   112.703      62.682
    Rosenbrock          1.41e+04            10.445        5315.919     3563.709  6686.343     0.00000
     Schaffer2             0.020             0.484           0.011        0.003     0.009       0.491
     Schaffer4             0.322             0.389           0.321        0.298     0.340       0.469
      Schwefel         -1173.049         -2832.437       -1366.689    -2209.379 -1618.957   -1917.588
      Shuberts          -137.556          -181.835         -99.754     -186.075  -122.979       0.685
       SixHump            -1.030            -1.032          -1.031       -1.030    -0.905      -1.032
        Sphere          6.58e+19          8.69e+16        3.65e+19     3.85e+19  9.75e+19     0.00000
  SumDiffPower             0.025           0.00002           0.167        0.008     0.001     0.00000
  WeitedSphere            87.741             0.097          60.882       54.900    93.916     0.00000
        XinShe             0.119             0.002           0.210        0.006     0.083       0.003
      Zahkarov          9.35e+32          4.93e+27        1.95e+37     1.54e+25  6.57e+36   -7.82e+09

          #Win                 1                15               1            5         1          14
         Score                96                19              78           41        97          54
       Ranking                 5                 1               4            2         6           3



- timelimit = 60 sec

::

  func
  ====

      Instance HyperoptTPESearch OptunaCmaEsSearch OptunaTPESearch RandomSearch      SFLA ScipySearch
      -------- ----------------- ----------------- --------------- ------------      ---- -----------
        Ackley             3.836             1.049           4.531        7.668     3.454      14.662
         Beale           0.00022           0.00000         0.00058      0.00004     0.003     0.00000
         Booth             0.002           0.00000           0.001      0.00025   0.00000     0.00000
         Bukin             1.177             0.019           1.375        0.096     0.011       0.016
         Camel           0.00044           0.00000         0.00000      0.00001   0.00000       0.299
      DeJongF3           -28.000           -29.000         -27.000      -28.000   -22.000     0.00000
         Easom            -0.907            -1.000          -0.822       -1.000    -1.000     0.00000
     Eggholder          -959.275          -717.769        -932.006     -958.880  -904.842    -507.874
     Goldstain             3.010             3.000           3.014        3.001     3.133      84.000
      Griewank             4.189             0.815           4.257       18.873     3.325       0.037
        Ktable          7603.246           707.098        7451.325     8181.155  3554.440     0.00000
          Levi             0.040           0.00000           0.020      0.00002   0.00000       0.110
        Matyas           0.00012           0.00000         0.00001      0.00001   0.00000     0.00000
     McCormick            -1.913            -1.913          -1.913       -1.913    -1.913      -1.913
   Michalewicz           0.00000           0.00000         0.00000      0.00000   0.00000     0.00000
     Rastrigin            54.011            53.346          61.186       56.277    55.403     113.424
    Rosenbrock           126.648             6.902         176.332      480.027    91.941     0.00000
     Schaffer2           0.00081             0.055         0.00000      0.00003   0.00000       0.495
     Schaffer4             0.297             0.297           0.293        0.293     0.293       0.492
      Schwefel         -2335.034         -2034.257       -3621.028    -2656.434 -2382.220   -2628.825
      Shuberts          -178.330          -182.252        -178.522     -186.727  -186.699      -1.638
       SixHump            -1.031            -1.032          -1.031       -1.032    -1.032      -1.032
        Sphere          9.27e+18          6.36e+13        9.49e+18     1.10e+19  3.23e+18     0.00000
  SumDiffPower           0.00061           0.00000         0.00003        0.001   0.00033     0.00000
  WeitedSphere            12.439           0.00046           8.212       24.347     8.748     0.00000
        XinShe             0.011             0.007           0.006        0.003     0.004       0.003
      Zahkarov          5.35e+30          5.20e+28        5.98e+28     1.61e+18  2.67e+09    7.04e+08

          #Win                 2                14               2            3         9          13
         Score                86                33              81           71        46          59
       Ranking                 6                 1               5            4         2           3



.. code-block:: shell

  python compute_performance.py RandomSearch      RandomSearch      --datasets func --params ./settings/default.param --log_level 10
  python compute_performance.py OptunaTPESearch   OptunaTPESearch   --datasets func --params ./settings/default.param --log_level 10
  python compute_performance.py HyperoptTPESearch HyperoptTPESearch --datasets func --params ./settings/default.param --log_level 10
  python compute_performance.py OptunaCmaEsSearch OptunaCmaEsSearch --datasets func --params ./settings/default.param --log_level 10
  python compute_performance.py SFLA              SFLA              --datasets func --params ./settings/default.param --log_level 10
  python compute_performance.py ScipySearch       ScipySearch       --datasets func --params ./settings/default.param --log_level 10
  python view_performance.py --dataset func


