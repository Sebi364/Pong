#!/usr/bin/python
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame.math import Vector2
import socket
import threading
from time import time
from librarys import interpol, pos_filter
import json
from pygame import mixer
import platform

#----------------------------------------------------------------------------------------------------------#

WINDOW_RESOLUTION = Vector2(1920,1080)

SERVER_HOST = "sebi364.xyz"
#SERVER_HOST = "127.0.0.1"
SERVER_PORT = 6969

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

MENUE_FONT_SIZE = 40
COUNTER_FONT_SIZE = 140
WAIT_FONT_SIZE = 65

DEBUG_DRAWINGS = False

KONAMI_CODE = ["UP", "UP", "DOWN", "DOWN", "LEFT", "RIGHT", "LEFT", "RIGHT", "B", "A", "START"]

MUSIC_FADE_TIME = 3000

INTERPOLATION = True
POSITION_FILTER = True

#----------------------------------------------------------------------------------------------------------#

paddle_height = 100
paddle_active = False

running = True
game_running = False

theme = "2077"
theme_loadet = False

click = False
mouse_button_down = False

konami_enabled = False
input_history = []

time_offset = 0

#----------------------------------------------------------------------------------------------------------#

class Ball():
    def __init__(self) -> None:
        # Standard ball Pos
        self.relative_pos = Vector2(0.5, 0.5)

        # Variabels for interpolation
        self.speed = 0.2
        self.vector = Vector2(1,0)
        self.col_time = time()
        self.col_pos = Vector2(0.5, 0.5)

        # Field variabels
        self.field_offset = Vector2(80, 80)
        self.field_width = 1720
        self.field_height = 880

        self.flipped = False

        self.decal = None

    def update_pos(self, posX, posY):
        self.relative_pos = Vector2(float(posX), float(posY))
    
    def get_pos(self):
        if INTERPOLATION:
            vector_length = self.speed * (time() - self.col_time)
            relative_pos = self.col_pos + self.vector.clamp_magnitude(vector_length, vector_length)
        
        else:
            relative_pos = self.relative_pos
        
        if POSITION_FILTER:
            relative_pos = pos_filter.pos(relative_pos)

        if self.flipped:
            relative_x, relative_y = self.relative_pos.y, 1 - self.relative_pos.x

        else:
            relative_x, relative_y = self.relative_pos.x, self.relative_pos.y

        pos_X = relative_x * self.field_width + self.field_offset.x
        pos_Y = relative_y * self.field_height + self.field_offset.y

        pos = Vector2(pos_X, pos_Y)
        return(pos)

    def draw(self, screen):

        pos = self.get_pos()

        if DEBUG_DRAWINGS == False and theme_loadet == True:
            screen.blit(self.decal, pos)

        else:
            pygame.draw.circle(screen, "Black", pos, 40)

#---------------------------------------#

class Radio():
    def __init__(self):
        self.sounds = {

        }

        self.playing = False
    
    def play_music(self, name):
        mixer.music.load(self.sounds[name])
        mixer.music.play(-1, 0, MUSIC_FADE_TIME)
        self.playing = True
    
    def play_sound(self, name):
        sound = mixer.Sound(self.sounds[name])
        sound.play()
        self.playing = True

    def fade_out(self):
        mixer.music.fadeout(MUSIC_FADE_TIME)
        self.playing = False

    def load_music(self, name, path):
        self.sounds[name] = path
    
    def load_sound(self, name, path):
        self.sounds[name] = path

#---------------------------------------#

class Enviroment():
    def __init__(self) -> None:
        self.decal = None
        self.counter_size = 0
        self.counter_font = None
        self.counter_color = "Black"
        self.counter_pos = Vector2(WINDOW_RESOLUTION.x / 2, 40)

        self.player1_score = 0
        self.player2_score = 0

    def draw(self, screen):
        if DEBUG_DRAWINGS == False and theme_loadet == True:
            screen.blit(self.decal, (0, 0))

            text = self.counter_font.render(str(f"{self.player1_score} : {self.player2_score}"), True, self.counter_color)
            textRect = text.get_rect()
            textRect.center = self.counter_pos

            screen.blit(text, textRect)

        else:
            screen.fill("White")

#---------------------------------------#

