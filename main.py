import pygame 
import pymunk 
import math 
import pymunk.pygame_util 

pygame.init()
WIDTH, HEIGHT = 1200, 678

# game window 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("pool")


# images 
table_image = pygame.image.load('.\\assets\\images\\table.png').convert_alpha()
cue_image = pygame.image.load('.\\assets\\images\\cue.png')

# pymunk space 
space = pymunk.Space()
static_body = space.static_body # objects are to be attached to this static body via joints
draw_options = pymunk.pygame_util.DrawOptions(screen)

# clock
FPS = 120 
clock = pygame.time.Clock()

# game variables
diameter = 36
taking_shot = True 
force = 0
max_force = 10_000
force_direction = 1
powering_up = False

# create a ball
def create_ball(radius, position):
    body = pymunk.Body()
    body.position = position

    shape = pymunk.Circle(body, radius)
    shape.mass = 50

    # add bouncing capabilities 
    shape.elasticity = 0.95

    # pivot joint to add friction 
    # (0, 0) -> center of both objects
    pivot = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0))
    pivot.max_bias = 0  # no headstart in friction 
    pivot.max_force = 10000 # linear friction 


    space.add(body, pivot, shape)
    return shape

# setup game balls
balls = []
rows = 5 

from_the_left = 250 #px 
from_the_top  = 267 #px

# potting balls 
for col in range(5):
    for row in range(rows):
        y_offset = col * diameter // 2

        pos = (from_the_left + (col * (diameter + 3)), y_offset + from_the_top + (row * (diameter +3))) # start from left, and increase by column * dia per iteration 
        new_ball = create_ball(diameter // 2, pos)
        balls.append(new_ball)

    rows -= 1


cue_ball = create_ball(diameter / 2, (888, HEIGHT // 2))
balls.append(cue_ball)

#create six pockets on table
pockets = [
  (55, 63),
  (592, 48),
  (1134, 64),
  (55, 616),
  (592, 629),
  (1134, 616)
]

#create pool table cushions
cushions = [
  [(88, 56), (109, 77), (555, 77), (564, 56)],
  [(621, 56), (630, 77), (1081, 77), (1102, 56)],
  [(89, 621), (110, 600),(556, 600), (564, 621)],
  [(622, 621), (630, 600), (1081, 600), (1102, 621)],
  [(56, 96), (77, 117), (77, 560), (56, 581)],
  [(1143, 96), (1122, 117), (1122, 560), (1143, 581)]
]

def create_cushion(poly_dims):
    body = pymunk.Body(body_type=pymunk.Body.STATIC) # static holes to get the balls 
    body.position = ((0, 0))
    shape = pymunk.Poly(body, poly_dims)
    shape.elasticity = 0.65

    space.add(body, shape)

for c in cushions:
    create_cushion(c)
     
# create pool cue
class Cue():
    def __init__(self, pos):
        self.original_img = cue_image
        self.angle = 0
        self.image = pygame.transform.rotate(self.original_img, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = pos
    
    def update(self, angle):
        self.angle = angle

    def draw(self, surface):
        self.image = pygame.transform.rotate(self.original_img, self.angle)
        surface.blit(self.image,
            (self.rect.centerx - self.image.get_width() / 2,
             self.rect.centery - self.image.get_height() / 2),
        )

# create cue 
cue = Cue(balls[-1].body.position) # last ball put in is cueball

# game loop 
running = True 
bgColor = (50, 50, 50)


ball_images = []
for i in range(1, 17):
    # balls drawin in game loop associated with respective ball bodies
    ball_image = pygame.image.load(f".\\assets\\images\\ball_{i}.png").convert_alpha()
    ball_images.append(ball_image)

while running:
    clock.tick(FPS)
    space.step(1 / FPS)

    # fill background 
    screen.fill(bgColor)

    # draw pool table 
    screen.blit(table_image, (0, 0)) # from left-top corner

    # draw pool balls
    for index, ball in enumerate(balls):
        # compatibility issue between pygame and pymunk - incorrect mapping of positions 
        img_pos = (ball.body.position[0] - ball.radius, ball.body.position[1] - ball.radius)

        screen.blit(ball_images[index], img_pos)
    
    # check if all balls have stopped moving so that the cue should reappear
    taking_shot = True
    for ball in balls:
        if int(ball.body.velocity[0]) != 0 or int(ball.body.velocity[1]) != 0:
            taking_shot = False

    # draw cue ball
    # pool cue angle 
    if taking_shot: 
        mouse_pos = pygame.mouse.get_pos()
        cue.rect.center = balls[-1].body.position
        x_dist = balls[-1].body.position[0] - mouse_pos[0]
        y_dist = -(balls[-1].body.position[1] - mouse_pos[1]) # -ve bcz pygame y coordinate increases down the screen 

        cue_angle = math.degrees(math.atan2(y_dist, x_dist)) # given in radians

        cue.update(cue_angle)
        cue.draw(screen)

    # power up pool cue 
    if powering_up:
        force += 100 * force_direction

        if force >= max_force or force < 0:
            force_direction *= (-1)
        print(force)

        # increaes force 
    elif not powering_up and taking_shot:
        x_dir_impulse = math.cos(math.radians(cue_angle)) * force
        y_dir_impulse = math.sin(math.radians(cue_angle)) * force
        balls[-1].body.apply_impulse_at_local_point((-x_dir_impulse, y_dir_impulse), (0, 0))

        force = 0 # reset zero
        force_direction = 1

    # event handler for exiting of game 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and taking_shot:
            powering_up = True
        
        if event.type == pygame.MOUSEBUTTONUP and taking_shot:
            powering_up = False  

            
    # draw all the objects created
    # space.debug_draw(draw_options)
    pygame.display.update()

pygame.QUIT