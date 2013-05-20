from itasca import PFC3D_Connection
from itasca import FishBinaryReader
import math
import numpy as np

class pfcBridge(object):
    def __init__(self):
        self._pfc = PFC3D_Connection()
        self._pfc.start("bridge-server.p3dat")
        self._pfc.connect()

    def eval(self, fish_string):
        """Evaluate a FISH expression and return the result

        The expression can either be an assignment or an
        expression. Assignments return zero expressions return the
        value they evaluate to.
        """
        assert type(fish_string) == str

        if fish_string.find("=") == -1:
            code = 11
        else:
            code = 12

        self._pfc.send(code)
        self._pfc.send(fish_string)
        res = self._pfc.receive()
        return res

    def cmd(self, command):
        "execute a PFC3D command"
        assert type(command) == str
        self._pfc.send(10)
        self._pfc.send(command)
        res = self._pfc.receive()
        assert res == 0

    def ball_radii(self):
        """ returns a NumPy array of the ball locations """
        self.cmd("write_ball_radii")
        return self.read_v1_fish()

    def ball_positions(self):
        """ returns a NumPy array of the ball locations """
        self.cmd("write_ball_positions")
        return self.read_v3_fish()

    def ball_velocities(self):
        """ returns a NumPy array of the ball locations """
        self.cmd("write_ball_velocities")
        return self.read_v3_fish()

    def read_v3_fish(self, filename='bin.fish'):
        fish_file = FishBinaryReader(filename)
        tmp = []
        try:
            while True:
                x,y,z = fish_file.read(), fish_file.read(), fish_file.read()
                assert type(x)==float
                assert type(y)==float
                assert type(z)==float
                tmp.append([x,y,z])
        except:
            pass
        a = np.array(tmp)
        return a.reshape(a.shape[0], 3)

    def read_v1_fish(self, filename='bin.fish'):
        fish_file = FishBinaryReader(filename)
        tmp = []
        try:
            while True:
                x = fish_file.read()
                assert type(x)==float
                tmp.append(x)
        except:
            pass
        return np.array(tmp)

    def ball_list(self):
        return ball_list(self)

    def close(self):
        self._pfc.send(-1)

    def quit(self):
        self._pfc.send(-2)


class ball_list(object):
    "iterator object for list of balls"
    def __init__(self, bridge):
        self._bridge = bridge
        self.current = pfc_ball(self._bridge.eval("ball_id_head"),
                                self._bridge)
    def __iter__(self):
        return self
    def next(self):
        if self.current.id==-1:
            raise StopIteration
        else:
            retval = self.current
            self._bridge.eval("current_id = %i" % self.current.id)
            self.current = pfc_ball(self._bridge.eval("ball_id_next"),
                                    self._bridge)
            return retval

class pfc_contact(object):
    def __init__(self, idn, bridge):
        self.id = idn

    def __repr__(self):
        return "<pfc contact id=%i>" % (self.id)


class pfc_ball(object):
    methods = """b_clist b_ctype b_xfix b_yfix b_zfix b_vfix
b_rxfix b_ryfix b_rzfix b_rfix b_x b_y b_z b_vpos b_ux b_uy b_uz b_vu
b_xvel b_yvel b_zvel b_vvel b_rxvel b_ryvel b_rzvel b_rvel b_xfob
b_yfob b_zfob b_vfob b_xfap b_yfap b_zfap b_vfap b_xmom b_ymom b_zmom
b_mom b_rad b_mass b_realmass b_moi b_dens b_kn b_ks b_shearmod
b_poiss b_fric b_ex del_ball b_color b_xmap b_ymap b_zmap b_map
b_shared b_type b_rot b_damp b_realmoi b_clump b_cllist b_extra
b_stress b_vrvel b_vmom b_vmap b_vrfix b_xdisp b_ydisp b_zdisp b_vdisp
b_delete b_thexp b_thfix b_thpob b_thpsrc b_thsheat b_thtemp
b_thdeltemp b_perflag b_perBall b_xffap b_yffap b_zffap b_vffap
b_multi_type b_realmassset b_realmoiset""".split()

    def __init__(self, idn, bridge):
        self.id = idn
        self._bridge = bridge

    def __repr__(self):
        return "<pfc ball id=%i>" % (self.id)

    def __getattr__(self, item):
        fname = "b_" + item
        if not fname in pfc_ball.methods:
            raise AttributeError("no pfc_ball fish intrinsic " + fname)

        # shoud check for rw here?
        def handle_fishcall(arg=None):
            if arg==None:
                fish_string = "%s(find_ball(%i))" % (fname, self.id)
                res = self._bridge.eval(fish_string)
                return res
            else:
                fish_string = "%s(find_ball(%i))=%s" % (fname,
                                                        self.id,
                                                        str(arg))
                res = self._bridge.eval(fish_string)
                return arg

        return handle_fishcall


if __name__=='__main__':
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
        ball.rad(0.123)

    print pfc.ball_positions()
    print pfc.ball_velocities()
    print pfc.ball_radii()

    #pfc.quit()
