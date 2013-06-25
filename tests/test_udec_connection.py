from itasca import UDEC_Connection

udec = UDEC_Connection()
udec.connect()

for i in range(10):
    print "sending", i
    udec.send(i)
    value = udec.receive()
    print "got", value, "from UDEC"

udec.send(-1)
udec.end()
