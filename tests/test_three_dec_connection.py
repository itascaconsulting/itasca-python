
from itasca import threeDEC_Connection
threeDEC = threeDEC_Connection()
threeDEC.start("./three_dec_socket_test.dat")
threeDEC.connect()

threeDEC.send(99.9)
threeDEC.send([1,2])
threeDEC.send([1,2,3])
threeDEC.send("James")

for i in range(10):
    print "sending", i, "...",
    threeDEC.send(i)
    print "sent", i
    value = threeDEC.receive()
    print "got", value, "from 3DEC"

threeDEC.send(-1)
threeDEC.end()
