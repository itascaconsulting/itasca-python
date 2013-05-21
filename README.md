Python connectivity for Itasca software.

This library implements a connection via sockets between Python and
the numerical modeling software from Itasca Consulting
Group.

www.itascacg.com/software

FLAC, FLAC3D, PFC2D, PFC3D, UDEC & 3DEC

## Installation

A pure-python module, easy installation.

```python
$ python setup.py install
```

## Demo high-level interface to PFC

```python
>>> from itasca import pfcBridge
>>> pfc = pfcBridge()  # launches a new PFC instance
```

Evaluate fish expressions:

```python
>>> res = pfc.eval("1+1")
>>> assert res == 2

>>> res = pfc.eval("cos(1+2.2)")
>>> assert res == math.cos(1+2.2)

>>> res = pfc.eval("a=123.456")
>>> assert res == 0

>>> res = pfc.eval("a")
>>> assert res == 123.456
```

Execute PFC commands:

```python
>>> pfc.cmd("ball id 1 rad 1 x 12.30 y .2 z 0")
>>> pfc.cmd("ball id 2 rad 1 x 12.30 y .4 z 3")
>>> pfc.cmd("ball id 3 rad 1 x 12.30 y .5 z 6")
>>> pfc.cmd("prop dens 2500 kn 1.0e3 ks 1.0e3")
>>> pfc.cmd("set grav 0 0 -9.81")
>>> pfc.cmd("measure id 1 x 0.122 y 0.4 z -0.3 rad 0.0225")
>>> pfc.cmd("wall face 0 0 0  1 1 1  2 0 0 fric 0.25")
```

Use a *Pythonic* interface to PFC model objects:

```python
>>> for ball in pfc.ball_list():
>>>     print ball.x(), ball.y(), ball.z()
12.3 0.5 6.0
12.3 0.4 3.0
12.3 0.2 0.0

>>> pfc.time()
0.0

>>> pfc.ball_head()
<pfc ball id=3>

>>> pfc.ball_near3(0,0,0)
<pfc ball id=1>
```

Get and set PFC model properties pragmatically

```python
>>> b = pfc.ball_head()
>>> b.rad(99.9)
>>> assert b.rad() == 99.9
>>> b = b.next()
>>> print b.rad()
1.0

>>> w = pfc.wall_head()
>>> print w
<pfc wall id=1>
>>> print w.fric()
0.25
>>> w.fric(0.112)
>>> assert w.fric() == 0.112

>>> meas = pfc.circ_head()
>>> print meas
<pfc measurement sphere id=1>
>>> print meas.x()
0.122
>>> meas.x(12.55)
>>> assert meas.x() == 12.55
```

NumPy array interface

```python
>>> pfc.ball_positions()
array([[ 12.3   0.5   6. ]
       [ 12.3   0.4   3. ]
       [ 12.3   0.2   0. ]])
>>> pfc.cmd("cycle 100")
>>> pfc.ball_velocities()
array([[ 0.      ,  0.      , -2.190092],
       [ 0.      ,  0.      , -2.190092],
       [ 0.      ,  0.      , -2.190092]])
```

Close connection:
```python
>>> pfc.quit()  # quits PFC
```
or
```python
>>> pfc.close()  # to return control to PFC
```
## Low level socket interface to all Itasca codes

Send and receive FISH data to Itasca codes

```python
from itasca import FLAC3D_Connection

flac3d = FLAC3D_Connection()
flac3d.start("flac_socket_test.f3dat")
flac3d.connect()

flac3d.send(99.9)
flac3d.send([1,2])
flac3d.send([1,2,3])
flac3d.send("James")

for i in range(10):
    print "sending", i, "...",
    flac3d.send(i)
    print "sent", i
    value = flac3d.receive()
    print "got", value, "from FLAC3D"

flac3d.send(-1)
flac3d.end()
```

On the Itasca code side a simple server loop reads these values and
performs some action.

## Fish binary format reader

Generate some fish binary data

```python
def genIOtestdata
  array a(1)
  fp = open('testdata.fish', 1, 0)
  a(1) = 1
  oo = write(a, 1)
  a(1) = 99.987
  oo = write(a, 1)
  a(1) = 'James'
  oo = write(a, 1)
  a(1) = vector(99.5, 89.3)
  oo = write(a, 1)
  a(1) = vector(7,8,9)
  oo = write(a, 1)
  oo = close
end
@genIOtestdata
```

Read it in Python

```python
>>> from itasca import FishBinaryReader

>>> fish_file = FishBinaryReader("testdata.fish")

>>> assert fish_file.read() == 1
>>> assert fish_file.read() == 99.987
>>> assert fish_file.read() == "James"
>>> assert fish_file.read() == [99.5, 89.3]
>>> assert fish_file.read() == [7.0, 8.0, 9.0]

>>> FishBinaryReader("testdata2.fish").aslist()  # convert data to list
[1, 2, 3, 4, 5, 6, 7]
>>> FishBinaryReader("testdata2.fish").asarray() # conver to NumPy array
array([[1, 2, 3, 4, 5, 6, 7])
```
