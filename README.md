Python connectivity for Itasca software.

This library implements a connection via sockets between Python and
the numerical modeling software from Itasca Consulting
Group.

www.itascacg.com/software

FLAC, FLAC3D, PFC2D, PFC3D, UDEC & 3DEC

# Installation

A pure-python module, easy installation.

    $ python setup.py install

# Demo high-level interface to PFC

    from itasca import pfcBridge
    pfc = pfcBridge()

## Evaluate fish expressions:

    res = pfc.eval("1+1")
    assert res == 2

    res = pfc.eval("cos(1+2.2)")
    assert res == math.cos(1+2.2)

    res = pfc.eval("a=123.456")
    assert res == 0

    res = pfc.eval("a")
    assert res == 123.456

## Execute PFC commands:

    pfc.cmd("ball id 1 rad 1 x 12.30 y .2 z 0")
    pfc.cmd("ball id 2 rad 1 x 12.30 y .4 z 3")
    pfc.cmd("ball id 3 rad 1 x 12.30 y .5 z 6")
    pfc.cmd("prop dens 2500 kn 1.0e3 ks 1.0e3")
    pfc.cmd("set grav 0 0 -9.81")



## Use a *Pythonic* interface to PFC model objects:

    for ball in pfc.ball_list():
        print ball.x(), ball.y(), ball.z()

## Close connection:

    pfc.close()

# Low level socket interface to all Itasca codes

Send and receive FISH data to Itasca codes

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

On the Itasca code side a simple server loop reads these values and
performs some action.

# Fish binary format reader

## Generate some fish binary data

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


## Read it in Python

    from itasca import FishBinaryReader

    fish_file = FishBinaryReader("testdata.fish")

    assert fish_file.read() == 1
    assert fish_file.read() == 99.987
    assert fish_file.read() == "James"
    assert fish_file.read() == [99.5, 89.3]
    assert fish_file.read() == [7.0, 8.0, 9.0]
