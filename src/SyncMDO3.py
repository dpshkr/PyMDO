# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 11:21:48 2023

@author: Pushkar
"""

import socket
import numpy as np

class SyncMDO3:
    def __init__(self, ipaddress, port):
        self.__sock = socket.create_connection((ipaddress, port))
        
    def query(self, command):
        self.__sock.sendall((command+"\n").encode())
        response = ""
        
        # Read the response till newline character
        while (True):
            d = self.__sock.recv(1)
            if (d == b"\n"):
                break
            else:
                response += (d.decode())
        return response
        
    def write(self, command):
        self.__sock.sendall((command+"\n").encode())

    def readdata(self, channel, start=1, stop=10000):
        self.write(f":data:source ch{channel}") # Channel to recieve data from
        self.write(f":data:start {start}") # Starting point of the data 
        self.write(f":data:stop {stop}") # Stopping point of the data
        self.write(f":data:encdg ribinary") # Recieve in RIBinary format, as mentioned in the manual
        self.write(f":data:width 1") # Data width 1 (8 bits) is enough, as the ADC is 8 bit
        self.write(":header 0") # Don't send any header
        
        '''
        Read the necessary scaling factors to properly scale the received data
        '''
        ymult = float(self.query(":wfmoutpre:ymult?")) # Y dimension multiplyng factor
        yoffset = float(self.query(":wfmoutpre:yoff?")) # Y offset
        yzero = float(self.query(":wfmoutpre:yzero?")) # Y zero
        xzero = float(self.query(":wfmoutpre:xzero?")) # X Zero
        xincr = float(self.query(":wfmoutpre:xincr?")) # ime interval between two samples, sampling rate

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
        
        return datanp
        
    def close(self):
        self.__sock.close()
