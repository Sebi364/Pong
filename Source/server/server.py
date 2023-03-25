#!/bin/python3
import socket
import threading
from time import sleep, time
from datetime import datetime
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame.math import Vector2
from random import randrange

#----------------------------------------------------------------------------------------------------------#

SERVER_PORT = 6969
SERVER_HOST = ''
LOG_TO_FILE = False

#----------------------------------------------------------------------------------------------------------#

afk_players = {

}

waitlist = {

}

running_games = {

}

#----------------------------------------------------------------------------------------------------------#

class Player:
    def __init__(self, connection, ip, player_id):
        self.name = None
        self.color = None
        self.connection = connection
        self.running = True
        self.ip = ip
        self.player_id = player_id
        self.match_id = 0
        self.match = None
        self.last_heartbeat = 0
        self.running = True

    def __repr__(self):
        return(str(self.player_id))

    def put(self, content):
        try:
            self.connection.send(f"{content}\n".encode())

        except:
            printlog(f"Player {self.player_id} disconnected from the game.","red")
            self.running = False
            self.exit()

    def talk_to_player(self):
        printlog(f"Player {self.player_id} from {self.ip[0]} joined the game", "green")

        while self.running:
            try:
                data = self.connection.recv(1024).decode()
                data = data.split("\n")
            except:
                printlog(f"Player {self.player_id} disconnected from the game.","red")
                self.exit()
                break

            for i in data:
                command = i.split(" ")
                if command[0] == "player" and command[1] == "set":
                    if command[2] == "color":
                        self.color = command[3]
                    
                    if command[2] == "name":
                        self.name = command[3]

                if command[0] == "player" and command[1] == "exit":
                    printlog(f"Player {self.player_id} from {self.ip[0]} left the game", "orange")
                    self.exit()
                
                if command[0] == "player" and command[1] == "join":
                    if command[2] == "open":
                        if self.match_id == 0:
                            move_to_waitlist(self.player_id)
                            self.put("player entered waitlist")
                
                if command[0] == "game":
                    if self.match_id != 0:
                        self.match.network_handler(command[1:], self.player_id)

    def close_match(self, reason):
        self.match = None
        self.match_id = 0
        self.put(f"game ended {reason}")

    def heartbeat(self):
        while self.running:
            self.put("player ping")
            sleep(1)

    def join_match(self, match_id):
        self.match_id = match_id
        self.match = running_games[self.match_id]
        self.put(f"game started")

    def exit(self):
        self.running = False
        if self.match_id != 0:
            self.match.exit(self.player_id)

        try:
            remove_from_waitlist(self.player_id)
            printlog(f"Player 1000 removed from waiting list because he left.", "orange")

        except:
            pass

        self.connection.close()
        self.running = False

#---------------------------------------#

class Match:
    def __init__(self, player1, player2, match_id):
        # players
        self.player1 = player1
        self.player2 = player2

        # Match info
        self.match_id = match_id
        self.running = True

        # Game Variables
        self.ball_vector = Vector2(1,2).normalize()
        self.ball_pos = Vector2(0.5,0.5)
        self.ball_speed = 0.5 # per second

        self.player_width = 0.2
        self.player_speed = 0.2

        self.player1_pos = 0.5
        self.player2_pos = 0.5

        self.player1_score = 0
        self.player2_score = 0

    def __repr__(self):
        return str(f"{self.player1.player_id},{self.player2.player_id}")
    
    def broadcast(self, content):
        self.player1.put(content)
        self.player2.put(content)
    
    def push(self, content, player):
        player.put(content)

    def exit(self, player_id):
        self.running = False
        printlog(f"Match {self.match_id} ended, because player {player_id} left the game","orange")
        if self.player1.player_id == player_id:
            rescue_player(self.match_id, self.player2)
            self.player2.close_match("enemy_left")

        else:
            rescue_player(self.match_id, self.player1)
            self.player1.close_match("enemy_left")

        remove_match(self.match_id)

    def network_handler(self, command, sender):
        if command[0] == "moved":
            if sender == self.player1.player_id:
                self.player1_pos = float(command[1])
            else:
                self.player2_pos = float(command[1])

    def check_collision(self, pos):
        pos2 = pos * (1 - self.player_width) + self.player_width / 2

        if self.ball_pos.y < pos2 - self.player_width / 2 or self.ball_pos.y > pos2 + self.player_width / 2:
            return(True)
        else:
            return(False)

    def game(self):
        start_time = int(time()) + 12
        self.push(f"game info {start_time} {self.player_width} {self.player_speed} {self.player1_pos} {self.player2_pos}", self.player1)
        self.push(f"game info {start_time} {self.player_width} {self.player_speed} {self.player2_pos} {self.player1_pos}", self.player2)

        while self.running:
            if start_time < time():
                last_time = time()
                while self.running:
                    delta = time() - last_time
                    last_time = time()
                    sleep(0.01)
                    scored = False

                    self.ball_pos += self.ball_vector.clamp_magnitude(self.ball_speed * delta, self.ball_speed * delta)

                    last_wall = -1
                    if self.ball_pos.x < 0 and last_wall != 1:
                        if self.check_collision(self.player1_pos):
                            self.player2_score += 1
                            scored = True

                        self.ball_vector.x = -self.ball_vector.x
                        last_wall = 1

                    if self.ball_pos.x > 1 and last_wall != 2:
                        if self.check_collision(self.player2_pos):
                            self.player1_score += 1
                            scored = True

                        self.ball_vector.x = -self.ball_vector.x
                        last_wall = 2


                    if self.ball_pos.y < 0 and last_wall != 3:
                        self.ball_vector.y = -self.ball_vector.y
                        last_wall = 3

                    if self.ball_pos.y > 1 and last_wall != 4:
                        self.ball_vector.y = -self.ball_vector.y
                        last_wall = 4

                    if scored:
                        self.push(f"game score {self.player1_score} {self.player2_score}", self.player1)
                        self.push(f"game score {self.player2_score} {self.player1_score}", self.player2)

                        self.ball_pos = Vector2(0.5,0.5)
                        self.ball_vector = Vector2(1,2).normalize().rotate(randrange(0,360))

                    self.push(f"game state {self.ball_pos.x} {self.ball_pos.y} {self.player1_pos} {self.player2_pos}", self.player1)
                    self.push(f"game state {1 - self.ball_pos.x} {self.ball_pos.y} {self.player2_pos} {self.player1_pos}", self.player2)

                break
            sleep(0.1)

