from p2pLink import p2pLinkClient
import numpy as np

with p2pLinkClient() as s:

    s.connect("localhost")

    s.send_data("James")

    s.send_data(np.array([1,2,3]))

    adata = np.random.random((1000,1000))
    print adata
    s.send_data(adata)

    for i in range(10):
        print "sent", i
        s.send_data(i)

    s.send_data(-1)
