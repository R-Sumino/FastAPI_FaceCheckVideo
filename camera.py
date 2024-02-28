# camera.py

import cv2
from detect import MTCNN_detect
import time

class VideoCamera(object):
    def __init__(self, url):
        self.video = cv2.VideoCapture(url)
        self.detect = MTCNN_detect()
        self.frame_count = 0
        
        

    def __del__(self):
        self.video.release()
    '''
    # 原本
    def get_frame(self):
        if not self.video.isOpened():
            raise RuntimeError('Could not start camera.')
        
        while True:
            _, image = self.video.read()
            image = cv2.resize(image, dsize=(640, 360))
            ret, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()
    '''
    
    def get_frame(self, id_vector, id_name):
        if not self.video.isOpened():
            raise RuntimeError('Could not start camera.')
        
        while True:
            _, frame = self.video.read()
            frame = cv2.resize(frame, dsize=(640, 360))
            frame = cv2.flip(frame, 1)
            self.frame_count += 1
            if self.frame_count % 5 == 0:
                self.frame_count = 0
                image = self.detect.Rec_draw(frame, id_vector, id_name)
                
                ret, jpeg = cv2.imencode('.jpg', image)
                return jpeg.tobytes()
            
