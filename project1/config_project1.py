from cv2 import cv2
import numpy as np
import os
import time
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 


YOLO_CONFIG = r"project1/src/yolo/yolov4-tiny-custom.cfg"
YOLO_WEIGHT = r"project1/src/yolo/yolov4-tiny-custom_last.weights"
YOLO_CLASSES = r"project1/src/yolo/obj.names"

MODEL = r"project1/Model/my_model.h5"
WEIGHTS= r"project1/Model/my_model_weights.h5"
LABEL_DATA = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C','D', 'E', 'F', 'G', 'H', 'K', 'L', 'M', 'N', 'P', 'R', 'S', 'T', 'U', 'V', 'X', 'Y', 'Z', 'None']

WIDTH_IMG = 800
HEIGHT_IMG = 600
SIZE_IMAGE = (WIDTH_IMG, HEIGHT_IMG)

WIDTH_YOLO = 300
HEIGHT_YOLO = 200
SIZE_YOLO = (WIDTH_YOLO, HEIGHT_YOLO)