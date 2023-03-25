#!/usr/bin/python
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame.math import Vector2
import socket
import threading
from time import time

#window
RESOLUTION = (700,500)
#network
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 6969
#ball
BALL_RADIUS = 40
BALL_COLOR = "Magenta"
#field
BORDER_WIDTH = 80
COLLISION_DISTANCE = BORDER_WIDTH + BALL_RADIUS
#paddle
PADDLE_HEIGHT = 200

#-------------------------------------------------------------------------------------------------------------#

class Ball:
    def __init__(self, radius, color, pos) -> None:
        self.pos = pos
        self.color = color
        self.radius = radius

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.pos, self.radius)

class Player:
    def __init__(self, pos_x) -> None:
        self.min_y = BORDER_WIDTH
        self.max_y = RESOLUTION[1] - BORDER_WIDTH - PADDLE_HEIGHT

        self.range = self.max_y - self.min_y
        self.pos_y = 1
        self.pos_x = pos_x

        self.width = BORDER_WIDTH
        self.height = PADDLE_HEIGHT
        self.speed = 50

    def draw(self, screen):
        position = self.min_y + (self.pos_y * self.range)
        
        rect = pygame.Rect(self.pos_x, position, self.width, self.height)

        pygame.draw.rect(screen, "Black", rect, 10)

    def update_info(self, height, speed):
        self.height = height
        self.min_y = BORDER_WIDTH
        self.max_y = RESOLUTION[1] - BORDER_WIDTH - height

        self.range = self.max_y - self.min_y
        self.speed = speed

#-------------------------------------------------------------------------------------------------------------#

def draw(screen):
    screen.fill("White")
    ball.draw(screen)
    player1.draw(screen)
    player2.draw(screen)
    pygame.display.update()

def put(data):
    connection.send(f"{data}\n".encode())

def get():
    data = connection.recv(1024).decode()
    return data

def network_parser():
    global ball
    global player1
    global player2
    
    global running
    put("player join open")
    while running:
        data = get()
        data = data.split("\n")
        for i in data:
            i = i.split(" ")
            if len(i) != 1:
                try:
                    if i[0] == "game":
                        if i[1] == "state":
                            if len(i) == 6:
                                ball.pos = Vector2(int(float(i[2]) * (RESOLUTION[0] - COLLISION_DISTANCE * 2)) + COLLISION_DISTANCE,
                                                    int(float(i[3]) * (RESOLUTION[1] - COLLISION_DISTANCE * 2)) + COLLISION_DISTANCE)
                                player2.pos_y = float(i[5])
                        
                        if i[1] == "info":
                            player1.update_info(int(float(i[3]) * RESOLUTION[1]), int(float(i[4]) * RESOLUTION[1]))
                            player2.update_info(int(float(i[3]) * RESOLUTION[1]), int(float(i[4]) * RESOLUTION[1]))

                except Exception as e:
                    print(e)

def main():
    last_time = time()
    global running
    while running:
        delta = last_time - time()
        last_time = time()

        draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_w] or pressed[pygame.K_UP]:
                put(f"game moved {player1.pos_y}")
                player1.pos_y += player1.speed * delta

            if pressed[pygame.K_s] or pressed[pygame.K_DOWN]:
                put(f"game moved {player1.pos_y}")
                player1.pos_y -= player1.speed * delta
            

#-------------------------------------------------------------------------------------------------------------#

try:
    connection = socket.socket()
    connection.connect((SERVER_HOST, SERVER_PORT))

except:
    print("Failed to connect to server")
    quit()

pygame.init()
screen = pygame.display.set_mode(RESOLUTION)

ball = Ball(BALL_RADIUS, BALL_COLOR, Vector2(RESOLUTION[0] / 2, RESOLUTION[1] / 2))
player1 = Player(0)
player2 = Player(RESOLUTION[0] - BORDER_WIDTH)

running = True
threading._start_new_thread(network_parser, ())
main()