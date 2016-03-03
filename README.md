# Python connectivity for Itasca software.

This library implements a connection via sockets between Python and
the numerical modeling software from Itasca Consulting Group.
Functions are provided to read and write files in the Itasca FISH
binary format.

www.itascacg.com/software

FLAC, FLAC3D, PFC2D, PFC3D, UDEC & 3DEC

The Python interpreter is now embedded within PFC3D see:
http://www.itascacg.com/python-and-pfc

## Requirements

`numpy` > 1.0.2

## Installation

Via pip:

```python
pip install itasca
```

or from source:
```python
python setup.py install
```

## Low level socket interface to all Itasca codes

Send and receive FISH data to Itasca codes

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

Here is an example of creating FISH binary data with FLAC3D

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

This can be read from Python

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
