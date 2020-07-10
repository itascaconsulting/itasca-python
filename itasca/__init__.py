"""Python connectivity for Itasca software.

This library implements a connection via sockets between Python and
the numerical modeling software from Itasca Consulting Group.
Functions are provided to read and write files in the Itasca FISH
binary format.

itascacg.com/software

FLAC, FLAC3D, PFC2D, PFC3D, UDEC & 3DEC

See https://github.com/jkfurtney/itasca-python for more information.
"""

__version__ = "2020.07.10"

from .main import FLAC3D_Connection
from .main import PFC3D_Connection
from .main import PFC2D_Connection
from .main import FishBinaryReader
from .main import FishBinaryWriter
from .main import FLAC_Connection
from .main import UDEC_Connection
from .main import ThreeDEC_Connection
from .main import UDECFishBinaryReader
from .main import UDECFishBinaryWriter
from .main import p2pLinkClient, p2pLinkServer
