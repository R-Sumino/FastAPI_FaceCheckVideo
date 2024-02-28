# camera_multi.py

import cv2
from base_camera import BaseCamera
from detect import MTCNN_detect


class VideoCamera(BaseCamera):
    
    def __init__(self):
        super().__init__()

    # over-wride of BaseCamera class frames method
    @classmethod
    def frames(cls):
        print("cls.url_tmp : ", cls.url_tmp)
        camera = cv2.VideoCapture(cls.url_tmp)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')
        
        while True:
            # read current frame
            _, img = camera.read()
        
            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()

'''
    # over-wride of BaseCamera class frames method
    @classmethod
    def frames(cls):
        print("cls.url_tmp : ", cls.url_tmp)
        camera = cv2.VideoCapture(cls.url_tmp)
        detect = MTCNN_detect()
        frame_count = 0
        count = 1
        camera.set(cv2.CAP_PROP_FPS, 15)
        print(camera.get(cv2.CAP_PROP_FPS))
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()
            frame_count += 1
            if frame_count % 2  == 0:
                frame_count = 0
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = detect.Rec_draw(img)
                # encode as a jpeg image and return it
                yield cv2.imencode('.jpg', img)[1].tobytes()
'''
