#!/usr/bin/python
import os
import socket

SERVER_HOST = "sebi364.xyz"
#SERVER_HOST = "127.0.0.1"
SERVER_PORT = 6969

try:
    connection = socket.socket()
    connection.connect((SERVER_HOST, SERVER_PORT))

except:
    print("Failed to connect to server")
    quit()

def put(data):
    connection.send(f"{data};".encode())

def get():
    data = connection.recv(1024).decode()
    return data

put("player join open")

while True:
    packet = get()
    packet = packet.replace(";", "").split(" ")
    if len(packet) == 6:
        put(f"game moved {packet[3]}")