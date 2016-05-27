from p2pLink import p2pLinkServer
import numpy as np

with p2pLinkServer() as s:
    s.start()

    while True:
        a=s.read_data()
        if type(a) is int and a ==-1:
            print "done"
            break
        print "got", a
        if type(a) is np.ndarray:
            print a.shape
