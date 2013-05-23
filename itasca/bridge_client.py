from itasca import PFC3D_Connection
from itasca import FishBinaryReader
import numpy as np

class pfcBridge(object):
    def __init__(self):
        self._pfc = PFC3D_Connection()
        self._pfc.start("bridge-server.p3dat")
        self._pfc.connect()

    def __del__(self):
        self.quit()

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
        return self.map_return_type(res)

    def map_return_type(self, val):
        if not type(val)==str: return val
        if not val.startswith(':'): return val
        if val==":null:": return None

        flag, idn = val.split()
        if flag == ':ball:':
            return pfc_ball(int(idn), self)
        elif flag == ':wall:':
            return pfc_wall(int(idn), self)
        elif flag == ':contact:':
            return pfc_contact(self)
        elif flag == ':clump:':
            return pfc_clump(int(idn), self)
        elif flag == ':meas:':
            return pfc_meas(int(idn), self)
        else:
            raise "unknown type in bridge communication"


    def cmd(self, command):
        "execute a PFC3D command"
        assert type(command) == str
        self._pfc.send(10)
        self._pfc.send(command)
        res = self._pfc.receive()
        assert res == 0

    def ball_radii(self):
        """ returns a NumPy array of the ball radii """
        self.cmd("write_ball_radii")
        return self._read_v1_fish()

    def ball_positions(self):
        """ returns a NumPy array of the ball locations """
        self.cmd("write_ball_positions")
        return self._read_v3_fish()

    def ball_velocities(self):
        """ returns a NumPy array of the ball velocities """
        self.cmd("write_ball_velocities")
        return self._read_v3_fish()

    def ball_list(self):
        return ball_list(self)

    def close(self):
        """ Return control to PFC """
        self._pfc.send(-1)

    def quit(self):
        """ Close PFC """
        self._pfc.send(-2)

    def _read_v3_fish(self, filename='bin.fish'):
        a = FishBinaryReader(filename).asarray()
        assert a.shape[0] % 3 == 0, "bad fish array shape"
        return a.reshape(a.shape[0]/3, 3)

    def _read_v1_fish(self, filename='bin.fish'):
        return FishBinaryReader(filename).asarray()

    def __getattr__(self, item):
        """
        intercept method calls and try them as fish intrinsics
        """
        # shoud check for rw here?
        def handle_fishcall(*args):
            if len(args)==0:
                fish_string = "%s"  % (item)
                return self.eval(fish_string)
            else:
                fish_string = "%s(%s)" % (item, ",".join(map(str, args)))
                return self.eval(fish_string)

        return handle_fishcall


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

class pfc_object(object):
    """ Catch uncought method calls and try them as FISH intrinsics.  """
    def __getattr__(self, item):
        fname = self.prefix + item
        if not fname in self.methods:
            raise AttributeError("no fish intrinsic " + fname)

        # shoud check for rw here?
        def handle_fishcall(arg=None):
            if arg==None:
                fish_string = "%s(%s)" % (fname, self.find)
                return self._bridge.eval(fish_string)
            else:
                fish_string = "%s(%s)=%s" % (fname,
                                             self.find,
                                             str(arg))
                res = self._bridge.eval(fish_string)
                return arg
        return handle_fishcall


class pfc_contact(pfc_object):
    methods = """c_next c_ball1 c_ball2 c_b1clist c_b2clist c_gobj1 c_gobj2 c_go1clist
c_go2clist c_wseg c_type c_bflag c_broken c_x c_y c_z c_vpos c_nforce
c_xsforce c_ysforce c_zsforce c_sforce c_kn c_ks c_hn c_hs c_fric
c_nstrength c_sstrength c_ex c_pb c_xun c_yun c_zun c_vun c_jset
c_slipwork c_inhibit c_prop c_model c_extra c_vsforce c_dampn c_damps
c_thactive c_thlen c_thpipe c_thpow c_thres c_active c_installpb
c_ondisk c_ondisk c_nvforce c_xsvforce c_ysvforce c_zsvforce c_svforce
c_vsvforce c_knset c_ksset c_fricset c_dampnt c_ontri c_mom c_tmom
c_vbmom""".split()

    def __init__(self, idn, bridge):
        self.prefix = "c_"
        self.id = 0
        self._bridge = bridge
        self.methods = pfc_contact.methods
        self.find = 'find_contact(current_contact)'
    def __repr__(self):
        return "<pfc contact>"


