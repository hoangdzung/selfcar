import numpy as np
import math
from utils import CHOICE_ROAD, euclide_distance, OBSTACLE

def linear_function(x1, y1, x2, y2):
    get_x = None
    get_y = None
    if x1 == x2:  # x = b
        b = x1
        k = np.inf  # assume k = inf

        def get_x(yy): return b
        # can't get y when given x
    else:  # y = kx + b
        k = (y1-y2) / (x1-x2)
        b = y1 - k*x1

        def get_x(yy): return None if k == 0 else (yy-b)/k

        def get_y(xx): return k*xx + b
    return k, b, get_x, get_y

def distance_to_borders(sensorL, sensorR, UL, UR, center, virtual_map):
    """
    sensorL: position of left sensor
    sensorR: position of right sensor
    UL: lower left position of car
    UR: lower right position of car
    init_angle: angle between sensorL with x axis, in radians format
    rotation angle: in radians format
    """
    x1, y1 = sensorL
    x2, y2 = sensorR
    k, b, get_x, get_y = linear_function(x1, y1, x2, y2)

    distanceL, impactL = search_for_impact(k, b, get_x, get_y, x2, y2, x1, y1, virtual_map)
    distanceR, impactR = search_for_impact(k, b, get_x, get_y, x1, y1, x2, y2, virtual_map)
    
    # back
    x3, y3 = UL
    x4, y4 = UR
    k, b, get_x, get_y = linear_function(x3, y3, x4, y4)

    distanceBackL, impactBackL = search_for_impact(k, b, get_x, get_y, x4, y4, x3, y3, virtual_map)
    distanceBackR, impactBackR = search_for_impact(k, b, get_x, get_y, x3, y3, x4, y4, virtual_map)

    # front nearly 45degree
    x5,y5 = center
    k, b, get_x, get_y = linear_function(x5, y5, x1, y1)
    distanceL45, impactL45 = search_for_impact(k, b, get_x, get_y, x5, y5, x1, y1, virtual_map)
    k, b, get_x, get_y = linear_function(x5, y5, x2, y2)
    distanceR45, impactR45 = search_for_impact(k, b, get_x, get_y, x5, y5, x2, y2, virtual_map)

    distances= [distanceL, distanceR, distanceBackL, distanceBackR, distanceL45, distanceR45]
    impacts = [impactL, impactR, impactBackL, impactBackR, impactL45, impactR45]
    return distances, impacts

def distance_to_obstacles(sensorL, sensorR, LL, LR, virtual_map):
    """
    sensorL: position of left sensor
    sensorR: position of right sensor
    LL: lower left position of car
    LR: lower right position of car
    init_angle: angle between sensorL with x axis, in radians format
    rotation angle: in radians format
    """
    x1, y1 = sensorL
    x2, y2 = sensorR
    x3, y3 = LL
    x4, y4 = LR
    k1, b1, get_x1, get_y1 = linear_function(x1, y1, x3, y3)
    distanceForwardL, impactForwardL = search_for_impact_obstacles(k1, b1, get_x1, get_y1, x3, y3, x1, y1, virtual_map)
    k2, b2, get_x2, get_y2 = linear_function(x2, y2, x4, y4)
    distanceForwardR, impactForwardR = search_for_impact_obstacles(k2, b2, get_x2, get_y2, x4, y4, x2, y2, virtual_map)
    
    return distanceForwardL, distanceForwardR, impactForwardL, impactForwardR

