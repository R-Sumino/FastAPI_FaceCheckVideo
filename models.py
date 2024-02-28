from datetime import datetime
from db import Base

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN, VARBINARY

import hashlib

SQLITE3_NAME = "./db.sqlite3"

CAMERA_NAME = 'cameraname'
CAMERA_URL = 'url'
CAMERA_LOCATION = 'location'

USER_NUMBER = 'number'
USER_NAME = 'username'
USER_MAIL = 'mail'

USERDATA_PATH = 'path'
USERDATA_HASH = 'hash'
USERDATA_VECTOR = 'vector'
USERDATA_TIME = 'data'

# ------------------------------------------------------
# カメラ用データベーステーブル
# ------------------------------------------------------
class Camera(Base):
    """
    Cameraテーブル
    
    id          ：主キー
    cameraname  ：カメラ名称
    url         ：IPカメラのURL or DviceID
    location    ：カメラの設置場所
    date        ：登録日時
    change_time ：変更日時
    """
    __tablename__ = 'camera'
    id = Column(
        'id',
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True
    )
    cameraname = Column('cameraname', String(256))
    url = Column('url', Text)
    location = Column('location', String)
    """
    date = Column(
        'date', 
        String, 
        default=datetime.now(), 
        nullable=False, 
        server_default=current_timestamp()
    )
    change_time = Column(
        'date',
        String,
        default=datetime.now(),
        server_default=current_timestamp()
    )
    """
    
    def __init__(self, cameraname: str, url: str, location: str) -> None:
        self.cameraname = cameraname
        self.url = url
        self.location = location
        
    def __str__(self) -> str:
        return str(self.id) + \
            ': \nCamera Name -> ' + self.cameraname + "type -> " + type(self.cameraname) + \
            ', \nURL or Device_Number -> ' + self.url + "type -> " + type(self.url) + \
            ', \nLocation -> ' + self.location + "type -> " + type(self.location)
    
    
# ------------------------------------------------------
# ユーザ用データベーステーブル
# ------------------------------------------------------
class User(Base):
    """
    Userテーブル
    
    id          ：主キー
    number      ：社員番号
    username    ：ユーザーネーム
    mail        ：メールアドレス
    regist_num  ：登録データ画像の枚数
    """
    __tablename__ = 'user'
    id = Column(
        'id',
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )
    number = Column('number', String(256))
    username = Column('username', String(256))
    mail = Column('mail', String(256))
    regist_num = Column('regist_num', INTEGER(unsigned=True))
    
    def __init__(self, number: str, username: str, mail: str, regist_num: int) -> None:
        self.number = number
        self.username = username
        self.mail = mail
        self.regist_num = regist_num
    
    def __str__(self) -> str:
        return str(self.id) + \
            ': Number -> ' + self.number + "type -> " + type(self.number) + \
            ', \nUser Name -> ' + self.username + "type -> " + type(self.username) + \
            ', \nMail -> ' + self.mail + "type -> " + type(self.mail) + \
            ', \nRegistImage_Quantity -> ' + self.regist_num + "type -> " + type(self.regist_num)
    
    
# ------------------------------------------------------
# ユーザデータ用データベーステーブル
# ------------------------------------------------------
class User_Data(Base):
    """
    Regist_Data（顔写真登録）テーブル
    
    id          ：主キー
    user_id     ：外部キー
    path        ：画像パス
    hash        ：ハッシュ値
    vector      ：特徴ベクトル
    date        ：登録日時
    change_time ：変更日時
    """
    __tablename__ = 'registdata'
    id = Column(
        'id',
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )
    
    user_id = Column('user_id', ForeignKey('user.id'))
    path = Column('path', String)
    hash = Column('hash', VARBINARY)
    vector = Column('vector', VARBINARY)
    date = Column(
        'date', 
        String, 
        default=datetime.now(), 
        nullable=False, 
        server_default=current_timestamp()
    )
    """
    change_time = Column(
        'date',
        String,
        default=datetime.now(),
        server_default=current_timestamp()
    )
    """
    

    def __init__(self, user_id: int, path: str, hash, vector, date: datetime = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')) -> None:
        self.user_id = user_id
        self.path = path
        self.hash = hash
        self.vector = vector
        self.date = date
        
    
    def __str__(self) -> str:
        return str(self.id) + \
            ': User ID -> ' + str(self.user_id) + "type -> " + type(self.user_id) + \
            ', \nPath -> ' + str(self.path) + "type -> " + type(self.path) + \
            ', \nDateTime -> ' + str(self.date) + "type -> " + type(self.data)
    
