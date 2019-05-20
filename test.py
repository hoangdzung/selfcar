import pygame, sys
from pygame.locals import *

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import random
import math

from utils import eculid_distance
from virtual_map import Map 

class Road():
    def __init__(self, pts1, pts2, pts3, pts4, type='road', time=None):
        assert type in ["road", "intersection"]
        self.type = type
        if self.type == "intersection":
            self.time = time 
            self.count = random.randint(0, self.time)
            self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
            self.textsurface = self.myfont.render(str(self.count), False, (0, 0, 0))

        self.type = type
        self.pts1 = pts1 
        self.pts2 = pts2
        self.pts3 = pts3
        self.pts4 = pts4
        self.points = [self.pts1, self.pts2, self.pts3, self.pts4]
        self.polygon = Polygon(self.points)
        self.is_chosen = False
        self.color = (255, 0,0)

        self.textsurface_loc = None 

    def draw(self, display):
        pygame.draw.polygon(display, self.color, self.points)
        if self.textsurface_loc is not None:
            display.blit(self.textsurface, self.textsurface_loc)

    def clicked(self,display):
        self.is_chosen = not self.is_chosen
        if self.is_chosen:
            self.color = (0,255,0)
        else:
            self.color = (255,0,0) 
        self.draw(display)

    def update(self):
        if self.type == 'intersection':
            self.count = (self.count+1)%self.time
            self.textsurface = self.myfont.render(str(self.count), False, (0, 0, 0))
            # self.draw(display)
            # 
            self.textsurface_loc = ((self.pts1[0]+self.pts3[0])/2,(self.pts1[1]+self.pts3[1])/2)
            

    def include(self, x, y):
        return self.polygon.contains(Point(x,y))

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
    def __init__(self, x, y, w, h, routes=None):
        self.image = pygame.transform.scale(pygame.image.load("car.png"), (w,h))
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.front_left = [x+w/2,y+h/2]
        self.front_right = [x+w/2,y-h/2]
        self.back_left = [x-w/2,y+h/2]
        self.back_right = [x-w/2,y-h/2]
        self.color = (0,0,0)
        self.angle = 0
        self.temp_center = None
        self.routes = routes
        self.road_idx = 0
        
        # self.center = [(self.front_left[0] + self.back_right[0])/2,(self.front_left[1] + self.back_right[1])/2]
    
    def set_routes(self,routes):
        self.routes=routes

    def rotate(self, angle=math.pi/4):
        # center = self.rect.center
        # self.front_left = rotate(center, self.front_left, angle)
        # self.front_right = rotate(center, self.front_right, angle)
        # self.back_left = rotate(center, self.back_left, angle)
        # self.back_right = rotate(center, self.back_right, angle)
        # self.center = [(self.front_left[0] + self.back_right[0])/2,(self.front_left[1] + self.back_right[1])/2]
        self.angle += angle
        self.temp_center = self.rotateAroundCenter(self.angle)
        
    def rotateAroundCenter(self, angle):
        pos = self.rect.center
        w, h = self.image.get_size()
        originPos = [w/2, h/2]
        # calcaulate the axis aligned bounding box of the rotated image
        box = [pygame.math.Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
        box_rotate = [p.rotate(angle) for p in box]
        min_box = (min(box_rotate, key=lambda p: p[0])[
                0], min(box_rotate, key=lambda p: p[1])[1])
        max_box = (max(box_rotate, key=lambda p: p[0])[
                0], max(box_rotate, key=lambda p: p[1])[1])

        # calculate the translation of the pivot
        pivot = pygame.math.Vector2(originPos[0], -originPos[1])
        pivot_rotate = pivot.rotate(angle)
        pivot_move = pivot_rotate - pivot

        # calculate the upper left origin of the rotated image
        origin = (pos[0] - originPos[0] + min_box[0] - pivot_move[0],
                pos[1] - originPos[1] - max_box[1] + pivot_move[1])
        return origin
        # get a rotated image
        rotated_image = pygame.transform.rotate(self.image, math.degrees(angle))
        # rotate and blit the image
        display.blit(rotated_image, origin)

    def draw(self, display):
        rotated_image = pygame.transform.rotate(self.image, math.degrees(self.angle))
        if self.temp_center is not None:
            display.blit(rotated_image, self.temp_center)
        else:
            display.blit(rotated_image, self.rect.center)

    def update(self):
        self.rotate()
        # self.draw(display)

    
    def find_location(self):
        for i, road in enumerate(self.routes):
            if i < self.road_idx:
                continue
            if road.include(self.rect.left, self.rect.top):
                return i
        return -1

    @staticmethod 
    def find_common_vertex(road1, road2):
        return [pts for pts in road1.points if pts in road2.points ]

    def sensor_redlight(self):
        # TODO: check at the end of routes
        self.road_idx = self.find_location()
        if self.routes[self.road_idx].type == 'road': 
            common_vertex = self.find_common_vertex(self.routes[self.road_idx], self.routes[self.road_idx+1])
            self.next_intersection = self.routes[self.road_idx+1]
        elif self.routes[self.road_idx].type == 'intersection':
            common_vertex = self.find_common_vertex(self.routes[self.road_idx+1], self.routes[self.road_idx+2])
            self.next_intersection = self.routes[self.road_idx+2]

        self.next_redlight_location = [(common_vertex[0][0]+common_vertex[1][0])/2, (common_vertex[0][1]+common_vertex[1][1])/2]
        self.redlight_distance = eculid_distance([self.rect.left, self.rect.top], self.next_redlight_location)
        self.redlight_time = self.next_intersection.count 


def main():
    pygame.init()
    mapW = 1000
    mapH = 1000
    virtual_map = Map(mapW, mapH)

    DISPLAY=pygame.display.set_mode((1000,1000),0,32)

    WHITE=(255,255,255)
    BLUE=(0,0,255)
    RED=(255,0,0)

    
    road1 = Road([0,0], [50,0], [50, 200] , [0,200])
    road2 = Road([0,200], [50,200], [50,250], [0,250], "intersection", 20)
    road3 = Road([50,200], [300, 200],[300,250], [50,250])
    road4 = Road([300,200], [350, 200], [350,250], [300,250], "intersection", 20)
    road5 = Road([300,200], [350,200], [50, 0], [50,50])
    roads = [road1, road2, road3, road4, road5]
    
    routes  = []
    route_picked = False

    while True:
        DISPLAY.fill(WHITE)
        for road in roads:
            road.draw(DISPLAY)
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
                        road.clicked(DISPLAY)
                        routes.append(road)
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_RETURN:
                    print("Enter")
                    route_picked = True
                    virtual_map.drawRoutes(routes)
                    # done choosing routes
                    # update virtual map
        if route_picked:
            break
        pygame.display.update()

    car_pick=False
    while True:
        DISPLAY.fill(WHITE)
        for road in roads:
            road.draw(DISPLAY)
        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                car = Car(mousex,mousey,20,10,routes)
                car.draw(DISPLAY)
                car_pick=True
        if car_pick:
            break
        pygame.display.update()


    while True:
        DISPLAY.fill(WHITE)
        for road in roads:
            road.update()
            road.draw(DISPLAY)
        car.sensor_redlight()
        car.update()
        print(car.redlight_distance, car.redlight_time)
        car.draw(DISPLAY)    
        pygame.display.update()

main()