from itasca import FLAC3D_Connection

flac3d = FLAC3D_Connection()
flac3d.start("flac3d_socket_test.f3dat")
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
