#!/usr/bin/python
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame.math import Vector2

def pos(vec):
    if vec.x > 1:
        vec.x = 1
        
    if vec.y > 1:
        vec.y = 1
    
    if vec.x < 0:
        vec.x = 0
        
    if vec.y < 0:
        vec.y = 0
    
    return vec

def num(num):
    if num < 0:
        return(0)
    if num > 1:
        return(1)
    else:
        return(num)