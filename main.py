import pygame 
import pymunk 
import math 
import pymunk.pygame_util 

import random
from typing import Tuple


pygame.init()
WIDTH, HEIGHT = 1200, 678

# game window 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("pool")

# pymunk space 
space = pymunk.Space()
static_body = space.static_body # objects are to be attached to this static body via joints

# space.gravity = (0, 981) // not needed in a pool game

draw_options = pymunk.pygame_util.DrawOptions(screen)

# create a ball
def create_ball(radius, position):
    body = pymunk.Body()
    body.position = position

    shape = pymunk.Circle(body, radius)
    shape.mass = 50

    # pivot joint to add friction 
    # (0, 0) -> center of both objects
    pivot = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0))
    pivot.max_bias = 0  # no headstart in friction 
    pivot.max_force = 10000 # linear friction 


    space.add(body, pivot, shape)
    return shape


ball_1 = create_ball(25, (560, 300))
cue_ball = create_ball(25, (600, 340))


def create_cushion(poly_dims):
    body = pymunk.Body(body_type=pymunk.body.STATIC) # static holes to get the balls 
    body.position = ((0, 0))

    shape = pymunk.Poly(body, poly_dims)
    
    space.add(body, shape)
    
# game loop 
running = True 
bgColor = (50, 50, 50)

# Clock
FPS = 120 
clock = pygame.time.Clock()

# images 
table_image = pygame.image.load('.\\assets\\images\\table.png').convert_alpha()

while running:
    clock.tick(FPS)
    space.step(1 / FPS)

    # fill background 
    screen.fill(bgColor)

    # draw pool table 
    screen.blit(table_image, (0, 0)) # from left-top corner

    # event handler for exiting of game 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            cue_ball.body.apply_impulse_at_local_point((-50000, 0), (0, 0))

    # draw all the objects created
    space.debug_draw(draw_options)
    pygame.display.update()

pygame.QUIT