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

## TCP socket connection to all Itasca codes

The classes `FLAC3D_Connection`, `PFC3D_Connection`,
`FLAC_Connection`, `UDEC_Connection` and `threeDEC_Connection` allow
Python to connect to an Itasca code and exchange information with FISH
programs. The data types are converted between FISH and Python. `int`,
`float`, `str`, and length 2 and 3 vectors are supported.

The following is an example of the Python side of a connection.

```python
from itasca import FLAC3D_Connection

flac3d = FLAC3D_Connection()
flac3d.start("flac_socket_test.f3dat")
flac3d.connect()

flac3d.send(99.9)
flac3d.send([1,2])
flac3d.send([1,2,3])
flac3d.send("James")

for i in range(10):
    print "sending", i, "...",
    flac3d.send(i)
    print "sent", i
    value = flac3d.receive()
    print "got", value, "from FLAC3D"

flac3d.send(-1)
flac3d.end()
```

On the Itasca code side a simple server loop reads these values and
performs some action.

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
  s = sopen(0,1,3333)

  loop i(0, 1000)
    oo = out('reading')
    oo = sread(data, 1, 1)
    oo = out(buildstr("got %1 from python server", data(1)))

    if type(data(1)) = 1 then
      if data(1)=-1 then
        oo = out('breaking out of read/write loop')
        exit
      endif
      data(1) = data(1) + 1000.1
    endif
    oo=swrite(data, 1, 1)

  end_loop

end
@open_socket

def close_socket
  oo=sclose(1)
  oo=out('closed socket connection')
end
@close_socket
```


## Fish binary format reader

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

## Python to Python socket link

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
            print "done"
            break
        print "got", a
        if type(a) is np.ndarray:
            print a.shape
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
    print adata
    s.send_data(adata)

    for i in range(10):
        print "sent", i
        s.send_data(i)

    s.send_data(-1)
```
