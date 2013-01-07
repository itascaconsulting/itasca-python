from itasca import PFC3D_Connection
import math

class pfcBridge(object):
    def __init__(self):
        self._pfc = PFC3D_Connection()
        self._pfc.start("bridge-server.p3dat")
        self._pfc.connect()

    def eval(self, fish_string):
        "Evaluate a FISH expression and return the result"
        assert type(fish_string) == str
        self._pfc.send(11)
        self._pfc.send(fish_string)
        res = self._pfc.receive()
        print res
        return res

    def cmd(self, command):
        "execute a PFC3D command"
        assert type(command) == str
        self._pfc.send(10)
        self._pfc.send(command)
        res = self._pfc.receive()
        assert res == 0


class ball(object):
    def __init__(self, idn):
        self.id = idn



if __name__=='__main__':
    pfc = pfcBridge()

    res = pfc.eval("1+1")
    assert res == 2

    res = pfc.eval("cos(1+2.2)")
    assert res == math.cos(1+2.2)


    my_command = """
ball id 1 rad 1 x 12.30 y .2 z 0
ball id 2 rad 1 x 12.30 y .4 z 3
ball id 3 rad 1 x 12.30 y .5 z 6
prop dens 2500 kn 1.0e3 ks 1.0e3
set grav 0 0 -9.81
"""
    pfc.cmd(my_command)


    pfc._pfc.send(-1)
