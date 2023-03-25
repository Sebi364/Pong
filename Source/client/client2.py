#!/usr/bin/python
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame.math import Vector2
import socket
import threading
from time import time
from librarys import interpol

#----------------------------------------------------------------------------------------------------------#

WINDOW_RESOLUTION = Vector2(1920,1080)
WINDOW_COLOR = "White"

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 6969

BALL_RADIUS = 20
BALL_COLOR = "Magenta"

BORDER_WIDTH = 80

BUTTON_HEIGHT = 100
BUTTON_WIDTH = 400
BUTTON_BORDER_WIDTH = 5
BUTTON_BORDER_RADIUS = 20
BUTTON_PADDING = 20
BUTTON_COLOR = (170, 170, 170)
BUTTON_COLOR_H = (255, 255, 255)
BUTTON_ENLARGE_H = 5
BUTTON_BORDER_WIDTH_H = 7
BUTTON_BORDER_RADIUS_H = 20
BUTTON_ADJUST_TIME_H = 0.1

SWORD_CURSOR = False
SUS_NUMBERS = False

PADDLE_COLOR = "Black"

MENUE_FONT_SIZE = 40
SCORE_FONT_SIZE = 40
COUNTER_FONT_SIZE = 140

DEBUG_DRAWINGS = False

#----------------------------------------------------------------------------------------------------------#

paddle_height = 100
paddle_active = False

running = True
game_running = False

theme = "gate"

click = False
mouse_button_down = False

#----------------------------------------------------------------------------------------------------------#

class Ball():
    def __init__(self) -> None:
        self.relative_pos = Vector2(0.5, 0.5)
        self.decal = pygame.image.load(f"themes/{theme}/ball.png").convert_alpha()

    def update_pos(self, posX, posY):
        self.relative_pos = Vector2(float(posX), float(posY))

    def draw(self, screen):
        collision_distance = BORDER_WIDTH + BALL_RADIUS
        absolute_x = (int(float(self.relative_pos.x) * (WINDOW_RESOLUTION.x - collision_distance * 2)) + collision_distance)
        absolute_y = (int(float(self.relative_pos.y) * (WINDOW_RESOLUTION.y - collision_distance * 2)) + collision_distance)

        if DEBUG_DRAWINGS == False:
            screen.blit(self.decal, (absolute_x - BALL_RADIUS, absolute_y - BALL_RADIUS))

        else:
            pygame.draw.circle(screen, BALL_COLOR, (absolute_x, absolute_y), BALL_RADIUS)

#---------------------------------------#

class Enviroment():
    def __init__(self) -> None:
        self.background_decal = pygame.image.load(f"themes/{theme}/background.png").convert_alpha()
        self.border_decal = pygame.image.load(f"themes/{theme}/border.png").convert_alpha()
        self.counter_font = pygame.font.Font("ui_elements/font.ttf", SCORE_FONT_SIZE)

        self.player1_score = 0
        self.player2_score = 0


    def draw(self, screen):
        if DEBUG_DRAWINGS == False:
            screen.blit(self.background_decal, (0, 0))
            screen.blit(self.border_decal, (0, 0))

            text = self.counter_font.render(str(f"{self.player1_score} : {self.player2_score}"), True, "White")
            textRect = text.get_rect()
            textRect.center = (WINDOW_RESOLUTION.x / 2, BORDER_WIDTH / 2)

            screen.blit(text, textRect)

        else:
            screen.fill(WINDOW_COLOR)

#---------------------------------------#

class Counter():
    def __init__(self):
        self.enabled = False
        self.target_time = 0

        if SUS_NUMBERS:
            self.number_height = 200
            self.number_width = 90
            self.padding = 15

            self.decals = {

            }

            for i in range(0, 10):
                img = pygame.image.load(f"ui_elements/sus_numbers/{i}.gif").convert_alpha()
                self.decals[f"decal_{i}"] = pygame.transform.scale(img, (self.number_width, self.number_height))

        else:
            self.font = pygame.font.Font("ui_elements/font.ttf", COUNTER_FONT_SIZE)

    def count(self, target_time):
        self.enabled = True
        self.target_time = target_time
    
    def draw(self, screen):
        if self.enabled:
            time_remaining = self.target_time - time()
            if time_remaining < 0:
                self.enabled = False
            else:
                time_remaining = round(time_remaining)

                if SUS_NUMBERS:
                    digits = str(time_remaining)

                    total_width = ((len(digits) * self.number_width) + ((len(digits) - 1) * self.padding))

                    digit_pos = 0

                    for i in digits:
                        xpos = (digit_pos * (self.number_width + self.padding)) + ((WINDOW_RESOLUTION.x / 2) - (total_width / 2))
                        ypos = ((WINDOW_RESOLUTION.y / 2) - (self.number_height / 2))
                        screen.blit(self.decals[f"decal_{i}"], (xpos, ypos))
                        digit_pos += 1

                else:
                    text = self.font.render(str(time_remaining), True, "Black")
                    textRect = text.get_rect()
                    textRect.center = (WINDOW_RESOLUTION.x / 2, WINDOW_RESOLUTION.y / 2)
                    screen.blit(text, textRect)