class Counter():
    def __init__(self):
        self.enabled = False
        self.target_time = 0

        self.number_height = 200
        self.number_width = 90
        self.padding = 15

        self.decals = {

        }

        for i in range(0, 10):
            img = pygame.image.load(f"ui_elements/sus_numbers/{i}.gif").convert_alpha()
            self.decals[f"decal_{i}"] = pygame.transform.scale(img, (self.number_width, self.number_height))

        self.font = pygame.font.Font("ui_elements/font.ttf", COUNTER_FONT_SIZE)

    def count(self, target_time):
        self.enabled = True
        self.target_time = target_time
    
    def draw(self, screen):
        if self.enabled:
            time_remaining = self.target_time - time() - time_offset
            if time_remaining < 0:
                self.enabled = False
            else:
                time_remaining = round(time_remaining)

                text = self.font.render(str(time_remaining), True, "Black")
                textRect = text.get_rect()
                textRect.center = (WINDOW_RESOLUTION.x / 2, WINDOW_RESOLUTION.y / 2)
                screen.blit(text, textRect)

#---------------------------------------#

class Player1():
    def __init__(self) -> None:
        self.pos1 = Vector2(0, 80)
        self.pos2 = Vector2(0, 776)

        self.relative_y = 0.5

        self.is_moving = False
        self.movement_direction = 1
        self.movement_speed = 0.2

        self.decal = None

    def update_pos(self, pos_y):
        self.relative_y = pos_y

    def update(self, delta):
        if self.is_moving and counter.enabled == False:
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
        pos = interpol.vec(self.pos1, self.pos2, self.relative_y)

        if DEBUG_DRAWINGS == False and theme_loadet == True:
            screen.blit(self.decal, pos)
        
        else:
            rect = pygame.Rect(pos.x, pos.y, 80, 184)
            pygame.draw.rect(screen, "Black", rect)

#---------------------------------------#

class Player2():
    def __init__(self):
        self.pos1 = Vector2(0, 80)
        self.pos2 = Vector2(0, 776)
        self.travel_time = 0.1
        self.start_time = time()

        self.relative1 = 0.5
        self.relative2 = 0.5

        self.decal = None

    def update_pos(self, pos):
        self.relative1 = self.relative2
        self.relative2 = float(pos)
        self.travel_time = time() - self.start_time
        self.start_time = time()
    
    def update(self, delta):
        pass
    
    def draw(self, screen):
        if INTERPOLATION:
            relative_y = interpol.num(self.relative1, self.relative2, ((time() - self.start_time) / self.travel_time))
        
        else:
            relative_y = self.relative2
        
        if POSITION_FILTER:
            relative_y = pos_filter.num(relative_y)

        pos = interpol.vec(self.pos1, self.pos2, relative_y)

        if DEBUG_DRAWINGS == False and theme_loadet == True:
            screen.blit(self.decal, pos)
        
        else:
            rect = pygame.Rect(pos.x, pos.y, 80, 184)
            pygame.draw.rect(screen, "Black", rect)

#---------------------------------------#

class NetworkConnection:
    def __init__(self) -> None:
        try:
            self.connection = socket.socket()
            self.connection.connect((SERVER_HOST, SERVER_PORT))

            self.packet_sendtime = 0

        except:
            print("Failed to connect to server")
            pygame.quit()
            quit()

    def put(self, data):
        self.connection.send(f"{data};".encode())

    def get(self):
        data = self.connection.recv(1024).decode()
        return data

    def packet_parser(self, packet):
        global game_running

        if packet[0] == "game" and packet[1] == "info" and len(packet) == 8:
            radio.play_music("background")
            player1.relative_height = float(packet[3])
            player2.relative_height = float(packet[3])

            player1.movement_speed = float(packet[4])
            player2.movement_speed = float(packet[4])

            player1.relative_y = float(packet[5])
            player2.relative_y = float(packet[6])

            ball.speed = float(packet[7])

            counter.count(float(packet[2]))

            game_running = True

        elif packet[0] == "game" and packet[1] == "state" and len(packet) == 6:
            ball.update_pos(float(packet[2]), float(packet[3]))
            player2.update_pos(float(packet[5]))

        elif packet[0] == "game" and packet[1] == "score" and len(packet) == 4:
            radio.play_sound("goal")
            player1.relative_y = 0.5
            player2.relative_y = 0.5
            ball.update_pos(float(0.5), float(0.5))

            enviroment.player1_score = int(packet[2])
            enviroment.player2_score = int(packet[3])

        elif packet[0] == "bounce" and len(packet) == 5:
            radio.play_sound("bounce")
            ball.col_time = time()
            ball.col_pos = Vector2(float(packet[1]), float(packet[2]))
            ball.vector = Vector2(float(packet[3]), float(packet[4]))
            
        elif packet[0] == "game" and packet[1] == "ended":
            game_menue.waiting = False
            radio.play_music("start_background")
            player1.relative_y = 0.5
            player2.relative_y = 0.5
            ball.update_pos(float(0.5), float(0.5))
            game_running = False

            if packet[2] == "finished":
                if packet[3] == "won":
                    print("won")

                if packet[3] == "lost":
                    print("lost")
        
        elif packet[0] == "game" and packet[1] == "pause":
            counter.count(float(packet[2]))
        
        elif packet[0] == "time_sync" and len(packet) == 2:
            travel_time = (time() - self.packet_sendtime) / 2
            time_offset = time() - float(packet[1]) - travel_time
            print(f"New time offset: {time_offset}")

    def main(self):
        data = ""
        while running:
            packet = str(self.get())

            for i in packet:
                if i != ";":
                    data += i
                else:
                    self.packet_parser(data.split(" "))
                    data = ""

