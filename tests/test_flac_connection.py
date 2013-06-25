from itasca import FLAC_Connection

flac = FLAC_Connection()
flac.connect()

for i in range(10):
    print "sending", i
    flac.send(i)
    value = flac.receive()
    print "got", value, "from FLAC"

flac.send(-1)
flac.end()
