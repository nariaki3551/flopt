from math import sqrt
from flopt import Variable, Solution

b = Solution('b', [Variable(f'b{i}', lowBound=0, upBound=10, iniValue=i+1,
                        cat='Continuous') for i in range(5)] )
c = Solution('c', [Variable(f'c{i}', lowBound=0, upBound=10, iniValue=2*i,
                        cat='Continuous') for i in range(5)] )
d = [1, 1, 1, 1, 1]
e = 3*b
f = Solution('f', [Variable(f'c{i}', lowBound=0, upBound=10, iniValue=2*i,
                        cat='Integer') for i in range(5)] )
g = [0.1, 0.2, 0.3, 0.4, 0.5]

def test_Solution_value_1():
    assert b.value() == [1, 2, 3, 4, 5]

def test_Solution_value_2():
    assert c.value() == [0, 2, 4, 6, 8]

def test_Solution_floor():
    assert (b/2).floor().value() == [0, 1, 1, 2, 2]

def test_Solution_ceil():
    assert (b/2).floor().value() == [0, 1, 1, 2, 2]

def test_Solution_clone():
    assert (b.clone()).value() == [1, 2, 3, 4, 5]

def test_Solution_pos():
    assert (+b).value() == [1, 2, 3, 4, 5]

def test_Solution_neg():
    assert (-b).value() == [-1, -2, -3, -4, -5]

def test_Solution_add_s():
    assert (b+c).value() == [1, 4, 7, 10, 13]

def test_Solution_add_c_1():
    assert (b+d).value() == [2, 3, 4, 5, 6]

def test_Solution_add_c_2():
    assert (f+g).value() == list(map(int, [0.1, 2.2, 4.3, 6.4, 8.5]))

def test_Solution_radd_c():
    assert (d+b).value() == [2, 3, 4, 5, 6]

def test_Solution_add_scalar():
    assert (b+1).value() == [2, 3, 4, 5, 6]

def test_Solution_radd_scalar():
    assert (1+b).value() == [2, 3, 4, 5, 6]

def test_Solution_sub_s():
    assert (b-c).value() == [1, 0, -1, -2, -3]

def test_Solution_sub_c():
    assert (b-d).value() == [0, 1, 2, 3, 4]

def test_Solution_rsub_s():
    assert (c-b).value() == [-1, 0, 1, 2, 3]

def test_Solution_rsub_c():
    assert (d-b).value() == [0, -1, -2, -3, -4]

def test_Solution_mul_s():
    assert (b*c).value() == [0, 4, 12, 24, 40]  # [1, 2, 3, 4, 5] * [0, 2, 4 ,6, 8]

def test_Solution_doc():
    assert b.dot(c) == 0 + 4 + 12 + 24 + 40 # [1, 2, 3, 4, 5] dot [0, 2, 4 ,6, 8]

def test_Solution_mul():
    assert (b*2).value() == [2, 4, 6, 8, 10]

def test_Solution_rmul():
    assert (2*b).value() == [2, 4, 6, 8, 10]

def test_Solution_div_c():
    assert (b/d).value() == [1, 2, 3, 4, 5]

def test_Solution_div():
    assert (b/2).value() == [0.5, 1, 1.5, 2, 2.5]

def test_Solution_squaredNorm():
    assert b.squaredNorm() == sum((1+i)*(1+i) for i in range(5))

def test_Solution_norm():
    assert b.norm() == sqrt(sum((1+i)*(1+i) for i in range(5)))

def test_Solution_len():
    assert len(b) == 5

def test_Solution_hash():
    hash(b)

def test_Solution_repr():
    repr(b)

def test_Solution_feasible_1():
    assert b.feasible()

def test_Solution_feasible_2():
    assert not (3*b).feasible()

def test_Solution_clip():
    e.clip()
    assert e.value() == [3, 6, 9, 10, 10]
