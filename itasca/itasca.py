import struct
import socket
import select
import time
import subprocess
import os
import numpy as np

class _ItascaFishSocketServer(object):
    """Low level details of the Itasca FISH socket communication"""
    def __init__(self, fish_socket_id=0):
        assert type(fish_socket_id) is int and 0 <= fish_socket_id < 6
        self.port = 3333 + fish_socket_id

    def start(self):
        """() -> None. Open the low level socket connection. Blocks but allows the Python thread scheduler to run.

        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("", self.port))
        self.socket.listen(1)
        while True:
            connected, _, _ = select.select([self.socket], [], [], 0.0)
            if connected: break
            else: time.sleep(1e-8)
        self.conn, addr = self.socket.accept()
        print 'socket connection established by', addr

    def send_data(self, value):
        """(value: any) -> None. Send value to Itasca software. value must be int, float, length two list of doubles, length three list of doubles or a string.

        """
        while True:
            _, write_ready, _ = select.select([], [self.conn], [], 0.0)
            if write_ready: break
            else: time.sleep(1e-8)

        if type(value) == int:
            self.conn.sendall(struct.pack("i", 1))
            self.conn.sendall(struct.pack("i", value))
        elif type(value) == float:
            self.conn.sendall(struct.pack("i", 2))
            self.conn.sendall(struct.pack("d", value))
        elif type(value) == list and len(value)==2:
            float_list = [float(x) for x in value]
            self.conn.sendall(struct.pack("i", 5))
            self.conn.sendall(struct.pack("dd", float_list[0], float_list[1]))
        elif type(value) == list and len(value)==3:
            float_list = [float(x) for x in value]
            self.conn.sendall(struct.pack("i", 6))
            self.conn.sendall(struct.pack("ddd", float_list[0],
                                          float_list[1], float_list[2]))
        elif type(value) == str:
            length = len(value)
            self.conn.sendall(struct.pack("ii", 3, length))
            buffer_length = 4*(1+(length-1)/4)
            format_string = "%is" % buffer_length
            value += " "*(buffer_length - length)
            self.conn.sendall(struct.pack(format_string, value))
        else:
            raise Exception("unknown type in send_data")

    def wait_for_data(self):
        """() -> None. Block until data is available. This call allows the Python thread scheduler to run.

        """
        while True:
            input_ready, _, _ = select.select([self.conn],[],[], 0.0)
            if input_ready: return
            else: time.sleep(1e-8)

    def read_type(self, type_string):
        """(type: str) -> any. This method should not be called directly. Use the read_data method.

        """
        byte_count = struct.calcsize(type_string)
        bytes_read = 0
        data = ''
        self.wait_for_data()
        while bytes_read < byte_count:
            data_in = self.conn.recv(byte_count - bytes_read)
            data += data_in
            bytes_read += len(data)
        assert len(data)==byte_count, "bad packet data"
        return data

    def read_data(self):
        """() -> any. Read the next item from the socket connection."""
        raw_data = self.read_type("i")
        type_code, = struct.unpack("i", raw_data)
        if type_code == 1:     # int
            raw_data = self.read_type("i")
            value, = struct.unpack("i", raw_data)
            return value
        elif type_code == 2:   # float
            raw_data = self.read_type("d")
            value, = struct.unpack("d", raw_data)
            return value
        elif type_code == 3:   # string
            length_data = self.read_type("i")
            length, = struct.unpack("i", length_data)
            buffer_length = (4*(1+(length-1)/4))
            format_string = "%is" % buffer_length
            data = self.read_type(format_string)
            return data [:length]
        elif type_code == 5:   # V2
            raw_data = self.read_type("dd")
            value0, value1 = struct.unpack("dd", raw_data)
            return [value0, value1]
        elif type_code == 6:   # V3
            raw_data = self.read_type("ddd")
            value0, value1, value3 = struct.unpack("ddd", raw_data)
            return [value0, value1, value3]
        assert False, "Data read type error"

    def get_handshake(self):
        """() -> int. Read the handshake packet from the socket. """
        raw_data = self.read_type("i")
        value, = struct.unpack("i", raw_data)
        print "handshake got: ", value
        return value

    def close(self):
        """() -> None. Close the active socket connection."""
        self.conn.close()


class _ItascaSoftwareConnection(object):
    """Base class for communicating via FISH sockets with an Itasca program. This class spawns a new instance of the Itasca software and initializes the socket communication.

    """
    def __init__(self, fish_socket_id=0):
        """(fish_socket_id=0: int) -> Instance. Constructor."""
        self.executable_name = None
        self.server = _ItascaFishSocketServer(fish_socket_id)
        self.iteration = 0
        self.global_time = 0
        self.fishcode = 178278912

    def start(self, datafile_name):
        """(projectfile_name: str, datafile_name: str) -> None. Launch Itasca software in a separate process, open the specified data file. The green execute button must be pressed in the Itasca software to start the calculation.

        """
        if os.access(datafile_name, os.R_OK):
            args = [self.executable_name, datafile_name]
            self.process = subprocess.Popen(args)
        else:
            raise ValueError("The file {} is not readable".format(datafile_name))


    def connect(self):
        """() -> None. Connect to Itasca software, read fishcode to confirm connection. Call this function to establish the socket connection after calling the start method to launch the code.

        """
        assert self.process
        self.server.start()
        value = self.server.get_handshake()
        print "got handshake packet"
        assert value == self.fishcode
        print "connection OK"

    def send(self, data):
        """(data: any) -> None. Send an item to the Itasca code."""
        self.server.send_data(data)

    def receive(self):
        """() -> any. Read an item from the Itasca code."""
        return self.server.read_data()

    def end(self):
        """() -> None. Close the socket connection."""
        self.server.close()

class FLAC3D_Connection(_ItascaSoftwareConnection):
    """Launch and connect to FLAC3D."""
    def __init__(self, fish_socket_id=0):
        """(fish_socket_id=0: int) -> Instance. Constructor."""
        _ItascaSoftwareConnection.__init__(self, fish_socket_id)
        self.executable_name = "C:\\Program Files\\Itasca\\Flac3d500\\exe64\\flac3d501_gui_64.exe"

class PFC3D_Connection(_ItascaSoftwareConnection):
    """Launch and connect to PFC3D."""
    def __init__(self, fish_socket_id=0):
        """(fish_socket_id=0: int) -> Instance. Constructor."""
        _ItascaSoftwareConnection.__init__(self, fish_socket_id)
        self.executable_name = "C:\\Program Files\\Itasca\\PFC500\\exe64\\pfc3d500_gui_64.exe"

class PFC2D_Connection(_ItascaSoftwareConnection):
    """Launch and connect to PFC2D."""
    def __init__(self, fish_socket_id=0):
        """(fish_socket_id=0: int) -> Instance. Constructor."""
        _ItascaSoftwareConnection.__init__(self, fish_socket_id)
        self.executable_name = "C:\\Program Files\\Itasca\\PFC500\\exe64\\pfc2d500_gui_64.exe"


class FLAC_Connection(_ItascaSoftwareConnection):
    """Connect to FLAC. FLAC must be started manually first."""
    def start(self, _=None):
        """() -> None. Calling this function raises an exception. Do not call this function, start FLAC manually."""
        raise NotImplemented("FLAC must be started manually")
    def connect(self):
        """() -> None. Call this function to connect to FLAC once it has been started manually.

        """
        self.process=True
        _ItascaSoftwareConnection.connect(self)

class UDEC_Connection(_ItascaSoftwareConnection):
    """Connect to UDEC. UDEC must be started manually first."""
    def start(self, _=None):
        """() -> None. Calling this function raises an exception. Do not call this function, start UDEC manually."""
        raise NotImplemented("UDEC must be started manually")
    def connect(self):
        """() -> None. Call this function to connect to UDEC once it has been started manually.

        """
        self.process=True
        _ItascaSoftwareConnection.connect(self)

class threeDEC_Connection(_ItascaSoftwareConnection):
    """Launch and connect to 3DEC."""
    def __init__(self, fish_socket_id=0):
        """(fish_socket_id=0: int) -> Instance. Constructor."""
        _ItascaSoftwareConnection.__init__(self, fish_socket_id)
        self.executable_name = "C:\\Program Files\\Itasca\\3DEC500\\exe64\\3dec_dp500_gui_64.exe"


class FishBinaryReader(object):
    """Read structured FISH binary files.

    Call the constructor with the structured FISH filename and call
    read() to read individual values. This class also supports
    iteration. Return values are converted to python types. Supports
    int, float, string, bool, v2 and v3.

    >>> fish_file = FishBinaryReader('my_fish_data.fish')
    >>> for val in fish_file:
    ...    print val
    42
    "this is a string"
    [1.0,2.0,3.0]

    """
    def __init__(self, filename):
        """(filename: str) -> FishBinaryReader object. """
        self.file = open(filename, "rb")
        fishcode = self._read_int()
        assert fishcode == 178278912, "invalid FISH binary file"

    def _read_int(self):
        data = self.file.read(struct.calcsize('i'))
        value, = struct.unpack("i", data)
        return value

    def _read_double(self):
        data = self.file.read(struct.calcsize('d'))
        value, = struct.unpack("d", data)
        return value

    def read(self):
        """() -> any. Read and return a value (converted to a Python type) from the .fish binary file.

        """
        type_code = self._read_int()

        if type_code == 1:  # int
            return self._read_int()
        if type_code == 8:  # bool
            value = self._read_int()
            return_value = True if value else False
            return return_value
        if type_code == 2:  # float
            return self._read_double()
        if type_code == 3:
            length = self._read_int()
            buffer_length = 4*(1+(length-1)/4)
            format_string = "%is" % buffer_length
            data = self.file.read(struct.calcsize(format_string))
            return data [:length]
        if type_code == 5:  # v2
            return [self._read_double(), self._read_double()]
        if type_code == 6:  # v3
            return [self._read_double(), self._read_double(),
                    self._read_double()]

    def __iter__(self):
        self.file.seek(0)  # return to the begining of the file
        self._read_int()   # pop the magic number off
        return self

    def next(self):
        """() -> any. Get the next item from the FISH binary file."""
        try:
            return self.read()
        except:
            raise StopIteration

    def aslist(self):
        """() -> [any]. Return fish file contents as a Python list."""
        return [x for x in self]

    def asarray(self):
        """() -> numpy array. Return fish file contents as a numpy array. Types must be homogeneous.

        """
        return np.array(self.aslist())

class UDECFishBinaryReader(FishBinaryReader):
    "Special version of FishBinarReader for files generated by UDEC."
    def _read_int(self):
        data = self.file.read(struct.calcsize('i'))
        value, = struct.unpack("i", data)
        data = self.file.read(struct.calcsize('i')) # read the dummy data off
        return value

class FishBinaryWriter(object):
    """Write fish binary data. data can be any iterable (array, list, etc.).

    example: FishBinaryWriter("t.fis", [12.23, 1, 33.0203, 1234.4])
    """
    def __init__(self, filename, data):
        """(filename: str, data: iterable) -> FishBinaryWriter instance."""
        with open(filename, "wb") as f:
            self._write_int(f,178278912)
            for datum in data:
                if type(datum) is float:
                    self._write_int(f, 2)
                    self._write_double(f, datum)
                elif type(datum) is int:
                    self._write_int(f, 1)
                    self._write_int(f, datum)
                else:
                    raise TypeError(
                        "Currently unsupported type for Fish binary write ")

    def _write_int(self, f, datum):
        f.write(struct.pack("i", datum))

    def _write_double(self, f, datum):
        f.write(struct.pack("d", datum))

class UDECFishBinaryWriter(FishBinaryWriter):
    "Fish Binary writer for UDEC (which has 8 byte ints)"
    def _write_int(self, f, datum):
        f.write(struct.pack("i", datum))
        f.write(struct.pack("i", 0))