#---------------------------------------#

class Player():
    def __init__(self, absolute_x) -> None:
        self.absolute_x = absolute_x
        self.relative_y = 0.5
        self.relative_height = 0.2

        self.movement_range = (WINDOW_RESOLUTION[1] - (BORDER_WIDTH * 2))

        self.is_moving = False
        self.movement_direction = 1
        self.movement_speed = 0.2

        self.decal = pygame.image.load(f"themes/{theme}/paddle.png").convert_alpha()

    def update_pos(self, pos_y):
        self.relative_y = pos_y

    def update(self, delta):
        if self.is_moving:
            self.relative_y += delta * self.movement_direction
            if self.relative_y > 1:
                self.relative_y = 1

            if self.relative_y < 0:
                self.relative_y = 0

            network_handler.put(f"game moved {self.relative_y}")

    def start_moving(self, direction):
        self.is_moving = True
        self.movement_direction = direction

    def stop_moving(self):
        self.is_moving = False

    def draw(self, screen):
        absolute_height = self.relative_height * self.movement_range
        absolute_y = (BORDER_WIDTH + ((self.movement_range - absolute_height) * self.relative_y))

        if DEBUG_DRAWINGS == False:
            screen.blit(self.decal, (self.absolute_x, absolute_y))
        
        else:
            rect = pygame.Rect(self.absolute_x, absolute_y, BORDER_WIDTH, (self.relative_height * self.movement_range))
            pygame.draw.rect(screen, PADDLE_COLOR, rect)

#---------------------------------------#

class NetworkConnection:
    def __init__(self) -> None:
        try:
            self.connection = socket.socket()
            self.connection.connect((SERVER_HOST, SERVER_PORT))

        except:
            print("Failed to connect to server")
            pygame.quit()
            quit()

    def put(self, data):
        self.connection.send(f"{data}\n".encode())

    def get(self):
        data = self.connection.recv(1024).decode()
        return data

    def packet_parser(self, packet):
        global game_running

        if packet[0] == "game" and packet[1] == "info" and len(packet) == 7:
            player1.relative_height = float(packet[3])
            player2.relative_height = float(packet[3])

            player1.movement_speed = float(packet[4])
            player2.movement_speed = float(packet[4])

            player1.relative_y = float(packet[5])
            player2.relative_y = float(packet[6])

            counter.count(float(packet[2]))

            game_running = True

        if packet[0] == "game" and packet[1] == "state" and len(packet) == 6:
            ball.update_pos(float(packet[2]), float(packet[3]))
            player2.update_pos(float(packet[5]))

        if packet[0] == "game" and packet[1] == "score" and len(packet) == 4:
            player1.relative_y = 0.5
            player2.relative_y = 0.5
            ball.update_pos(float(0.5), float(0.5))

            enviroment.player1_score = int(packet[2])
            enviroment.player2_score = int(packet[3])
        
        if packet[0] == "game" and packet[1] == "ended":
            player1.relative_y = 0.5
            player2.relative_y = 0.5
            ball.update_pos(float(0.5), float(0.5))
            game_running = False

    def main(self):
        while running:
            data = self.get()
            data = data.split("\n")
            for i in data:
                i = i.split(" ")
                if len(i) != 0:
                    self.packet_parser(i)

#---------------------------------------#

class Sword:
    def __init__(self):
        if SWORD_CURSOR:
            pygame.mouse.set_visible(0)

        self.decal = pygame.transform.scale(pygame.image.load(f"ui_elements/cursor.png").convert_alpha(), (55, 55))

    def draw(self, screen):
        if SWORD_CURSOR:
            screen.blit(self.decal, (pygame.mouse.get_pos()))

#---------------------------------------#