class pfc_wall(pfc_object):
    methods = """w_next w_clist w_id w_x w_y w_z w_pos w_ux w_uy w_uz w_vu w_xvel
w_yvel w_zvel w_vvel w_xfob w_yfob w_zfob w_vfob w_kn w_ks w_fric w_ex
del_wall w_color w_flist w_wlist w_extra w_fix w_delete w_rxvel
w_ryvel w_rzvel w_rvel w_vrvel w_xmom w_ymom w_zmom w_mom w_vmom
w_type w_radvel w_radfob w_radend1 w_radend2 w_posend1 w_posend2 w_rad""".split()
    def __init__(self, idn, bridge):
        self.prefix = "w_"
        self.id = idn
        self._bridge = bridge
        self.methods = pfc_wall.methods
        self.find = 'find_wall(%i)' % (self.id)
    def __repr__(self):
        return "<pfc wall id=%i>" % (self.id)


class pfc_clump(pfc_object):
    methods = """cl_add cl_extra cl_id cl_list cl_next cl_rel cl_scale cl_color
cl_damp cl_mass cl_realmass cl_moi cl_vmoi cl_vol cl_volgiven cl_vfix
cl_xfix cl_yfix cl_zfix cl_rfix cl_vrfix cl_rxfix cl_ryfix cl_rzfix
cl_vfap cl_xfap cl_yfap cl_zfap cl_map cl_vmap cl_xmap cl_ymap cl_zmap
cl_vpos cl_x cl_y cl_z cl_vvel cl_xvel cl_yvel cl_zvel cl_rvel
cl_vrvel cl_rxvel cl_ryvel cl_rzvel cl_vfob cl_xfob cl_yfob cl_zfob
cl_mom cl_vmom cl_xmom cl_ymom cl_zmom cl_stress cl_vdisp cl_xdisp
cl_ydisp cl_zdisp""".split()

    def __init__(self, idn, bridge):
        self.prefix = "cl_"
        self.id = id
        self._bridge = bridge
        self.methods = pfc_clump.methods
        self.find = 'find_clump(%i)' % (self.id)
    def __repr__(self):
        return "<pfc clump id=%i>" % (self.id)


class pfc_meas(pfc_object):
    methods = """m_coord m_poros m_sfrac m_s11 m_s12 m_s21 m_s22 m_s13 m_s31
m_s23 m_s32 m_s33 m_ed11 m_ed12 m_ed21 m_ed22 m_ed13 m_ed31 m_ed23
m_ed32 m_ed33 m_x m_y m_z m_vpos m_rad m_id m_next m_tc11 m_tc12
m_tc21 m_tc22 m_tc13 m_tc31 m_tc23 m_tc32 m_tc33""".split()

    def __init__(self, idn, bridge):
        self.prefix = "m_"
        self.id = idn
        self._bridge = bridge
        self.methods = pfc_meas.methods
        self.find = 'find_meas(%i)' % (self.id)
    def __repr__(self):
        return "<pfc measurement sphere id=%i>" % (self.id)


class pfc_ball(pfc_object):
    methods = """b_next b_clist b_ctype b_xfix b_yfix b_zfix b_vfix
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
        self.prefix = "b_"
        self.id = idn
        self._bridge = bridge
        self.methods = pfc_ball.methods
        self.find = "find_ball(%i)" % (self.id)
    def __repr__(self):
        return "<pfc ball id=%i>" % (self.id)

if __name__=='__main__':
    pfc = pfcBridge()

    res = pfc.eval("1+1")
    assert res == 2

    res = pfc.eval("cos(1+2.2)")
    assert res == np.cos(1+2.2)

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
    #print pfc.ball_radii()

    #pfc.quit()
