from itasca import pfcBridge

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


for ball in pfc.ball_list():
    print ball.x(), ball.y(), ball.z()

pfc.close()
