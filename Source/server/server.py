#!/bin/python3
import socket
import threading
from time import sleep, time
from datetime import datetime
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame.math import Vector2

#static variables
SERVER_PORT = 6969
SERVER_HOST = ''

MATCH_SIZE = 2

#changing stuff
afk_players = {

}

waitlist = {

}

running_games = {

}

#classes
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

    def __repr__(self):
        return(str(self.player_id))

    def put(self, content):
        try:
            self.connection.send(f"{content}\n".encode())

        except:
            printlog(f"Player {self.player_id} disconnected from the game.","red")
            self.exit()

    def talk_to_player(self):
        printlog(f"Player {self.player_id} from {self.ip[0]} joined the game", "green")

        while self.running:
            data = self.connection.recv(1024).decode()
            data = data.split("\n")
            for i in data:
                command = i.split(" ")
                if command[0] == "player":
                    if command[1] == "set":
                        if command[2] == "color":
                            self.color = command[3]
                    
                        if command[2] == "name":
                            self.name = command[3]

                    if command[1] == "exit":
                        printlog(f"Player {self.player_id} from {self.ip[0]} left the game", "orange")
                        self.exit()
                
                    if command[1] == "join":
                        if command[2] == "open":
                            if self.match_id == 0:
                                move_to_waitlist(self.player_id)
                                self.put("player entered waitlist")
                
                if command[0] == "game":
                    if self.match_id != 0:
                        self.match.main(command[1:], self.player_id)

    def join_match(self, match_id):
        self.match_id = match_id
        self.match = running_games[self.match_id]
        self.put(f"game started")

    def exit(self):
        if self.match_id != 0:
            self.match.exit(self.player_id)

        self.connection.close()
        self.running = False


class Match:
    def __init__(self, players, match_id):
        self.players = players
        self.match_id = match_id

        self.variables = {
            "ball_radius":0.1,
            "ball_pos":Vector2(0.5,0.5),
            "ball_vector":Vector2(1,2),
            "ball_speed": 0.1,
            
            "player1_id": 0,
            "player1_score": 0,
            "player1_pos": 0.5,

            "player2_id": 0,
            "player2_pos": 0.5,
            "player2_score": 0,
        }

        self.variables["player1_id"] = players[list(self.players.keys())[0]].player_id
        self.variables["player2_id"] = players[list(self.players.keys())[1]].player_id
    
    def __repr__(self):
        return str(self.players)
    
    def broadcast(self, content, sender):
        for i in self.players:
            if self.players[i].player_id != sender:
                self.players[i].put(content)
    
    def push(self, content, player):
        self.players[player].put(content)

    def exit(self, player_id):
        for i in self.players:
            if self.players[i].player_id != player_id:
                self.players[i].put(f"game netevent player_left {player_id}")
                afk_players[i] = self.players[i]
                afk_players[i].match_id = 0

        self.players = {}
        printlog(f"Match {self.match_id} ended, because player {player_id} left the game","orange")
        remove_match(self.match_id)

    def game(self):
        start_time = int(time()) + 10
        running = True

        self.broadcast(f"game starts {start_time}", 0)
        last_time = time()
        while running:
            if start_time < time():
                delta = last_time - time()
                last_time = time()
                vec = self.variables["ball_vector"].normalize()
                vec.x = vec.x * self.variables["ball_speed"] * delta
                vec.y = vec.y * self.variables["ball_speed"] * delta

                self.variables["ball_pos"] += vec

                if self.variables["ball_pos"].x > 1:
                    self.variables["ball_vector"].x = -self.variables["ball_vector"].x
                    
                if self.variables["ball_pos"].x < 0:
                    self.variables["ball_vector"].x = -self.variables["ball_vector"].x

                if self.variables["ball_pos"].y > 1:
                    self.variables["ball_vector"].y = -self.variables["ball_vector"].y
                    
                if self.variables["ball_pos"].y < 0:
                    self.variables["ball_vector"].y = -self.variables["ball_vector"].y
                
                info_packet1 = f"game state {self.variables['ball_pos'].x} {self.variables['ball_pos'].y} {self.variables['player1_pos']} {self.variables['player2_pos']}"
                info_packet2 = f"game state {1 - self.variables['ball_pos'].x} {self.variables['ball_pos'].y} {self.variables['player1_pos']} {self.variables['player2_pos']}"
                self.push(info_packet1, self.variables["player1_id"])
                self.push(info_packet2, self.variables["player2_id"])

    def main(self, command, sender):
        if command[0] == "set":
            self.variables[command[1]] = command[2]
            if len(command) == 4:
                self.broadcast(f"game var {command[1]} {command[2]}", sender)
        
        if command[0] == "get":
            if command[1] in self.variables.keys():
                requested_data = self.variables[command[1]]
                self.push(f"game var {command[1]} {requested_data}", sender)
        
        if command[0] == "msg":
            message = " ".join(command[1:])
            self.broadcast(f"game msg {message}", sender)

#functions
def matchmaker():
    free_match_id = 1000
    while True:
        #x = waitlist.keys()
        total_waiting_players =  len(list(waitlist.values()))

        while total_waiting_players >= MATCH_SIZE:

            keys = list(waitlist.keys())

            invited_players = 0
            players = {}

            for i in keys:
                if invited_players <= MATCH_SIZE:
                    players[i] = waitlist[i]
                else:
                    break

            running_games[free_match_id] = Match(players, free_match_id)

            printlog(f"Started new Match ({free_match_id}) with {running_games[free_match_id]}", "blue")

            for i in players:
                players[i].join_match(free_match_id)
                waitlist.pop(players[i].player_id)
            
            threading._start_new_thread(running_games[free_match_id].game,())


            free_match_id +=1  
            total_waiting_players =  len(list(waitlist.values()))
        sleep(1)

def printlog(content, text_color):
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

def move_to_waitlist(player_id):
    printlog(f"Player {player_id} joined the waiting list.","blue")
    waitlist[player_id] = afk_players[player_id]
    afk_players.pop(player_id)

def remove_match(match_id):
    running_games.pop(match_id)

def server_program():
    server_socket = socket.socket()
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    free_ID = 1000

    while True:
        server_socket.listen(2)
        conn, ip = server_socket.accept()
        player = Player(conn, ip, free_ID)
        threading._start_new_thread(player.talk_to_player,())
        afk_players[free_ID] = player
        free_ID += 1

threading._start_new_thread(matchmaker,())
server_program()