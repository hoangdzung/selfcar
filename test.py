import pygame, sys
from pygame.locals import *

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import random
import math

class Road():
    def __init__(self, pts1, pts2, pts3, pts4):
        self.pts1 = pts1 
        self.pts2 = pts2
        self.pts3 = pts3
        self.pts4 = pts4
        self.points = [self.pts1, self.pts2, self.pts3, self.pts4]
        self.polygon = Polygon(self.points)
        self.is_chosen = False
        self.color = (255, 0,0)

    def draw(self, display):
        pygame.draw.polygon(display, self.color, self.points)

    def update(self,display):
        self.is_chosen = not self.is_chosen
        if self.is_chosen:
            self.color = (0,255,0)
        else:
            self.color = (255,0,0) 
        self.draw(display)
    
    def include(self, x, y):
        return self.polygon.contains(Point(x,y))

# class InterSect(Road):
#     def __init__(self, pts1, pts2, pts3, pts4, time):
#         super(InterSect).__init__(self, pts1, pts2, pts3, pts4)
#         self.time = time 
#         self.count = random.randint(self.time)
    
#     def 

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        self.front_left = [x+w/2,y+h/2]
        self.front_right = [x+w/2,y-h/2]
        self.back_left = [x-w/2,y+h/2]
        self.back_right = [x-w/2,y-h/2]
        self.color = (0,0,0)
        self.image = pygame.transform.scale(pygame.image.load("car.png"), (w,h))
        self.center = [(self.front_left[0] + self.back_right[0])/2,(self.front_left[1] + self.back_right[1])/2]

    def rotate(self,angle=math.pi/4):
        
        center =self.center
        self.front_left = rotate(center, self.front_left, angle)
        self.front_right = rotate(center, self.front_right, angle)
        self.back_left = rotate(center, self.back_left, angle)
        self.back_right = rotate(center, self.back_right, angle)
        self.center = [(self.front_left[0] + self.back_right[0])/2,(self.front_left[1] + self.back_right[1])/2]
        pygame.transform.rotate(self.image, angle) 

    def draw(self, display):
        display.blit(self.image, self.center)

    def update(self, display):
        self.rotate()
        self.draw(display)
def main():
    pygame.init()

    DISPLAY=pygame.display.set_mode((500,400),0,32)

    WHITE=(255,255,255)
    BLUE=(0,0,255)
    RED=(255,0,0)

    DISPLAY.fill(WHITE)
    road1 = Road([0,0], [50,0], [50, 200] , [0,200])
    road2 = Road([0,200], [50,200], [50,250], [0,250])
    road3 = Road([50,200], [300, 200],[300,250], [50,250])
    road4 = Road([300,200], [350, 200], [350,250], [300,250])
    road5 = Road([300,200], [350,200], [50, 0], [50,50])
    roads = [road1, road2, road3, road4, road5]
    # pygame.draw.rect(DISPLAY,BLUE,(200,150,100,50))
    for road in roads:
        road.draw(DISPLAY)
    car = Car(25,225,20,10)
    car.draw(DISPLAY)
    routes  = []
    start = False
    i=0
    while True:
        mouseClicked = False
        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True
            if mouseClicked:
                for road in roads:
                    if road.include(mousex, mousey):
                        road.update(DISPLAY)
                        routes.append(road)
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_KP_ENTER:
                    start = True
        i+=1
        print(i)
        if i %500==0:
            car.update(DISPLAY)

        pygame.display.update()

main()