#----------------------------------------------------------------------------------------------------------#

def matchmaker():
    free_match_id = 1000
    while True:
        #x = waitlist.keys()
        total_waiting_players =  len(list(waitlist.values()))

        while total_waiting_players >= 2:

            keys = list(waitlist.keys())

            player1 = waitlist[keys[0]]
            player2 = waitlist[keys[1]]

            running_games[free_match_id] = Match(player1, player2, free_match_id)

            printlog(f"Started new Match ({free_match_id}), players: {running_games[free_match_id]}", "blue")

            player1.join_match(free_match_id)
            waitlist.pop(player1.player_id)

            player2.join_match(free_match_id)
            waitlist.pop(player2.player_id)
            
            threading._start_new_thread(running_games[free_match_id].game,())

            free_match_id +=1  
            total_waiting_players =  len(list(waitlist.values()))
        sleep(0.5)

#---------------------------------------#

def printlog(content, text_color):
    global logfile

    colors = {
        "purple":'\033[95m',
        "blue":'\033[94m',
        "cyan":'\033[96m',
        "green":'\033[92m',
        "orange":'\033[93m',
        "red":'\033[91m',
        "end_color":'\033[0m',
    }

    date = f"[{datetime.today().strftime('%Y/%m/%d %H:%M:%S')}]"
    print(f"{colors[text_color]}{date} {content}{colors['end_color']}")

    if LOG_TO_FILE:
        logfile = open("logfile.txt", "a")
        logfile.write(f"{date} {content}\n")
        logfile.close()

#---------------------------------------#

def move_to_waitlist(player_id):
    printlog(f"Player {player_id} joined the waiting list.","blue")
    waitlist[player_id] = afk_players[player_id]
    afk_players.pop(player_id)

#---------------------------------------#

def remove_from_waitlist(player_id):
    global waitlist
    waitlist.pop(player_id)

#---------------------------------------#

def rescue_player(match_id, player):
    afk_players[player.player_id] = player
    

#---------------------------------------#

def remove_match(match_id):
    global running_games
    running_games.pop(match_id)

#---------------------------------------#

def server_program():
    try:
        server_socket = socket.socket()
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        printlog(f"Server started successfully on port {SERVER_PORT}", "blue")
    except Exception as e:
        printlog(f"Failed to start server:  {str(e)}", "red")
        exit(1)

    free_ID = 1000
    while True:
        server_socket.listen(2)
        conn, ip = server_socket.accept()
        player = Player(conn, ip, free_ID)
        threading._start_new_thread(player.talk_to_player,())
        threading._start_new_thread(player.heartbeat,())
        afk_players[free_ID] = player
        free_ID += 1

#----------------------------------------------------------------------------------------------------------#

threading._start_new_thread(matchmaker,())
server_program()