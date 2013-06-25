# This is a demonstration of a high level interface to PFC3D 4.0.

# to run this example:

# (i) make sure the file pfc_bridge_server.p3dat is in the same folder
# as this file.

# (ii) Run this file with Python: python pfc_bridge_test.py

# (iii) PFC3D will be started, click the green arrow to run the
# pfc_bridge_server.p3dat file. This puts PFC into server mode where
# it will respond to input from Python.

from itasca import pfcBridge
import math

pfc = pfcBridge()

res = pfc.eval("1+1")
assert res == 2

res = pfc.eval("cos(1+2.2)")
assert res == math.cos(1+2.2)

res = pfc.eval("a=123.456")
assert res == 0

res = pfc.eval("a")
assert res == 123.456

pfc.cmd("ball id 1 rad 1 x 12.30 y .2 z 0")
pfc.cmd("ball id 2 rad 1 x 12.30 y .4 z 3")
pfc.cmd("ball id 3 rad 1 x 12.30 y .5 z 6")
pfc.cmd("prop dens 2500 kn 1.0e3 ks 1.0e3")
pfc.cmd("set grav 0 0 -9.81")
pfc.cmd("measure id 1 x 0.122 y 0.4 z -0.3 rad 0.0225")
pfc.cmd("wall face 0 0 0  1 1 1  2 0 0 fric 0.25")

for ball in pfc.ball_list():
    print ball.x(), ball.y(), ball.z()

print pfc.time()
print pfc.ball_head()
print pfc.ball_near3(0,0,0)

b = pfc.ball_head()
b.rad(99.9)
assert b.rad() == 99.9
b = b.next()
print b.rad()

w = pfc.wall_head()
print w, w.fric()
w.fric(0.112)
assert w.fric() == 0.112

meas = pfc.circ_head()
print meas, meas.x()
meas.x(12.55)
assert meas.x() == 12.55

# ball iterator
for ball in pfc.ball_list():
    print ball.x(), ball.y(), ball.z()
    ball.rad(0.123)

# array interface
print pfc.ball_positions()
print pfc.ball_velocities()


#pfc.quit()