#---------------------------------------#

class Sword():
    def __init__(self):
        if konami_enabled:
            pygame.mouse.set_visible(0)
        
        self.decal = pygame.transform.scale(pygame.image.load(f"ui_elements/cursor.png").convert_alpha(), (55, 55))

    def draw(self, screen):
        if konami_enabled:
            pygame.mouse.set_visible(0)
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

        self.hoversound_played = False

    def draw(self, screen):
        rect = pygame.Rect(self.pos_X - self.hover_adjust, self.pos_Y - self.hover_adjust ,BUTTON_WIDTH + self.hover_adjust * 2 ,BUTTON_HEIGHT + self.hover_adjust * 2)
        
        color = interpol.col(BUTTON_COLOR, BUTTON_COLOR_H, self.hover_percentage)
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
                radio.play_sound("ui_confirm")
                game_menue.on_pressed(self.id)
                click = False
            
            self.mouse_hovering = True
        
        else:
            self.mouse_hovering = False
        
        if self.mouse_hovering:
            if self.hover_adjust < BUTTON_ENLARGE_H:
                if not self.hoversound_played:
                    radio.play_sound("ui_hover")
                    self.hoversound_played = True

                self.hover_adjust += (BUTTON_ENLARGE_H / BUTTON_ADJUST_TIME_H * delta)
                self.hover_percentage = 1 / BUTTON_ENLARGE_H * self.hover_adjust
        
        else:
            if self.hover_adjust > 0:
                self.hoversound_played = False
                self.hover_adjust -= (BUTTON_ENLARGE_H / BUTTON_ADJUST_TIME_H * delta)
                self.hover_percentage = 1 / BUTTON_ENLARGE_H * self.hover_adjust

#---------------------------------------#

class Menue():
    def __init__(self):
        self.background = pygame.image.load(f"ui_elements/background.png").convert_alpha()

        self.waiting = False

        self.font = self.font = pygame.font.Font("ui_elements/font.ttf", WAIT_FONT_SIZE)
        
        self.buttons = [
            Button("Join", 0, 3, "join-button"),
            Button("Test", 1, 3, "test-button"),
            Button("Exit", 2, 3, "exit-button")
        ]

    def draw(self, screen):
        if game_running == False:
            screen.blit(self.background, (0, 0))
            if self.waiting:
                text = self.font.render("Loading...", True, "White")
                textRect = text.get_rect()
                textRect.center = (WINDOW_RESOLUTION.x / 2, WINDOW_RESOLUTION.y / 2)
                screen.blit(text, textRect)

            else:
                for i in self.buttons:
                    i.draw(screen)
    
    def on_pressed(self, button_name):
        if button_name == "join-button":
            network_handler.put("player join open")
            self.waiting = True
        
        if button_name == "exit-button":
            network_handler.put("player exit")
            pygame.quit()
            quit()

    def update(self, delta):
        if game_running == False and self.waiting == False:
            for i in self.buttons:
                i.update(delta)

#----------------------------------------------------------------------------------------------------------#

def draw(screen):
    enviroment.draw(screen)
    player1.draw(screen)
    player2.draw(screen)
    ball.draw(screen)

    counter.draw(screen)
    game_menue.draw(screen)

    cursor.draw(screen)
    
    pygame.display.update()

#---------------------------------------#

def sync_time():
    network_handler.packet_sendtime = time()
    network_handler.put("player time_sync")

#---------------------------------------#

def konami_watcher():
    global input_history
    global konami_enabled

    if konami_enabled == False:
        if input_history[-11:] == KONAMI_CODE:
            konami_enabled = True
        
        if len(input_history) > 15:
            input_history = input_history[-12:]

#---------------------------------------#

