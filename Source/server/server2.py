#!/bin/python3
import socket
import threading
from time import sleep, time
from datetime import datetime
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame.math import Vector2
from random import randrange, choice

#----------------------------------------------------------------------------------------------------------#

SERVER_PORT = 6969
SERVER_HOST = ''

LOG_TO_FILE = False
LOG_TO_CMD = True

PLAYER_WIDTH = 0.2
PLAYER_SPEED = 0.2

INTERVAL_LENGTH = 3
MAX_SCORE = 5

GAME_LOOP_SLEEP = 0.015

BALL_SPEED = 0.5

FILTER_POS = True

#----------------------------------------------------------------------------------------------------------#

afk_players = {}
waitlist = {}
running_games = {}

#----------------------------------------------------------------------------------------------------------#

class Player():
    def __init__(self, connection, player_ip, player_id):
        self.connection = connection
        self.player_ip = player_ip
        self.player_id = player_id
        self.state = "afk"
        self.match = None

        printlog(f"Player {self.player_id} from {self.player_ip[0]}:{self.player_ip[1]} connected to the game", "green")

    def __repr__(self):
        representation = f"[ID:{self.player_id},IP:{self.player_ip[0]},STATE:{self.state}]"
        return(str(representation))

    def put(self, content):
        try:
            self.connection.send(f"{content}\n".encode())

        except:
            self.running = False
            self.destroy("disconnected")
    
    def packet_parser(self, packet):
        if packet[0] == "player" and packet[1] == "time_sync":
            self.put(f"time_sync {time()}")

        elif packet[0] == "exit" and self.state != "dead":
            self.destroy("left")

        elif packet[0] == "game" and self.state == "playing":
            self.match.network_handler(packet[1:], self.player_id)
        
        elif packet == ["player","join","open"]:
            waitlist[self.player_id] = afk_players[self.player_id]
            afk_players.pop(self.player_id)

            self.state = "waiting"

            printlog(f"Player {self.player_id} joined the waiting list.","blue")

    def network_handler(self):
        empty_packets = 0

        while self.state != "dead":
            try:
                data = self.connection.recv(1024).decode()
                data = data.split("\n")

            except:
                self.destroy("disconnected")
                break
            
            for i in data:
                if len(i) != 0:
                    self.packet_parser(i.split(" "))
                    empty_packets = 0

                else:
                    empty_packets += 1
                    if empty_packets > 20:
                        self.destroy("disconnected")

    def join_match(self, match):
        self.state = "playing"
        self.match = match

    def destroy(self, reason):
        if reason == "disconnected":
            printlog(f"Player {self.player_id} from {self.player_ip[0]}:{self.player_ip[1]} disconnected.", "red")
        
        elif reason == "left":
            printlog(f"Player {self.player_id} from {self.player_ip[0]}:{self.player_ip[1]} left.", "green")
        
        if self.state == "playing":
            self.match.disolve(self.player_id, reason)
        
        elif self.state == "afk":
            afk_players.pop(self.player_id)
        
        elif self.state == "waiting":
            waitlist.pop(self.player_id)
        
        self.state = "dead"
        self.connection.close()

#---------------------------------------#

