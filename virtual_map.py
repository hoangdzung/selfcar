import numpy as np 
import cv2
from utils import CHOICE_ROAD

class Map():
    def __init__(self, w, h):
        self.map = np.zeros((w, h))
        
    def drawRoutes(self, routes):
        for road in routes:
            cv2.fillPoly(self.map, pts=road.points, color=(CHOICE_ROAD))
        cv2.imwrite('routes.png', self.map)