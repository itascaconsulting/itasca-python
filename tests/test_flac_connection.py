from itasca import FLAC_Connection

flac = FLAC_Connection()
#flac.start("test flac_socket_test.dat")
flac.process = True
flac.connect()

flac.send(99.9)
flac.send([1,2])
flac.send([1,2,3])
flac.send("James")

for i in range(10):
    print "sending", i, "...",
    flac.send(i)
    print "sent", i
    value = flac.receive()
    print "got", value, "from FLAC"

flac.send(-1)
flac.end()
