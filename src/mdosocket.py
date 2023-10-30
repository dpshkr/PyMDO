# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 11:21:48 2023

@author: Pushkar
"""

import socket
import numpy as np

class MDO3024:
    def __init__(self, ipaddress, port):
        self.__sock = socket.create_connection((ipaddress, port))
        
    def query(self, command):
        self.__sock.sendall((command+"\n").encode())
        response = ""
        while (True):
            d = self.__sock.recv(1)
            if (d == b"\n"):
                break
            else:
                response += (d.decode())
        return response
    def write(self, command):
        self.__sock.sendall((command+"\n").encode())

    def afg_setfrequency(self, frequency):
        self.write(f":afg:frequency {frequency}")

    def sethorizontalscale(self, scale):
        self.write(f":horizontal:scale {scale}")

    def readdata(self, channel, start=1, stop=10000):
        self.write(f":data:source ch{channel}")
        self.write(f":data:start {start}")
        self.write(f":data:stop {stop}")
        self.write(f":data:encdg ribinary")
        self.write(f":data:width 1")
        self.write(":header 0")

        ymult = float(self.query(":wfmoutpre:ymult?"))
        yoffset = float(self.query(":wfmoutpre:yoff?"))
        yzero = float(self.query(":wfmoutpre:yzero?"))
        xzero = float(self.query(":wfmoutpre:xzero?"))
        xincr = float(self.query(":wfmoutpre:xincr?"))

        self.write("CURV?")
        '''
        Read the IEEE488.2 binary block header
        '''
        hash_ = self.__sock.recv(1)
        if (hash_ != b"#"):
            raise ValueError("Invalid Data Recieved")
        N = int((self.__sock.recv(1)).decode(), base=16)
        ndata = int((self.__sock.recv(N)).decode(), base=10)

        '''
        Start reading the actual bytes
        '''
        rawdata = np.zeros(ndata, dtype=np.int8)
        bytes_recd = 0
        while bytes_recd < ndata:
            chunk = self.__sock.recv(min(ndata-bytes_recd, 2048))
            if chunk == b"":
                raise RuntimeError("socket connection broken")
            rawdata[bytes_recd:bytes_recd+len(chunk)] = np.frombuffer(chunk, dtype=np.int8)
            bytes_recd += len(chunk)
            
        self.__sock.recv(1)
        
        datanp = np.zeros([ndata,2])
        datanp[:,1] = (rawdata-yoffset)*ymult + yzero
        datanp[:,0] = np.linspace(xzero, (ndata+1)*xincr, ndata)
        '''
        data = np.zeros([no_of_bytes, 2])
        i = 0
        for chunk in rawdata:
            for byte in chunk:
                k = int.from_bytes(byte.to_bytes(1), signed=True)
                data[i,1] = (k - yoffset)*ymult + yzero
                data[i,0] = xzero + i*xincr
                i += 1

        '''
        
        return datanp
        
    def close(self):
        self.__sock.close()


m = MDO3024("10.33.20.173", 4000)
print(m.query("*idn?"))

