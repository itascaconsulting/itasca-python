# Python connectivity for Itasca software.

This library implements a connection via sockets between Python and
the numerical modeling software from Itasca Consulting Group.
Functions are provided to read and write files in the Itasca FISH
binary format.

www.itascacg.com/software

*FLAC*, *FLAC3D*, *PFC2D*, *PFC3D*, *UDEC* & *3DEC*

The Python interpreter is now embedded within *FLAC3D* and *PFC3D* see:
 - http://www.itascacg.com/python-and-pfc
 - https://www.itascacg.com/software/flac3d/videos/using-python-in-flac3d-6
 
In the Python interpreter inside *FLAC3D* and *PFC3D* the functionality of this module is
available in the `itasca.util` module.


*Note:* If the used Itasca code includes a python installation the use of the p2pLinkClient/p2pLinkServer classes (python to python socket link) is recommended. For Itascsa codes without python use the TCP Socket with Itasca Fish.

## Installation

Via pip:

```python
pip install itasca
```

or from source:
```python
python setup.py install
```

## Requirements

`numpy` >= 1.0.2

## Usage

The Itasca python module can be used after the installation such as any other 
python module. The `client` is running outside the Itasca code and the `server`
is running within the Itasca code. The `client` is a python script using this 
module. For the `server` can be started as python or fish function. See the 
accordings sections below for further details.

### Python to Python socket link

Simple TCP socket client and server classes are provided to link two
Python programs. `str`, `int`, `float`, and NumPy arrays can be sent
over the link. The classes `p2pLinkServer` and `p2pLinkClient` are
demonstrated below.

An example of the server side of the connection is given below.

```python
from itasca import p2pLinkServer
import numpy as np

with p2pLinkServer() as s:
    s.start()

    while True:
        a = s.read_data()
        if type(a) is int and a ==-1:
            print("done")
            break
        print(f"got {a}")
        if type(a) is np.ndarray:
            print(a.shape)
```

Finally, an example of the client side of the connection is given.

```python
from itasca import p2pLinkClient
import numpy as np

with p2pLinkClient() as s:
    s.connect("localhost")
    s.send_data("James")
    s.send_data(np.array([1,2,3]))

    adata = np.random.random((1000,1000))
    print(adata)
    s.send_data(adata)

    for i in range(10):
        print(f"sent {i}")
        s.send_data(i)

    s.send_data(-1)
```

### TCP socket connection to all Itasca codes using FISH

The classes `FLAC3D_Connection`, `PFC3D_Connection`,
`FLAC_Connection`, `UDEC_Connection` and `threeDEC_Connection` allow
Python to connect to an Itasca code and exchange information with FISH
programs. The data types are converted between FISH and Python. `int`,
`float`, `str`, and length 2 and 3 vectors are supported.

The following is an example of the Python side of a connection.

```python
from itasca import FLAC3D_Connection

flac3d = FLAC3D_Connection()
flac3d.start("flac3d_socket_test.f3dat")
flac3d.connect()

flac3d.send(99.9)
flac3d.send([1,2])
flac3d.send([1,2,3])
flac3d.send("James")

for i in range(10):
    print(f"sending {i}...")
    flac3d.send(i)
    print(f"sent {i}")
    value = flac3d.receive()
    print(f"got {value} from FLAC3D")

flac3d.send(-1)
flac3d.end()
flac3d.shutdown()
```

On the Itasca code side a simple server loop reads these values and
performs some action. Below is an example that is execute be the
script above (see *tests/flac3d_socket_test.f3dat*):

```
;; this is the FLAC3D side of the FLAC3D/Python coupling example.

;; FLAC3D is started by the Python program. When FLAC3D is started it
;; is given this input file as a command line argument. To start the
;; coupling example run this file by clicking the green button. The
;; open_socket FISH function opens a connection to the Python
;; program. FLAC3D then waits for the Python program to write a FISH
;; parameter. 1000.1 is added to the value and it is sent back to the
;; Python program. When FLAC3D receives a value of -1 from Python it
;; exits the read/write loop.


def open_socket
  array data(1)
  s = socket.open(0,1,3333)

  loop i(0, 1000)
    oo = io.out('reading')
    oo = socket.read(data, 1, 1)
    oo = io.out(string.build("got %1 from python server", data(1)))

    if type(data(1)) = 1 then
      if data(1)=-1 then
        oo = io.out('breaking out of read/write loop')
        exit
      endif
      data(1) = data(1) + 1000.1
    endif

    oo = socket.write(data, 1, 1)
  end_loop
end
[ open_socket ]

def close_socket
  oo = socket.close(1)
  oo = io.out('closed socket connection')
end
[ close_socket ]
```

### Executable path 

The module uses the default installation path to search for the executables of 
the software code. The default executable path can be modified, example: 

```python 
from itasca import FLAC3D_Connection
f3d = FLAC3D_Connection()
f3d.executable_name = "C:\\my\\custom\\path\\FLAC3D700\\exe64\\flac3d700_gui.exe"
f3d.start('my_script')
... 
```

### Fish binary format reader

The classes `FishBinaryReader` and `FishBinaryWriter` allow Python to
read and write FISH binary data. The following is an example of FLAC3D
writing FISH binary data.

```
def genIOtestdata
  array a(1)
  fp = open('testdata.fish', 1, 0)
  a(1) = 1
  oo = write(a, 1)
  a(1) = 99.987
  oo = write(a, 1)
  a(1) = 'James'
  oo = write(a, 1)
  a(1) = vector(99.5, 89.3)
  oo = write(a, 1)
  a(1) = vector(7,8,9)
  oo = write(a, 1)
  oo = close
end
@genIOtestdata
```

This data can be read from Python

```python
from itasca import FishBinaryReader
fish_file = FishBinaryReader("testdata.fish")
```

Either one entry at a time:

```python
assert fish_file.read() == 1
assert fish_file.read() == 99.987
assert fish_file.read() == "James"
assert fish_file.read() == [99.5, 89.3]
assert fish_file.read() == [7.0, 8.0, 9.0]
```
Or all entries can be read into a list or `numpy` array

```python

FishBinaryReader("testdata2.fish").aslist()  # convert data to list
   [1, 2, 3, 4, 5, 6, 7]
FishBinaryReader("testdata2.fish").asarray() # convert to NumPy array
   array([[1, 2, 3, 4, 5, 6, 7])
```

Similarly FISH binary data files be written from Python.

```python
FishBinaryWriter("t.fis", [12.23, 1, 33.0203, 1234.4])
```

Special classes are provided for *UDEC* which uses a different integer
size: `UDECFishBinaryReader`, and `UDECFishBinaryWriter`

