"""Mock CCFD server

The MockCcfdServer class invokes and communicates with PFC the same
way the CCFD Proxy server does.

The purpose of this twofold:

(1) to provide a way to test PFC's CCFD functionality without
installing the CCFD software and

(2) to provide an example of how to couple other software
with PFC using the CCFD socket/files mechanism.
"""

import struct
import socket
import subprocess


class CcfdPacket(object):
    " Python version of the C struct _PACKET used to communicate with PFC "
    format_string ='4i 2d i 2048sxxxx'  # why are there are 4 extra bytes?
    byte_count = struct.calcsize(format_string)
    PFC_CYCLE   = 10002
    PFC_STOP    = 10006
    def __init__(self, raw_data=None):
        self.ifrom = 0
        self.to   = 0
        self.type = 0
        self.step = 0
        self.time = 0
        self.dt   = 0
        self.size = 0
        self.data = "\0"*2048
        if raw_data:
            self.read(raw_data)

    def pack_strings(self, s1, s2):
        "put two strings into the data segment of the packet"
        self.data = "%s\0%s\0%s" % (s1, s2, "\0"*(2048-len(s1)-len(s2)-2))

    def raw_data(self):
        "return the raw bytes representing the packet"
        return struct.pack(CcfdPacket.format_string, self.ifrom, self.to,
                           self.type, self.step, self.time, self.dt,
                           self.size, self.data)

    def read(self, raw_data):
        "read the raw bytes into the Python representation"
        t = struct.unpack(CcfdPacket.format_string, raw_data)
        self.ifrom,self.to,self.type, \
        self.step,self.time,self.dt, \
        self.size, self.data = t

    def get_strings(self):
        "return the two strings in the packet data segment"
        assert len(self.data)==2048
        return self.data.split("\0")[:2]

    def __repr__(self):
        "return a string containing a printable representation of the packet"
        fmt = "from %i to: %i\ntype %i \n" + \
              "step %i \ntime %lf \ndt %lf \n" + \
              "size %i \nstrings: %s %s\n"
        s1, s2 = self.get_strings()
        return fmt % (self.ifrom, self.to, self.type,
                      self.step, self.time, self.dt, self.size, s1, s2)


class SocketServer(object):
    "handles the low level details of the socket communication"
    def __init__(self, port):
        self.port = port
        self.size = CcfdPacket.byte_count
    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("", self.port))
        self.socket.listen(1)
        self.conn, addr = self.socket.accept()
        print 'socket connection established by', addr

    def send_packet(self, packet):
        self.conn.sendall(packet.raw_data())

    def get_packet(self):
        bytes_read=0
        data=''
        while bytes_read < self.size:
            data_in = self.conn.recv(self.size - bytes_read)
            data += data_in
            bytes_read += len(data)
        assert len(data)==self.size, "bad packet data from PFC"
        return CcfdPacket(data)

    def close(self): self.conn.close()


class MockCcfdServer(object):
    """Mimic CCFD's invocation of and communication with PFC for
    testing and as an example of coupling other software with PFC
    via the CCFD mechanism."""
    def __init__(self):
        #exename = "..\\..\\..\\binaries\\Win32Debug\\pfc3d500_gui_debug.exe"
        self.exename = "..\\..\\..\\binaries\\x64Debug\\pfc3d500_gui_64_debug.exe"
        self.server = SocketServer(2500)
        self.iteration = 0
        self.global_time = 0

    def start_pfc(self, pfc_datafile_name):
        """launch PFC in a seperate process with the given filename as
        a commandline argument"""
        args = [self.exename, pfc_datafile_name]
        self.process = subprocess.Popen(args)

    def connect_to_pfc(self, node_filename, element_filename):
        """Connect to PFC, send Mesh and receve PFC initial conditions
        return values are the initial porosity and body force filenames"""
        assert self.process
        self.server.start()
        self.server.get_packet()
        print "got handshake packet"
        self.server.send_packet(CcfdPacket())
        print "sent handshake packet"

        mesh_packet = CcfdPacket()
        mesh_packet.pack_strings(node_filename, element_filename)
        print "sending mesh packet", mesh_packet
        self.server.send_packet(mesh_packet)

        initial_conditions = self.server.get_packet()
        print "got initial conditions packet", initial_conditions
        return initial_conditions.get_strings()

    def cycle_pfc(self, time_interval):
        """direct PFC to solve forward for the given time interval
        return values are the porosity and body force filenames """
        cycle_packet = CcfdPacket()
        cycle_packet.type = CcfdPacket.PFC_CYCLE
        cycle_packet.step = self.iteration
        cycle_packet.time = self.global_time + time_interval
        cycle_packet.dt =  time_interval
        cycle_packet.pack_strings("cfd_velocity.dat",
                                  "cfd_pressure_gradient.dat")
        print "sending cycle packet", cycle_packet
        self.server.send_packet(cycle_packet)
        print "waiting for cycle response packet"
        response = self.server.get_packet()
        print "got response packet", response
        self.iteration += 1
        self.global_time += time_interval
        return response.get_strings()

    def stop_pfc(self):
        final = CcfdPacket()
        final.type = CcfdPacket.PFC_STOP
        print "sending stop packet to PFC"
        self.server.send_packet(final)
        #self.process.wait()
        print "pfc done"
        self.server.close()


if __name__=='__main__':
    ccfd = MockCcfdServer()
    ccfd.start_pfc("pfc5.dat")
    ccfd.connect_to_pfc("Node.dat", "Elem.dat")
    for i in range(10):
        ccfd.cycle_pfc(0.1)
    ccfd.stop_pfc()
