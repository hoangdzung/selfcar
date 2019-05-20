import numpy as np 
import cv2
from utils import CHOICE_ROAD

class Map():
    def __init__(self, w, h):
        self.map = np.zeros((w, h))
        
    def drawRoutes(self, routes):
        for road in routes:
            print(np.array(road.points).astype(np.int32).shape)
            cv2.fillPoly(self.map, pts=[np.array(road.points).astype(np.int32)], color=(CHOICE_ROAD))
        cv2.imwrite('routes.png', self.map*255)