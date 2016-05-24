## see: https://docs.python.org/2/howto/sockets.html
import numpy as np
import struct
import socket
import select
import time
import cStringIO

class _socketBase(object):
    code = 12345
    def send_data(self, value):
        """(value: any) -> None. Send value. value must be a number, a string or a NumPy array. """
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
        elif type(value) == np.ndarray:
            self.conn.sendall(struct.pack("i", 7))
            buffer = cStringIO.StringIO()
            np.save(buffer, value)
            data = buffer.getvalue()
            self.conn.sendall(struct.pack("i", len(data)))
            self.conn.sendall(data)
        else:
            raise Exception("unknown type in send_data")

    def wait_for_data(self):
        """() -> None. Block until data is available. This call allows the Python thread scheduler to run.
        """
        while True:
            input_ready, _, _ = select.select([self.conn],[],[], 0.0)
            if input_ready: return
            else: time.sleep(1e-8)

    def read_type(self, type_string, array_bytes=None):
        """(type: str) -> any. This method should not be called directly. Use the read_data method.
        """
        if array_bytes is None:
            byte_count = struct.calcsize(type_string)
        else:
            byte_count = array_bytes
        bytes_read = 0
        data = ''
        self.wait_for_data()
        while bytes_read < byte_count:
            data_in = self.conn.recv(byte_count - bytes_read)
            data += data_in
            bytes_read += len(data_in)
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
        elif type_code == 7:  # NumPy array:
            nbytes = struct.unpack("i", self.read_type("i"))[0]
            a = np.load(cStringIO.StringIO(self.read_type("",nbytes)))
            return a
        assert False, "Data read type error"

    def close(self):
        """() -> None. Close the active socket connection."""
        if hasattr(self, "conn"):
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
        else:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()

    def __enter__(self):
        return self

    def __exit__(self, eType, eValue, eTrace):
        print "cleaning up socket"
        self.close()

class p2pLinkServer(_socketBase):
    """Python to Python socket link server. Send and receive numbers, strings
    and NumPy arrays between Python instances."""
    def __init__(self, port=5000):
        """(port=5000) -> None. Create a Python to Python socket server. Call
        the start() method to open the connection."""
        assert type(port) is int
        self.port = port

    def start(self):
        """() -> None. Open the socket connection. Blocks but allows the
        Python thread scheduler to run.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("", self.port))
        self.socket.listen(1)
        while True:
            connected, _, _ = select.select([self.socket], [], [], 0.0)
            if connected: break
            else: time.sleep(1e-8)
        self.conn, addr = self.socket.accept()
        assert self.read_data() == _socketBase.code
        print "got code"

class p2pLinkClient(_socketBase):
    """Python to Python socket link client. Send and receive numbers, strings
    and NumPy arrays between Python instances."""
    def __init__(self,port=5000):
        """(port=5000) -> None. Create a Python to Python socket link client.
        Call the start() method to open the connection.""
        """
        assert type(port) is int
        self.port = port
    def connect(self, machine):
        """(machine: str) -> None. Connect to a Python to Python link server.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((machine,self.port))
        self.conn = self.socket
        self.send_data(_socketBase.code)
        print "sent code"
