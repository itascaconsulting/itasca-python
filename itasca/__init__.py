"""Python connectivity for Itasca software.

This library implements a connection via sockets between Python and
the numerical modeling software from Itasca Consulting Group.
Functions are provided to read and write files in the Itasca FISH
binary format.

itascacg.com/software

FLAC, FLAC3D, PFC2D, PFC3D, UDEC & 3DEC

See https://github.com/jkfurtney/itasca-python for more information.
"""

__version__ = "2016.05.24"

from itasca import FLAC3D_Connection
from itasca import PFC3D_Connection
from itasca import FishBinaryReader
from itasca import FLAC_Connection
from itasca import UDEC_Connection
from itasca import threeDEC_Connection
from itasca import UDECFishBinaryReader
from itasca import UDECFishBinaryWriter
from p2pLink import p2pLinkClient, p2pLinkServer
