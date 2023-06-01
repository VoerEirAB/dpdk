#! /usr/bin/env python
# SPDX-License-Identifier: BSD-3-Clause
# Copyright(c) 2018 Intel Corporation

from __future__ import print_function
from __future__ import unicode_literals

import socket 
import glob
import os
import sys
import time
import multiprocessing
from prometheus_client import start_http_server, CollectorRegistry, Counter, Gauge
import json
# For parsing the command line argument during calling of the script
import argparse 

BUFFER_SIZE = 200000

METRICS_PORT_PREFIX = "dpdk_port_"
DEFAULT_SOCKET_PATH = "/var/run/dpdk/default_client"
metrics = {}

METRICS_REQ = "{\"action\":0,\"command\":\"ports_all_stat_values\",\"data\":null}"
API_REG = "{\"action\":1,\"command\":\"clients\",\"data\":{\"client_path\":\""
API_UNREG = "{\"action\":2,\"command\":\"clients\",\"data\":{\"client_path\":\""

metric = Gauge('dpdk_exporter_total', 'List of metrics related to DPDK Interface', ['podname', 'pciaddress', 'namespace', 'type', 'nodename'])

try:
    raw_input  # Python 2
except NameError:
    raw_input = input  # Python 3

clients = []

def parse_socketpath():
    telemetry_paths = glob.glob('/var/run/dpdk/*/telemetry')
    return telemetry_paths
    
def getNodeName():
    nodename = socket.gethostname()
    return nodename

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-t', '--telemetry-socket-path', type=str, default=None, nargs='+',
        help='File path for telemetry socket.')

    args = parser.parse_args()

    telemetry_socket_paths = args.telemetry_socket_path

    return telemetry_socket_paths 

def get_clientPath(socketpath):
    cpath = []
    for spath in socketpath:
        cpath.append(spath.replace("telemetry", ".client"))
    
    return cpath


class Exporter:

    def __init__(self,port):
        self.port=port
        
        
    def setup_clients(self,socketPaths,clientPaths):
        global clients

        exists = [i.clientpath for i in clients]

        for cpath,spath in zip(clientPaths,socketPaths):
            if cpath not in exists:
                clients.append(Client(cpath,spath))

    def register_and_fetch_metrics(self):
        global clients
        
        while True:
            socketPaths = parse_socketpath()
       
            clientPaths = get_clientPath(socketPaths)

            self.setup_clients(socketPaths, clientPaths)

            for client in clients:
                
                if not client.is_socket_bound(client.clientpath):
                    client.register()
                
            
                try:
                    data = client.requestMetrics()
                    self.parse_metrics_response(data)


                except Exception as e:
                    print(e)

            time.sleep(5)
        

    def start_http(self):
        start_http_server(self.port)

    

    
    def parse_metrics_response(self, response):
        metrics_data = json.loads(response)
        prefix = METRICS_PORT_PREFIX
        

        stats=metrics_data['data'][0]['stats']

        podname= metrics_data['data'][0]['podName'] 
        pciaddress= metrics_data['data'][0]['pci_address'] 
        namespace = metrics_data['data'][0]['namespace'] 
        nodename = getNodeName()
        for stat in stats:
            full_metric_name = prefix + stat['name']
            metric_key = ".".join([podname,pciaddress,full_metric_name])
            
            # if full_metric_name not in self.metrics:
              
            metrics[metric_key] = metric.labels(podname, pciaddress, namespace, full_metric_name, nodename).set(stat['value'])
            metrics[metric_key]=stat['value']
    

    def collect(self):
        with self.metrics_lock:
            for metric in self.metrics.values():
                yield metric
    


    
class Socket:

    def __init__(self):
        self.send_fd = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.recv_fd = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.client_fd = None
        

    def __del__(self):
        try:
            self.send_fd.close()
            self.recv_fd.close()
            self.client_fd.close()
        except:
            raise
            print("Error - Sockets could not be closed")

class Client:

    def __init__(self,clientpath,socketpath): # Creates a client instance
        self.socket = Socket()
        self.clientpath = clientpath  
        self.socketpath = socketpath   
        


    def __del__(self):
        try:
            self.unregister()
        except:
            raise
            print("Error - Client could not be destroyed")
    

    def is_socket_bound(self,cpath):
        return os.path.exists(cpath)


    def register(self): # Connects a client to DPDK-instance

        if os.path.exists(self.clientpath):
            os.unlink(self.clientpath)
        while True:
            try:

                self.socket.recv_fd.bind(self.clientpath)
                break
            except socket.error as msg:
                print ("Error - Socket binding error: " + str(msg) + "\n")
                time.sleep(5)
        self.socket.recv_fd.settimeout(2)
        self.socket.send_fd.connect(self.socketpath)
        JSON = (API_REG + self.clientpath + "\"}}")
        self.socket.send_fd.sendall(JSON.encode())

        self.socket.recv_fd.listen(1)
        self.socket.client_fd = self.socket.recv_fd.accept()[0]

    def is_socket_connected(self):
        try:
        # The `send` method is used to test the socket connection
            self.socket.client_fd.send(b'')
            return True
        except socket.error:
            return False
    
    def unregister(self): # Unregister a given client

        try:
            self.socket.client_fd.send((API_UNREG + self.clientpath + "\"}}").encode())
        finally:
            try:    
                del self.socket

                os.unlink(self.clientpath)
                os.unlink(self.socketpath)
                clients.remove(self)

            except Exception as e:
                pass
                print(e)

    def requestMetrics(self): # Requests metrics for given client
        try:
            self.socket.client_fd.send(METRICS_REQ.encode())
            data = self.socket.client_fd.recv(BUFFER_SIZE).decode()
            return data
        except Exception as e:
            print(e)
            self.unregister()
            
    
if __name__ == "__main__":

    port=8000

    exporter=Exporter(port)
    exporter.start_http()
    exporter.register_and_fetch_metrics()
