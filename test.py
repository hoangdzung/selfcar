import pygame, sys
from pygame.locals import *

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import random
import math

from utils import euclide_distance
from distance import distance_to_borders, distance_to_obstacles
from virtual_map import Map 
from controller import get_steering_controller, get_speed_controller

import numpy as np 

from obstacle import init_obstacle_from_pos
steering_controller = get_steering_controller()
speed_controller = get_speed_controller()

ROAD_SCALE = 1.5

class Road():
    def __init__(self, pts1, pts2, pts3, pts4, type='road', time=None):
        assert type in ["road", "intersection"]
        self.type = type
        if self.type == "intersection":
            self.time = time 
            self.count = random.randint(0, self.time)
            self.myfont = pygame.font.SysFont('Comic Sans MS', 30)
            self.textsurface = self.myfont.render(str(self.count), False, (0, 0, 0))
        pts1 = [int(x * ROAD_SCALE) for x in pts1]
        pts2 = [int(x * ROAD_SCALE) for x in pts2]
        pts3 = [int(x * ROAD_SCALE) for x in pts3]
        pts4 = [int(x * ROAD_SCALE) for x in pts4]

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
        print(self.points)
        self.is_chosen = not self.is_chosen
        if self.is_chosen:
            self.color = (0,255,0)
        else:
            self.color = (255,0,0) 
        self.draw(display)

    def update(self):
        if self.type == 'intersection':
            self.count = (self.count+1)%self.time
            self.textsurface = self.myfont.render(str(6-self.count/10), False, (0, 0, 0))
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
    def __init__(self, x, y, w, h, steering_controller, speed_controller, virtual_map, routes=None):
        self.image = pygame.transform.scale(pygame.image.load("car.png"), (w,h))
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.steering_controller = steering_controller
        self.speed_controller = speed_controller
        # self.front_left = [x+w/2,y+h/2]
        # self.front_right = [x+w/2,y-h/2]
        # self.back_left = [x-w/2,y+h/2]
        # self.back_right = [x-w/2,y-h/2]
        self.color = (0,0,0)
        self.angle = 0
        self.temp_center = None
        self.routes = routes
        self.road_idx = 0
        self.virtual_map = virtual_map
        self.speed=3

        # 
        self.distanceL = None 
        self.distanceR = None 
        self.distanceFL = None 
        self.distanceFR = None
        self.distanceBackL = None
        self.distanceBackR = None
        self.distanceL45 = None 
        self.distanceR45 = None 

        self.find_init_angle_sensor_with_center_pos()
        self.compute_pos_sensors()
        self.rotate_true_angle()
        
        

        # self.center = [(self.front_left[0] + self.back_right[0])/2,(self.front_left[1] + self.back_right[1])/2]
    def rotate_true_angle(self):
        self.sensor_redlight()
        right_vector = np.array(self.next_redlight_location) - np.array([self.rect.left, self.rect.top])
        self.angle = - np.arccos(right_vector[0]/np.linalg.norm(right_vector)) 

    def set_routes(self,routes):
        self.routes=routes

    def rotate(self, angle=math.pi/32):
        self.angle += angle
        self.temp_center = self.rotateAroundCenter(self.angle)

    def find_init_angle_sensor_with_center_pos(self):
        centerX, centerY = self.rect.center
        ulX, ulY = self.rect.left, self.rect.top  # up left position
        half_diagonal = euclide_distance((ulX, ulY), (centerX, centerY))
        self.init_sensor_angle, self.half_diagonal = math.acos((self.rect.width//2)/half_diagonal), half_diagonal    
    
    def compute_pos_sensors(self):
        half_diagonal = self.half_diagonal
        # if self.temp_center is not None:
        #     centerX, centerY = self.temp_center
        # else:
        centerX, centerY = self.rect.center
        self.front_left = [centerX+half_diagonal * math.cos(self.angle+self.init_sensor_angle),
                        centerY - half_diagonal*math.sin(self.angle+self.init_sensor_angle)]  # position of left sensor
        self.front_right = [
            centerX+half_diagonal * math.cos(self.angle-self.init_sensor_angle),
            centerY - half_diagonal*math.sin(self.angle-self.init_sensor_angle)
        ]  # position of right sensor
        self.back_left = [
            centerX+half_diagonal * math.cos(math.pi + self.angle-self.init_sensor_angle),
            centerY - half_diagonal*math.sin(math.pi + self.angle-self.init_sensor_angle)
        ]
        self.back_right = [
            centerX+half_diagonal * math.cos(math.pi + self.angle+self.init_sensor_angle),
            centerY - half_diagonal*math.sin(math.pi + self.angle+self.init_sensor_angle)
        ]  # position of right sensor
        self.upperMid = [
            (self.front_left[0]+self.front_right[0]) // 2,
            (self.front_left[1]+self.front_right[1]) // 2,
        ]
        self.meanUpperMid = [
            (self.upperMid[0] + self.rect.center[0])//2,
            (self.upperMid[1] + self.rect.center[1])//2,
        ]


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

    def draw(self, display):
        rotated_image = pygame.transform.rotate(self.image, math.degrees(self.angle))
        if self.temp_center is not None:
            display.blit(rotated_image, self.temp_center)
        else:
            display.blit(rotated_image, self.rect.center)
        # print(self.distanceL, self.distanceR)
        self.compute_pos_sensors()
        if self.distanceL is not None:
            pygame.draw.line(display, (255, 0, 0), self.front_left, self.impactL)
        if self.distanceR is not None:
            pygame.draw.line(display, (255, 0, 0), self.front_right, self.impactR)
        if self.distanceBackL is not None:
            pygame.draw.line(display, (255, 0, 0), self.back_left, self.impactBackL)
        if self.distanceBackR is not None:
            pygame.draw.line(display, (255, 0, 0), self.back_right, self.impactBackR)
        if self.distanceFL is not None:
            pygame.draw.line(display, (255, 0, 0), self.front_left, self.impactFL)
        if self.distanceFR is not None:
            pygame.draw.line(display, (255, 0, 0), self.front_right, self.impactFR)
        if self.distanceL45 is not None:
            pygame.draw.line(display, (255, 0, 0), self.front_left, self.impactL45)
        if self.distanceR45 is not None:
            pygame.draw.line(display, (255, 0, 0), self.front_right, self.impactR45)

    def cal_speed(self):
        
        self.speed_controller.input['deviation'] = 100.0*self.distanceR /(self.distanceL+self.distanceR)
        self.speed_controller.input['lightstatus'] = self.redlight_time
        self.speed_controller.input['distance'] = min(100, self.redlight_distance)
        self.speed_controller.compute()
        # self.speed = min(self.speed, 3*self.speed_controller.output['speed']/100)
        self.speed = 3*self.speed_controller.output['speed']/100
        print(self.redlight_distance, self.speed)
        # print(self.time2changeRedlight, self.distanceRedLight, self.speed

    def update(self, display):
        #
        self.compute_pos_sensors()
        if self.road_idx+1==len(self.routes):
            return False
        self.sensor_redlight()
        self.compute_distance()
        # self.cal_speed()
        angle = self.cal_steering_angle()
        self.rotate(angle)
        self.move_forward()
        self.draw(display)
        return True
    
    def cal_steering_angle(self):
        print(100.0*self.distanceR45 /(self.distanceR45+self.distanceL45))
        self.steering_controller.input['deviation45'] = 100.0*self.distanceR45 /(self.distanceR45+self.distanceL45)
        # self.steering_controller.input['deviation'] = 100.0*self.distanceR /(self.distanceR+self.distanceL)
        # self.steering_controller.input['deviation_back'] = 100.0*self.distanceBackR /(self.distanceBackL+self.distanceBackR)
        self.steering_controller.compute()
        # steering = math.radians(self.steering_controller.output['steering']-180)/900
        # print(steering)
        steering = 5*math.pi*(self.steering_controller.output['steering']-45)/(180*50)
        # steering 
        return steering

    def move_forward(self):
        s = self.speed
        curCenterX, curCenterY = self.rect.center
        newCenterX, newCenterY = int(curCenterX + s*math.cos(self.angle)), int(curCenterY - s*math.sin(self.angle))
        self.rect.center = (newCenterX, newCenterY)

    def compute_distance(self):
        distances, impacts = distance_to_borders(self.front_left, self.front_right, self.back_left, self.back_right, self.meanUpperMid, self.virtual_map.map)
        self.distanceL, self.distanceR, self.distanceBackL, self.distanceBackR, self.distanceL45, self.distanceR45 = distances
        self.impactL, self.impactR, self.impactBackL, self.impactBackR, self.impactL45, self.impactR45 = impacts
        self.distanceFL, self.distanceFR, self.impactFL, self.impactFR = distance_to_obstacles(self.front_left, 
            self.front_right, self.back_left, self.back_right, self.virtual_map.map)
    
    def find_location(self):
        for i, road in enumerate(self.routes):
            if i < self.road_idx:
                continue
            if road.include(self.rect.left, self.rect.top):
                return i
        # print(self.redlight_distance)
        # if self.road_idx +1 < len(self.routes):
        #     return self.road_idx+1
        return self.road_idx

    @staticmethod 
    def find_common_vertex(road1, road2):
        common_vertex = [pts for pts in road1.points if pts in road2.points ]
        print(len(common_vertex))
        return common_vertex

    def sensor_redlight(self):
        # TODO: check at the end of routes
        self.road_idx = self.find_location()
        
        if self.road_idx == -1:
            raise "Out of map"
        for i in range(self.road_idx+1, len(self.routes)):
            if self.routes[i].type == 'intersection':
                self.next_intersection_idx = i
                self.next_intersection = self.routes[i]
                break

        common_vertex = self.find_common_vertex(self.routes[self.next_intersection_idx-1], self.next_intersection)
        # print(self.routes[self.road_idx].type, self.next_intersection.type)
        try:
            self.next_redlight_location = [(common_vertex[0][0]+common_vertex[1][0])/2, (common_vertex[0][1]+common_vertex[1][1])/2]
        except:
            import pdb; pdb.set_trace()
        self.redlight_distance = euclide_distance(self.upperMid, self.next_redlight_location)
        self.redlight_time = self.next_intersection.count 


def main():

    pygame.init()
    clock = pygame.time.Clock()
    mapW = 2000
    mapH = 1000
    virtual_map = Map(mapW, mapH)

    DISPLAY=pygame.display.set_mode((mapW,mapH),0,32)

    WHITE=(255,255,255)
    BLUE=(0,0,255)
    RED=(255,0,0)

    
    # road1 = Road([0,0], [50,0], [50, 200] , [0,200])
    # road2 = Road([0,200], [50,200], [50,250], [0,250], "intersection", TIME)
    # road3 = Road([50,200], [300, 200],[300,250], [50,250])
    # road4 = Road([300,200], [350, 200], [350,250], [300,250], "intersection", TIME)
    # road5 = Road([300,200], [350,200], [50, 0], [50,50])
    # roads = [road1, road2, road3, road4, road5]
    TIME=100
    roads = [
        Road([36,74], [72,74], [72, 104] , [36,104], "intersection", TIME),
        Road([72,74], [172, 74], [172, 104] , [72,104]),
        Road([172,74], [203, 74], [203, 104] , [172,104], "intersection", TIME),
        Road([203,74], [524, 74], [524, 104] , [203,104]),
        Road([524,74], [563, 74], [563, 104] , [524,104], "intersection", TIME),
        Road([563,74], [713, 74], [713, 104] , [563,104]),
        Road([713,74], [748, 74], [748, 104] , [713,104], "intersection", TIME),
        Road([36,104], [72, 104], [72, 193] , [36,193]),
        Road([36,193], [72, 193], [72, 225] , [36,225], "intersection", TIME),
        Road([72,193], [172, 193], [172, 225] , [72,225]),
        Road([172,104], [203, 104], [203, 193] , [172,193]),
        Road([172,193], [203, 193], [203, 225] , [172,225], "intersection", TIME),
        Road([203,193], [293, 192], [289, 227] , [203,225]),
        Road([293,192], [364, 205], [358, 238] , [289,227]),
        Road([364,205], [401, 212], [397, 246] , [358,238], "intersection", TIME),
        Road([401,212], [481, 224], [460, 258] , [397,246]),
        Road([481,224], [506, 251], [474, 269] , [460,258], "intersection", TIME),
        Road([506,251], [550, 303], [528, 323] , [474,269]),
        Road([550,303], [574, 328], [543, 343] , [528,323], "intersection", TIME),
        Road([481,224], [506, 251], [565, 195] , [530,178]),
        Road([530,178], [565, 195], [563,104], [524, 104]),
        Road([550,303], [574, 328], [636,270], [615, 246]),
        Road([636,270], [615, 246], [713,243], [713, 269]),
        Road([713,243], [748, 243], [748,269], [713, 269], "intersection", TIME),
        Road([713,104], [748, 104], [748,243], [713, 243]),
        Road([713,269], [748, 269], [748,500], [713, 500]),
        Road([713,500], [748, 500], [748,534], [713, 534], "intersection", TIME),
        Road([580,500], [713, 500], [713,534], [580, 534]),
        Road([545,500], [580, 500], [580,534], [545, 534], "intersection", TIME),
        Road([543,343], [574, 328], [580,500], [545, 500]),
        Road([348,500], [545, 500], [545,534], [348, 534]),
        Road([312,500], [348, 500], [348,534], [312, 534], "intersection", TIME),
        Road([200,500], [312, 500], [312,534], [200, 534]),
        Road([172,500], [200, 500], [200,534], [172, 534], "intersection", TIME),
        Road([74,500], [172, 500], [172,534], [74, 534]),
        Road([42,500], [74, 500], [74,534], [42, 534], "intersection", TIME),
        Road([36,225], [72, 225], [74,500], [42, 500]),
        Road([172,225], [203, 225], [203,363], [172, 363]),
        Road([172,363], [203, 363], [203,390], [172, 390], "intersection", TIME),
        Road([172,390], [203, 390], [200,500], [172, 500]),
        Road([203,363], [310, 357], [313,389], [203, 390]),
        Road([310,357], [345, 359], [346,386], [313, 389], "intersection", TIME),
        Road([313,389], [346, 386], [348,500], [312, 500]),
        Road([358,238], [397, 246], [345, 359], [310,357]),
    ]
    
    routes  = []
    route_picked = False

    # obstacles
    obstacles = []

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
                car = Car(mousex,mousey,20,10, steering_controller, speed_controller,virtual_map ,routes)
                car.draw(DISPLAY)
                car_pick=True
        if car_pick:
            break
        pygame.display.update()


    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                pos = pygame.mouse.get_pos()
                obstacle = init_obstacle_from_pos(pos)
                obstacles.append(obstacle)
                # update virtual map
                virtual_map.drawObstacle([obstacle])

        DISPLAY.fill(WHITE)
        for road in roads:
            road.update()
            road.draw(DISPLAY)
        for obstacle in obstacles:
            obstacle.draw(DISPLAY)
        
        car.sensor_redlight()
        updated = car.update(DISPLAY)
        if not updated:
            break
        # print(car.redlight_distance, car.redlight_time)
        car.draw(DISPLAY)    
        pygame.display.update()
    print("Done")

main()