def search_for_impact(k, b, get_x, get_y, x1, y1, x2, y2, mapp, values=[1]):
    """
    search with direction from (x1,y1) -> (x2, y2) ->
    start from x2, y2
    """
    abs_k = abs(k)
    # search for x or y axis,  then find increase or decrease
    x_impact = None
    y_impact = None
    if abs_k >= 0 and abs_k <= 1:  # find in x axis
        if x1 >= x2:  # decrease x, because x_impact <= x2
            x_impact = x2 - 1
            while True:
                y_impact = get_y(x_impact)
                # check if x_impact, y_impact is border
                try:
                    if x_impact < 0 or y_impact < 0:
                        # x_impact, y_impact = None, None
                        break
                    if mapp[int(y_impact), int(x_impact)] not in values:
                        break
                except:
                    # x_impact, y_impact = None, None
                    break
                x_impact -= 1
        else:
            x_impact = x2 + 1
            while True:
                y_impact = get_y(x_impact)
                # check if x_impact, y_impact is border
                try:
                    if x_impact < 0 or y_impact < 0:
                        # x_impact, y_impact = None, None
                        break
                    if mapp[int(y_impact), int(x_impact)] not in values:
                        break
                except:
                    # x_impact, y_impact = None, None
                    break
                x_impact += 1
    else:  # find in y axis
        if y1 >= y2:  # decrease y, because y_impact <= y2
            y_impact = y2 - 1
            while True:
                x_impact = get_x(y_impact)
                try:
                    if x_impact < 0 or y_impact < 0:
                        # x_impact, y_impact = None, None
                        break
                    if mapp[int(y_impact), int(x_impact)] not in values:
                        break
                except:
                    # x_impact, y_impact = None, None
                    break
                y_impact -= 1
        else:
            y_impact = y2 + 1
            while True:
                x_impact = get_x(y_impact)
                try:
                    if x_impact < 0 or y_impact < 0:
                        # x_impact, y_impact = None, None
                        break
                    if mapp[int(y_impact), int(x_impact)] not in values:
                        break
                except:
                    # x_impact, y_impact = None, None
                    break
                y_impact += 1

    if x_impact is not None and y_impact is not None:
        x_impact = int(x_impact)
        y_impact = int(y_impact)
        distance = euclide_distance((x_impact, y_impact), (x2, y2))
        impact = (x_impact, y_impact)
        return distance, impact
    return None, (None, None)

def search_for_impact_obstacles(k, b, get_x, get_y, x1, y1, x2, y2, mapp):
    """
    search with direction from (x1,y1) -> (x2, y2) ->
    start from x2, y2
    """
    abs_k = abs(k)
    # search for x or y axis,  then find increase or decrease
    x_impact = None
    y_impact = None
    if abs_k >= 0 and abs_k <= 1:  # find in x axis
        if x1 >= x2:  # decrease x, because x_impact <= x2
            x_impact = x2 - 1
            while True:
                y_impact = get_y(x_impact)
                # check if x_impact, y_impact is border
                try:
                    if x_impact < 0 or y_impact < 0:
                        # x_impact, y_impact = None, None
                        break
                    if mapp[int(y_impact), int(x_impact)] == OBSTACLE or mapp[int(y_impact), int(x_impact)] != CHOICE_ROAD:
                        break
                except:
                    # x_impact, y_impact = None, None
                    break
                x_impact -= 1
        else:
            x_impact = x2 + 1
            while True:
                y_impact = get_y(x_impact)
                # check if x_impact, y_impact is border
                try:
                    if x_impact < 0 or y_impact < 0:
                        # x_impact, y_impact = None, None
                        break
                    if mapp[int(y_impact), int(x_impact)] == OBSTACLE or mapp[int(y_impact), int(x_impact)] != CHOICE_ROAD:
                        break
                except:
                    # x_impact, y_impact = None, None
                    break
                x_impact += 1
    else:  # find in y axis
        if y1 >= y2:  # decrease y, because y_impact <= y2
            y_impact = y2 - 1
            while True:
                x_impact = get_x(y_impact)
                try:
                    if x_impact < 0 or y_impact < 0:
                        # x_impact, y_impact = None, None
                        break
                    if mapp[int(y_impact), int(x_impact)] == OBSTACLE or mapp[int(y_impact), int(x_impact)] != CHOICE_ROAD:
                        break
                except:
                    # x_impact, y_impact = None, None
                    break
                y_impact -= 1
        else:
            y_impact = y2 + 1
            while True:
                x_impact = get_x(y_impact)
                try:
                    if x_impact < 0 or y_impact < 0:
                        # x_impact, y_impact = None, None
                        break
                    if mapp[int(y_impact), int(x_impact)] == OBSTACLE or mapp[int(y_impact), int(x_impact)] != CHOICE_ROAD:
                        break
                except:
                    # x_impact, y_impact = None, None
                    break
                y_impact += 1

    if x_impact is not None and y_impact is not None:
        x_impact = int(x_impact)
        y_impact = int(y_impact)
        distance = euclide_distance((x_impact, y_impact), (x2, y2))
        impact = (x_impact, y_impact)
        return distance, impact
    return None, (None, None)

