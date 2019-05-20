from utils import OBSTACLE
import imutils
import pygame
import cv2
import numpy as np

class Obstacle:
    def __init__(self, pts):
        self.pts = pts

    def draw(self, display):
        pygame.draw.polygon(display, (0, 0, 0), self.pts.reshape(-1,2))

def init_obstacle_from_pos(pos):
    radius = 5
    h,w = pos
    pts = np.array([
        [[h-radius, w-radius]],
        [[h-radius, w+radius]],
        [[h+radius, w+radius]],
        [[h+radius, w-radius]]
    ]).astype(np.int32)
    obstacle = Obstacle(pts)
    return obstacle
