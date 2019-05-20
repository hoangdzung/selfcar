import math

CHOICE_ROAD = 1
OBSTACLE = 2

def euclide_distance(pts1, pts2):
    return math.sqrt((pts1[0]-pts2[0])**2+(pts1[1]-pts2[1])**2)