def event_handler():
    global running
    global mouse_button_down
    global click
    global input_history

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            network_handler.put("player exit")
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP or event.key == pygame.K_LEFT or event.key == pygame.K_a:
                if game_running:
                    player1.start_moving(-1)

            if event.key == pygame.K_s or event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                if game_running:
                    player1.start_moving(1)
            
            if event.key == pygame.K_UP:
                input_history.append("UP")

            elif event.key == pygame.K_DOWN:
                input_history.append("DOWN")
            
            elif event.key == pygame.K_LEFT:
                input_history.append("LEFT")
            
            elif event.key == pygame.K_RIGHT:
                input_history.append("RIGHT")
            
            elif event.key == pygame.K_a:
                input_history.append("A")
            
            elif event.key == pygame.K_b:
                input_history.append("B")
            
            elif event.key == pygame.K_RETURN:
                input_history.append("START")
            
            konami_watcher()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w or event.key == pygame.K_UP or event.key == pygame.K_LEFT or event.key == pygame.K_a:
                if game_running:
                    player1.stop_moving()

            if event.key == pygame.K_s or event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT or event.key == pygame.K_d:
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
    radio.play_music("start_background")

    while running:
        delta = time() - last_time
        last_time = time()

        player1.update(delta)
        player2.update(delta)
        game_menue.update(delta)

        draw(screen)
        event_handler()

#---------------------------------------#

def sound_loader(theme):
    try:
        config_file = open(f"themes/" + theme + "/sounds.json","r")
        settings = json.load(config_file)
        radio.load_music("background", "themes/" + theme + "/" + settings["background-music"])
        radio.load_sound("goal", "themes/" + theme + "/" + settings["goal"])
        radio.load_sound("bounce", "themes/" + theme + "/" + settings["bounce"])
        radio.load_music("start_background", "ui_elements/background.mp3")
        radio.load_sound("ui_confirm", "ui_elements/confirm.mp3")
        radio.load_sound("ui_hover", "ui_elements/hover.mp3")

    except Exception as e:
        print(e)

#---------------------------------------#

def theme_loader(theme):
    global theme_loadet

    try:
        config_file = open(f"themes/{theme}/theme.json","r")
        settings = json.load(config_file)
        
        pygame.display.set_caption("Pong! " + settings["name"])

        ball.decal = pygame.image.load("themes/" + theme + "/" + settings["ball"]["decal"]).convert_alpha()
        enviroment.decal = pygame.image.load("themes/" + theme + "/" + settings["field"]["decal"]).convert_alpha()
        player1.decal = pygame.image.load("themes/" + theme + "/" + settings["player1"]["decal"]).convert_alpha()
        player2.decal = pygame.image.load("themes/" + theme + "/" + settings["player2"]["decal"]).convert_alpha()

        player1.pos1 = Vector2(settings["player1"]["pos1"])
        player1.pos2 = Vector2(settings["player1"]["pos2"])
        player2.pos1 = Vector2(settings["player2"]["pos1"])
        player2.pos2 = Vector2(settings["player2"]["pos2"])

        ball.field_offset = Vector2(settings["field"]["pos"])
        ball.field_height = float(settings["field"]["height"])
        ball.field_width = float(settings["field"]["width"])

        enviroment.counter_color = settings["score"]["color"]
        enviroment.counter_size = settings["score"]["font_size"]
        enviroment.counter_pos = Vector2(settings["score"]["pos"])
        enviroment.counter_font = pygame.font.Font(("themes/" + theme + "/" + settings["score"]["font"]), settings["score"]["font_size"])

        if settings["field"]["type"] == "vertical":
            ball.flipped = True
        else:
            ball.flipped = False

        theme_loadet = True

    except Exception as e:
        print(f"Error while loading config file: {e}")
        pass

#----------------------------------------------------------------------------------------------------------#

pygame.init()
screen = pygame.display.set_mode((WINDOW_RESOLUTION.x,WINDOW_RESOLUTION.y))
menue_font = pygame.font.Font("ui_elements/font.ttf", MENUE_FONT_SIZE)
pygame.display.set_caption("Pong!")

mixer.init()

if platform.system() != 'Linux':
    print("Your OS isn't supported, proceed with caution.")

#----------------------------------------------------------------------------------------------------------#

enviroment = Enviroment()
ball = Ball()
network_handler = NetworkConnection()
player1 = Player1()
player2 = Player2()
game_menue = Menue()
cursor = Sword()
counter = Counter()
radio = Radio()

#----------------------------------------------------------------------------------------------------------#

sync_time()
theme_loader(theme)
sound_loader(theme)

threading._start_new_thread(network_handler.main, ())
main()