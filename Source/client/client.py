#!/usr/bin/python
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import socket
import threading

RESOLUTION = (720,540)
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 6969

BORDER_DISTANCE = 40
#-------------------------------------------------------------------------------------------------------------#

class Ball:
    def __init__(self, screen) -> None:
        self.posX = 0
        self.posY = 0
        self.color = "Black"
        self.radius = 20

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.posX, self.posY), self.radius)

    def update(self, pos):
        pass

#-------------------------------------------------------------------------------------------------------------#

def draw(screen):
    screen.fill("White")
    ball.draw(screen)
    pygame.display.update()

def network_parser(connection):
    global ball

    def put(data):
        connection.send(f"{data}\n".encode())

    def get():
        data = connection.recv(1024).decode()
        return data
    
    global running
    put("player join open")
    while running:
        data = get()
        data = data.split("\n")
        for i in data:
            i = i.split(" ")
            print(i)
            if len(i) != 1:
                try:
                    if i[0] == "game":
                        if i[1] == "state":
                            if len(i) == 6:
                                ball.posX = int(float(i[2]) * (RESOLUTION[0] - BORDER_DISTANCE * 2)) + BORDER_DISTANCE
                                ball.posY = int(float(i[3]) * (RESOLUTION[1] - BORDER_DISTANCE * 2)) + BORDER_DISTANCE

                except Exception as e:
                    print(e)

def main():
    global running
    while running:
        draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

#-------------------------------------------------------------------------------------------------------------#

try:
    connection = socket.socket()
    connection.connect((SERVER_HOST, SERVER_PORT))

except:
    print("Failed to connect to server")
    quit()

pygame.init()
screen = pygame.display.set_mode(RESOLUTION)

ball = Ball(screen)

running = True
threading._start_new_thread(network_parser, (connection,))
main()