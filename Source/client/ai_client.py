#!/usr/bin/python
import os
import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 6969

try:
    connection = socket.socket()
    connection.connect((SERVER_HOST, SERVER_PORT))

except:
    print("Failed to connect to server")
    quit()

def put(data):
    connection.send(f"{data}\n".encode())

def get():
    data = connection.recv(1024).decode()
    return data

put("player join open")

while True:
    packet = get()
    packet = packet.split("\n")
    for i in packet:
        i = i.split(" ")
        if len(i) == 6:
            put(f"game moved {i[3]}")