class Match():
    def __init__(self, player1, player2):
        self.state = "starting"
        self.player1 = player1
        self.player2 = player2

        self.ball_pos = Vector2(0.5, 0.5)
        self.ball_vector = self.throw_ball()

        self.player1_pos = 0.5
        self.player2_pos = 0.5

        self.player1_score = 0
        self.player2_score = 0
    
    def __repr__(self):
        representation = f"[Player1:{self.player1},Player2:{self.player2}]"
        return(str(representation))
    
    def broadcast(self, content):
        self.player1.put(content)
        self.player2.put(content)

    def throw_ball(self):
        throw_range = (list(range(40,71)) + list(range(110, 141)))
        throw_deg = (choice(throw_range) + choice([0,180]))
        ball_vec = Vector2(0,1).rotate(throw_deg).normalize()

        return(ball_vec)

    def disolve(self, player, reason):
        self.state = "finished"

        def notify_enemy(self, player, reason):
            if player == self.player1.player_id:
                self.player2.put(f"game ended {reason}")
                self.player2.state = "afk"
                self.player2.match = None
                afk_players[self.player2.player_id] = self.player2

            else:
                self.player1.put(f"game ended {reason}")
                self.player1.state = "afk"
                self.player1.match = None
                afk_players[self.player1.player_id] = self.player1

        if reason == "left":
            notify_enemy(self, player, reason)
            printlog(f"Game ended because {player} left the game", "orange")

        elif reason == "disconnected":
            notify_enemy(self, player, reason)
            printlog(f"Game ended because {player} got disconnected", "red")
        
        elif reason == "finished":
            if self.player1_score > self.player2_score:
                self.player1.put("game ended finished lost")
                self.player2.put("game ended finished won")
            
            else:
                self.player1.put("game ended finished won")
                self.player2.put("game ended finished lost")
            
            self.player2.state = "afk"
            self.player2.match = None
            afk_players[self.player2.player_id] = self.player2

            self.player1.state = "afk"
            self.player1.match = None
            afk_players[self.player1.player_id] = self.player1

    def send_state(self):
        self.player1.put(f"game state {self.ball_pos.x} {self.ball_pos.y} {self.player1_pos} {self.player2_pos}")
        self.player2.put(f"game state {1 - self.ball_pos.x} {self.ball_pos.y} {self.player2_pos} {self.player1_pos}")

    def check_collision(self, pos):
        pos2 = pos * (1 - PLAYER_WIDTH) + PLAYER_WIDTH / 2

        if self.ball_pos.y < pos2 - PLAYER_WIDTH / 2 or self.ball_pos.y > pos2 + PLAYER_WIDTH / 2:
            return(True)

        else:
            return(False)

    def network_handler(self, packet, sender):
        if packet[0] == "moved":
            if sender == self.player1.player_id:
                self.player1_pos = float(packet[1])
            else:
                self.player2_pos = float(packet[1])

    def filter_pos(self, vec):
        if vec.x > 1:
            vec.x = 1
            
        if vec.y > 1:
            vec.y = 1
        
        if vec.x < 0:
            vec.x = 0
            
        if vec.y < 0:
            vec.y = 0
        
        return vec

    def game(self):
        last_time = time()
        last_wall = 0

        while self.state != "finished":
            delta = time() - last_time
            last_time = time()

            scored = False

            sleep(GAME_LOOP_SLEEP)

            self.ball_pos += self.ball_vector.clamp_magnitude(BALL_SPEED * delta, BALL_SPEED * delta)

            if self.ball_pos.x < 0 and last_wall != 1:
                self.ball_vector.x = - self.ball_vector.x
                last_wall = 1

                if self.check_collision(self.player1_pos):
                    self.player1_score += 1
                    scored = True
                else:
                    self.broadcast("bounce")

            elif self.ball_pos.x > 1 and last_wall != 2:
                self.ball_vector.x = - self.ball_vector.x
                last_wall = 2

                if self.check_collision(self.player2_pos):
                    self.player2_score += 1
                    scored = True
                else:
                    self.broadcast("bounce")
            
            elif self.ball_pos.y < 0 and last_wall != 3:
                self.ball_vector.y = -self.ball_vector.y
                last_wall = 3
                self.broadcast("bounce")

            elif self.ball_pos.y > 1 and last_wall != 4:
                self.ball_vector.y = -self.ball_vector.y
                last_wall = 4
                self.broadcast("bounce")

            if FILTER_POS:
                self.filter_pos(self.ball_pos)

            if scored:
                self.player1.put(f"game score {self.player1_score} {self.player2_score}")
                self.player2.put(f"game score {self.player2_score} {self.player1_score}")

                self.ball_pos = Vector2(0.5,0.5)
                self.ball_vector = self.throw_ball()

                self.send_state()

                if self.player1_score >= MAX_SCORE or self.player2_score >= MAX_SCORE:
                    self.state = "finished"
                    self.disolve(0, "finished")
                    break

                self.broadcast(f"game pause {time() + INTERVAL_LENGTH}")
                last_wall = 0
                sleep(INTERVAL_LENGTH)
                last_time = time()
            
            self.send_state()

    def main(self):
        start_time = time() + INTERVAL_LENGTH

        self.player1.put(f"game info {start_time} {PLAYER_WIDTH} {PLAYER_SPEED} {self.player1_pos} {self.player2_pos}")
        self.player2.put(f"game info {start_time} {PLAYER_WIDTH} {PLAYER_SPEED} {self.player2_pos} {self.player1_pos}")

        while True:
            if time() > start_time:
                self.game()
                break
            else:
                sleep(0.1)            

#----------------------------------------------------------------------------------------------------------#

def matchmaker():
    free_match_id = 1000

    while True:
        waiting_players =  list(waitlist.keys())

        while len(waiting_players) >= 2:
            player1 = choice(waiting_players)
            player2 = choice(waiting_players)

            while player2 == player1:
                player2 = choice(waiting_players)
            
            new_match = Match(waitlist[player1], waitlist[player2])

            waitlist[player1].join_match(new_match)
            waitlist[player2].join_match(new_match)

            threading._start_new_thread(new_match.main, ())

            waitlist.pop(player1)
            waitlist.pop(player2)

            running_games[free_match_id] = new_match
            free_match_id += 1

            printlog(f"Started new Match ({free_match_id}) -> {new_match}", "blue")

            waiting_players =  list(waitlist.keys())
        
        sleep(0.1)

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

    if LOG_TO_CMD:
        print(f"{colors[text_color]}{date} {content}{colors['end_color']}")

    if LOG_TO_FILE:
        logfile = open("logfile.txt", "a")
        logfile.write(f"{date} {content}\n")
        logfile.close()

#---------------------------------------#

def server_program():
    try:
        server_socket = socket.socket()
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        printlog(f"Server started successfully on port {SERVER_PORT}", "blue")

    except Exception as e:
        printlog(f"Failed to start server:  {str(e)}", "red")
        quit(1)

    free_player_id = 1000

    while True:
        server_socket.listen(2)
        conn, ip = server_socket.accept()
        player = Player(conn, ip, free_player_id)
        threading._start_new_thread(player.network_handler,())
        afk_players[free_player_id] = player
        free_player_id += 1

#----------------------------------------------------------------------------------------------------------#

threading._start_new_thread(matchmaker,())
server_program()