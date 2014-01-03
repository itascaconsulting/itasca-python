from itasca import pfc5Bridge

# manually start pfc5
pfc = pfc5Bridge()
pfc._pfc.process = True
pfc._pfc.connect()

# pfc.execuitable_name = lambda self : \
#                         "C:\\Program Files\\Itasca\\PFC3D400\\exe64\\evpfc3d_64.exe"

print pfc.eval("1+1")
print pfc.eval("1/0")