class Button():
    def __init__(self, content, button_pos, total, button_id):
        self.content = content
        self.button_pos = button_pos
        self.total_buttons = total
        self.id = button_id

        self.pos_X = ((WINDOW_RESOLUTION.x / 2) - (BUTTON_WIDTH / 2))
        self.total_Y = ((self.total_buttons * BUTTON_HEIGHT) + ((self.total_buttons - 1)  * BUTTON_PADDING))
        self.start_Y = ((WINDOW_RESOLUTION.y / 2) - (self.total_Y / 2))
        self.pos_Y = self.start_Y + (button_pos * (BUTTON_HEIGHT + BUTTON_PADDING))

        self.textpos_Y = self.pos_Y +( BUTTON_HEIGHT / 2)
        self.textpos_X = self.pos_X +( BUTTON_WIDTH / 2)
        
        self.mouse_hovering = True

        self.hover_adjust = 0
        self.hover_percentage = 0

    def draw(self, screen):
        rect = pygame.Rect(self.pos_X - self.hover_adjust, self.pos_Y - self.hover_adjust ,BUTTON_WIDTH + self.hover_adjust * 2 ,BUTTON_HEIGHT + self.hover_adjust * 2)
        
        color = interpol.color(BUTTON_COLOR, BUTTON_COLOR_H, self.hover_percentage)
        width = int(interpol.num(BUTTON_BORDER_WIDTH, BUTTON_BORDER_WIDTH_H, self.hover_percentage))
        radius = int(interpol.num(BUTTON_BORDER_RADIUS, BUTTON_BORDER_RADIUS_H, self.hover_percentage))

        pygame.draw.rect(screen, color, rect, width, radius)

        text = menue_font.render(self.content, True, "White")
        textRect = text.get_rect()
        textRect.center = (self.textpos_X, self.textpos_Y)

        screen.blit(text, textRect)

    def update(self, delta):
        global click

        rect = pygame.Rect(self.pos_X,self.pos_Y,BUTTON_WIDTH,BUTTON_HEIGHT)
        
        if rect.collidepoint(pygame.mouse.get_pos()):
            if click:
                game_menue.on_pressed(self.id)
                click = False
            
            self.mouse_hovering = True
        
        else:
            self.mouse_hovering = False
        
        if self.mouse_hovering:
            if self.hover_adjust < BUTTON_ENLARGE_H:
                self.hover_adjust += (BUTTON_ENLARGE_H / BUTTON_ADJUST_TIME_H * delta)
                self.hover_percentage = 1 / BUTTON_ENLARGE_H * self.hover_adjust
        
        else:
            if self.hover_adjust > 0:
                self.hover_adjust -= (BUTTON_ENLARGE_H / BUTTON_ADJUST_TIME_H * delta)
                self.hover_percentage = 1 / BUTTON_ENLARGE_H * self.hover_adjust

#---------------------------------------#

class Menue():
    def __init__(self):
        self.background = pygame.image.load(f"ui_elements/background.png").convert_alpha()
        
        self.buttons = [
            Button("Join", 0, 3, "join-button"),
            Button("Test", 1, 3, "test-button"),
            Button("Exit", 2, 3, "exit-button")
        ]

    def draw(self, screen):
        if game_running == False:
            screen.blit(self.background, (0, 0))
            for i in self.buttons:
                i.draw(screen)
    
    def on_pressed(self, button_name):
        if button_name == "join-button":
            network_handler.put("player join open")
        
        if button_name == "exit-button":
            network_handler.put("player exit")
            pygame.quit()
            quit()

    def update(self, delta):
        if game_running == False:
            for i in self.buttons:
                i.update(delta)

#----------------------------------------------------------------------------------------------------------#

def draw(screen):
    enviroment.draw(screen)
    player1.draw(screen)
    player2.draw(screen)
    ball.draw(screen)

    game_menue.draw(screen)
    counter.draw(screen)

    cursor.draw(screen)
    
    pygame.display.update()

#---------------------------------------#

def event_handler():
    global running
    global mouse_button_down
    global click

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            network_handler.put("player exit")
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                if game_running:
                    player1.start_moving(-1)

            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                if game_running:
                    player1.start_moving(1)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                if game_running:
                    player1.stop_moving()

            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                if game_running:
                    player1.stop_moving()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if mouse_button_down == True:
                pass

            else:
                mouse_button_down = True
                click = True
        
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_button_down = False
            click = False

#---------------------------------------#

def main():
    last_time = time()

    while running:
        delta = time() - last_time
        last_time = time()

        player1.update(delta)
        player2.update(delta)
        game_menue.update(delta)

        draw(screen)
        event_handler()

#----------------------------------------------------------------------------------------------------------#

pygame.init()
screen = pygame.display.set_mode((WINDOW_RESOLUTION.x,WINDOW_RESOLUTION.y))
menue_font = pygame.font.Font("ui_elements/font.ttf", MENUE_FONT_SIZE)

#----------------------------------------------------------------------------------------------------------#

enviroment = Enviroment()
ball = Ball()
network_handler = NetworkConnection()
player1 = Player(0)
player2 = Player(WINDOW_RESOLUTION[0] - BORDER_WIDTH)
game_menue = Menue()
cursor = Sword()
counter = Counter()

#----------------------------------------------------------------------------------------------------------#

threading._start_new_thread(network_handler.main, ())
main()