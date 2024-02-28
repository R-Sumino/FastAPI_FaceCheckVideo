# -*- coding: utf-8 -*-

from typing import Union
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

import io
import sys
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

NO_NAME = '未登録'
FONT_PATH = "C:\WINDOWS\FONTS\MEIRYO.TTC"
FONT_SIZE = 12

class MTCNN_detect(object):
    def __init__(self) -> None:
        #self.mtcnn = MTCNN(select_largest=True)
        self.mtcnn = MTCNN()
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval()
    
    
    # ------------------------------------------------------
    # 顔の検出
    # flag -> True : 顔の座標のみ返り値
    #   |
    #   ----> False: 顔の座標と切り抜き顔データが返り値
    # ------------------------------------------------------
    def Detect(self, frame: np.uint8) -> Union[np.float32, np.float32]:
        boxes, probs, points = self.mtcnn.detect(frame, landmarks=True)
        return boxes
    
    
    
    # ------------------------------------------------------
    # 画像から顔を切り抜き
    # ------------------------------------------------------
    def Crop(self, img: np.uint8) -> Union[np.uint8, np.float32, np.float32]:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        boxes = self.Detect(img)
        face = self.mtcnn.extract(img, boxes, None)
        
        if(boxes is not None):
            img = img.crop(boxes[0].tolist())
            embedding = self.resnet(face.unsqueeze(0))
            np_embedding = embedding.to('cpu').detach().numpy().copy()
        else :
            np_embedding = None
        
        img = self.Chage(img)
        return img, face, np_embedding
    
    
    
    # ------------------------------------------------------
    # 顔を四角で囲むように描画、登録者であるかの可否
    # ------------------------------------------------------
    def Rec_draw(self, frame: np.uint8, id_vector, id_name) -> np.uint8:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        draw = ImageDraw.Draw(img, mode="RGBA")
        boxes = self.Detect(frame)
        name = NO_NAME
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        
        if(boxes is not None):
            crop = self.mtcnn.extract(img, boxes, None)
            embedding = self.resnet(crop.unsqueeze(0))
            np_embedding = embedding.to('cpu').detach().numpy().copy()
            
            
            result = 0
            id = -1
            for id_vec in id_vector:
                emb = np_embedding.squeeze()
                vec = np.frombuffer(id_vec[1], np.float32).reshape(1,512)
                check = np.dot(vec, emb) / (np.linalg.norm(vec) * np.linalg.norm(emb))
                if check >= 0.7:
                    result = check
                    id = id_vec[0]
            
            for id_na in id_name:
                if id == id_na[0]:
                    name = id_na[1]
                    break
                    
            xs, ys, xe, ye = boxes[0]
            if id < 0:
                color = 'red'
            else :
                color = 'green'
                
            draw.rectangle(boxes[0].tolist(), width=3, outline=color)
            draw.rectangle((xs, ye, xe, ye + 15), fill=color)
            draw.text((xs + 3, ye), name, font=font)
            if name != NO_NAME:
                draw.rectangle((xs, ye + 15, xe, ye + 30), fill=color)
                draw.text((xe - 30, ye + 12), str(int(result*100)) + "%", font=font)
        
        
        img = self.Chage(img)
        return img
    
    
    
    # ------------------------------------------------------
    # PIL -> OpenCV に変換
    # ------------------------------------------------------
    def Chage(self, image: Image) -> np.uint8:
        new_image = np.array(image, dtype=np.uint8)

        if new_image.ndim == 2:  # モノクロ
            pass
        elif new_image.shape[2] == 3:  # カラー
            new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
        elif new_image.shape[2] == 4:  # 透過
            new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
                
        return new_image
