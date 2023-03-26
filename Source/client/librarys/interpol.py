#!/usr/bin/python
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame.math import Vector2

def col(color1, color2, percentage):
    color = ()
    for i in range(len(color1)):
        result = ((color1[0] * (1 - percentage)) + (color2[0] * percentage))
        if result > 255:
            result = 255
        
        if result < 0:
            result = 0
        
        color = color + (result,)

    return(color)

def num(num_1, num_2, percentage):
    result = ((num_1 * (1 - percentage)) + (num_2 * percentage))
    
    return(result)

def vec(vec1, vec2, percentage):
    x = ((vec1.x * (1 - percentage)) + (vec2.x * percentage))
    y = ((vec1.y * (1 - percentage)) + (vec2.y * percentage))
    return(Vector2(x, y))