# -*- coding: utf-8 -*-

from fastapi import FastAPI, File, UploadFile, Depends, status
# from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse

# from fastapi_login import LoginManager
# from fastapi_login.exceptions import InvalidCredentialsException

from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse, StreamingResponse, HTMLResponse

import sys
import os
import io
import cv2
import shutil
import numpy as np
import hashlib
from typing import Dict, List, Optional, Tuple, Union
import re
from datetime import datetime

import db
from models import Camera, User, User_Data

from detect import MTCNN_detect

#from camera_multi import VideoCamera
from camera import VideoCamera


# --------------------------------------------------------
# 以下、定数
# --------------------------------------------------------
CAMERA_NAME = 'cameraname'
CAMERA_TYPE = 'camera-type'
CAMERA_ID = 'camera-id'
CAMERA_URL = 'url'
CAMERA_LOCATION = 'location'

LIST_CATEGORY = 'category'
LIST_SEARCH = 'search'
LIST_SUBMIT = 'submit'

USER_NUMBER = 'number'
USER_NAME = 'username'
USER_MAIL = 'mail'

USERDATA_NUM_NAME = 'num_name'

SECRET = "secret-key"

ROUTE_PATH = sys.path[1] if 2 == len(sys.path) else '.'
STATIC_PATH = ROUTE_PATH + '/static'
TEMPLATE_PATH = ROUTE_PATH + '/templates'

# 正規表現
pattern_camera = re.compile(r'\S+')                                             # 任意の文字列を示す正規表現
pattern_url = re.compile(r'\w{4,}://[\w/:%#\$&\?\(\)~\.=\+\-]+')                # URLの正規表現

pattern_number = re.compile(r'\w{4,}')                                          # 任意の4文字以上の英数字を示す正規表現
pattern_user = re.compile(r'\w{4,20}')                                          # 任意の4~20の英数字を示す正規表現
pattern_mail = re.compile(r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$')     # e-mailの正規表現


# FastAPI の準備
app = FastAPI(
    title='顔認証システム'
)

# staticディレクトリの設定 (starlette)
# app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

# テンプレート関連の設定（Jinja2）
# templates = Jinja2Templates(directory="templates")
templates = Jinja2Templates(directory=TEMPLATE_PATH)
jinja_env = templates.env       # Jinja2.Environment : finterやglobalの設定


# パスワード認証用（未完成）
# manager = LoginManager(SECRET, token_url="/login", use_cookie=True)
# manager.cookie_name = "some-name"

stop_flag = False


"""
@manager.user_loader
def load_user(username: str):
    user = db.session.query(User).filter(User.username == username).first()
    db.session.close()
    return user



# --------------------------------------------------------
# ログイン（未完成）
# --------------------------------------------------------
def login(request: Request):
        return templates.TemplateResponse('login.html',
                                         {'request': request}) 
    
async def login_auth(request: Request, data: OAuth2PasswordRequestForm = Depends()):
    print("data: ", vars(data))
    username = data.username
    password = data.password
    
    form_data = await request.form()
    number = form_data.get('number')
    
    user = load_user(username)
    if not user:
        raise InvalidCredentialsException
    # elif password != user['password']:
        # raise InvalidCredentialsException
    elif number != user.number:
        raise InvalidCredentialsException
    access_token = manager.create_access_token(
        data={"sub": username}
    )
    print("access_token: ", access_token)
    
    if username == "admin":
        resp = RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
    else:
        resp = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    manager.set_cookie(resp, access_token)
    return resp

def logout(_=Depends(manager)):
    resp = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    manager.set_cookie(resp, "")
    return resp
"""


def admin(request: Request):
    return templates.TemplateResponse('admin.html', 
                                      {'request': request})



# --------------------------------------------------------
# Top
# --------------------------------------------------------
def index(request: Request):
    return templates.TemplateResponse('index.html', 
                                      {'request': request})



# --------------------------------------------------------
# ストリーミング
# --------------------------------------------------------
async def stream(request: Request):
    print("===== Stream Start =====\n")
    
    global stop_flag

    camera_all = db.session.query(Camera).all()
    
    # GETデータ
    if request.method == 'GET':
        db.session.close()
        print("\n===== Stream GET End =====")
        return templates.TemplateResponse('stream.html', 
                                     {"request": request,
                                      'camera_all': camera_all})
    
    # POSTデータ
    if request.method == 'POST':
        data = await request.form()
        cameraname = data.get('cameraname')
        camera = db.session.query(Camera).filter(Camera.cameraname == cameraname).first()
        db.session.close()
        #VideoCamera.stop_flag = False
        stop_flag = False
        
        print("\n===== Stream POST End =====")
        return templates.TemplateResponse('stream.html', 
                                        {"request": request,
                                        'camera_all': camera_all,
                                        'cameraname': camera.cameraname,
                                        'url': camera.url})



# --------------------------------------------------------
# カメラ映像停止
# --------------------------------------------------------
def stop(request: Request):
    global stop_flag
    #VideoCamera.stop_flag = True
    stop_flag = True
    return RedirectResponse('/stream')



# --------------------------------------------------------
# カメラ映像取得
# --------------------------------------------------------
def gen(camera):
    global stop_flag
    
    id_vector = db.session.query(User_Data.user_id, User_Data.vector).all()
    id_name = db.session.query(User.id, User.username).all()
    db.session.close()
    
    """Video streaming generator function."""
    while True:
        #if VideoCamera.stop_flag :
        if stop_flag:
            break
        frame = camera.get_frame(id_vector, id_name)
        #frame = camera.get_frame()
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'



# --------------------------------------------------------
# カメラ映像出力
# --------------------------------------------------------
def video_feed(cameraname):
    print("===== Video Feed Start =====\n")
    
    camera = db.session.query(Camera).filter(Camera.cameraname == cameraname).first()
    db.session.close()
    
    """Video streaming route. Put this in the src attribute of an img tag."""
    print("Camera Name -> ", camera.cameraname, ", type -> ", type(camera.cameraname))
    print("URL -> ", camera.url, ", type -> ", type(camera.url))
    print("Location -> ", camera.location, ", type -> ", type(camera.location))
    #VideoCamera.url_tmp = camera.url
    #print("VideoCamera().url_tmp : ", VideoCamera.url_tmp)
    
    print("\n===== Video Feed End =====")
    return  StreamingResponse(gen(VideoCamera(camera.url)),
    #return  StreamingResponse(gen(VideoCamera()),
                    media_type='multipart/x-mixed-replace; boundary=frame')



# --------------------------------------------------------
# カメラ登録
# --------------------------------------------------------
async def register_camera(request: Request):
    print("===== Register Camera Start =====\n")
    
    # GETデータ
    if request.method == 'GET':
        print("\n===== Register Camera GET End =====")
        return templates.TemplateResponse('register_camera.html',
                                          {'request': request,
                                           'camera': '',
                                           'error': []})
    
    # POSTデータ
    if request.method == 'POST':
        data = await request.form()
        cameraname = data.get('cameraname')
        camera_type = data.get('camera-type')
        if camera_type == "Web":
            url = data.get('camera-id')
        elif camera_type == "IP":
            url = data.get('url')
        location = data.get('location')
        
        error = []
        
        tmp_camera = db.session.query(Camera).filter(Camera.cameraname == cameraname).first()
        tmp_url = db.session.query(Camera).filter(Camera.url == url).first()
        
        # エラー処理
        if tmp_camera is not None:
            error.append("同じカメラ名称が存在します。")
        if tmp_url is not None:
            error.append("同じURLもしくは同じ接続番号が存在します。")
        if pattern_camera.match(cameraname) is None:
            error.append("カメラの名称を入力してください。")
        if url == "":
            error.append("URLもしくは接続番号が入力されていません。")
        elif camera_type == "IP":
            if pattern_url.match(url) is None:
                error.append("正しくURLを入力してください。")
        
        
        
        if error:
            db.session.close()
            print("\n===== Register Camera POST verError End =====")
            return templates.TemplateResponse('register_camera.html', 
                                              {'request': request,
                                               'cameraname': cameraname,
                                               'error': error})
            
        # 問題が無ければカメラ登録
        camera = Camera(cameraname, url, location)
        db.session.add(camera)
        db.session.commit()
        db.session.close()
        
        print("\n===== Register Camera POST verSafety End =====")
        return templates.TemplateResponse('complete_camera.html',
                                          {'request': request,
                                           'cameraname': cameraname,
                                           'url': url})



# --------------------------------------------------------
# 登録カメラ情報の一覧
# --------------------------------------------------------
async def list_camera(request: Request):
    print("===== Camera List Start =====\n")
    
    camera = db.session.query(Camera).all()
    db.session.close()
    
    data = await request.form()
    category = data.get('category')
    search = data.get('search')
    submit = data.get('submit')
    
    # DB からキーワードにヒットするものを検索
    error = []
    print("submit -> ", submit, ", type -> ", type(submit))
    print("search -> ", search, ", type -> ", type(search))
    print("category -> ", category, ", type -> ", type(category))
    if submit == "検索":
        data_list = []
        data_list = list_search(search, category, camera)
        
        if data_list:
            camera = data_list
        elif search == "":
            error.append("キーワードを入力してください。")
        else:
            error.append("一致する検索結果がありませんでした。")
    
    print("\n===== Camera List End =====")
    return templates.TemplateResponse('list_camera.html',
                                      {'request': request,
                                       'error': error,
                                       'camera': camera,
                                       'all_path': 'list_camera'})



# --------------------------------------------------------
# 登録カメラ情報の削除
# --------------------------------------------------------
def delete_camera(c_id):
    print("===== Camera Delete Start =====\n")
    # 該当カメラ情報を取得
    camera = db.session.query(Camera).filter(Camera.id == c_id).first()
    
    # 削除してコミット
    db.session.delete(camera)
    db.session.commit()
    db.session.close()
    
    print("\n===== Camera Delere End =====")
    return RedirectResponse('/list_camera')



# --------------------------------------------------------
# ユーザ情報登録
# --------------------------------------------------------
async def register_user(request: Request):
    print("===== Register User Start =====\n")
    
    if request.method == 'GET':
        print("\n===== Register User GET End =====")
        return templates.TemplateResponse('register_user.html',
                                          {'request': request,
                                           'username': '',
                                           'error': []})
    
    # POSTデータ
    if request.method == 'POST':
        data = await request.form()
        print("data: ", data)
        number = data.get('number')
        username = data.get('username')
        mail = data.get('mail')
        
        error = []
        
        tmp_number = db.session.query(User).filter(User.number == number).first()
        tmp_mail = db.session.query(User).filter(User.mail == mail).first()
        
        # 怒涛のエラー処理
        if tmp_number is not None:
            error.append('同じ社員番号のユーザが存在します。')
        if pattern_number.match(number) is None:
            error.append('正しく社員番号を入力してください。')
        if pattern_user.match(username) is None:
            error.append('ユーザ名は４～２０文字の半角英数字にしてください。')
        if tmp_mail is not None:
            error.append('同じメールアドレスが存在します。')
        if pattern_mail.match(mail) is None:
            error.append('正しくメールアドレスを入力してください。')
            
        # エラーがあれば登録ページへ戻す
        if error:
            print("\n===== Register User verError End =====")
            return templates.TemplateResponse('register_user.html',
                                              {'request': request,
                                               'number': number,
                                               'username': username,
                                               'error': error})
            
        # 問題が無ければユーザ登録
        user = User(number, username, mail, regist_num=0)
        db.session.add(user)
        db.session.commit()
        db.session.close()
        
        print("\n===== Register User verSafety End =====")
        return templates.TemplateResponse('complete_user.html',
                                          {'request': request,
                                           'number': number,
                                           'username': username})



# --------------------------------------------------------
# 登録ユーザ情報の一覧
# --------------------------------------------------------
async def list_user(request: Request):
    print("===== User List Start =====\n")
    
    user = db.session.query(User).all()
    
    data = await request.form()
    category = data.get('category')
    search = data.get('search')
    submit = data.get('submit')
    
    # 登録画像枚数の再確認および訂正
    for u in user:
        dir = f'./files/{u.number}_{u.username}'
        if os.path.exists(dir):
            u.regist_num = sum(os.path.isfile(os.path.join(dir, name)) for name in os.listdir(dir))
        else :
            u.regist_num = 0
    
    # DB からキーワードにヒットするものを検索
    error = []
    print("submit -> ", submit, ", type -> ", type(submit))
    print("search -> ", search, ", type -> ", type(search))
    print("category -> ", category, ", type -> ", type(category))
    if submit == "検索":
        data_list = []
        data_list = list_search(search, category, user)
        
        if data_list:
            user = data_list
        elif search == "":
            error.append("キーワードを入力してください。")
        else:
            error.append("一致する検索結果がありませんでした。")
    
    
    db.session.commit()
    db.session.close()    
    
    print("\n===== User List End =====")
    return templates.TemplateResponse('list_user.html',
                                      {'request': request,
                                       'error': error,
                                       'user': user})



# --------------------------------------------------------
# 登録ユーザ情報の削除
# --------------------------------------------------------
def delete_user(u_id):
    print("===== User Delete Start =====\n")
    
    # 該当ユーザ情報を取得
    user = db.session.query(User).filter(User.id == u_id).first()
    db.session.query(User_Data).filter(User_Data.user_id == user.id).delete()
    
    # 社員番号_名前のフォルダがあればフォルダの中身ごとフォルダを削除
    if f'{user.number}_{user.username}' in os.listdir(f'./files/'):
        shutil.rmtree(f'./files/{user.number}_{user.username}/')
    
    # 削除してコミット
    db.session.delete(user)
    db.session.commit()
    db.session.close()
    
    print("\n===== User Delete End =====")
    return RedirectResponse('/list_user')



# --------------------------------------------------------
# ユーザに対しての顔画像登録（GET時）
# --------------------------------------------------------
def register_data(request: Request):
    print("===== Register Data Start =====\n")
    
    user = db.session.query(User).all()
    db.session.close()
    
    print("\n===== Register Data GET End =====")
    return templates.TemplateResponse('register_data.html',
                                      {'request': request,
                                       'user': user})



# --------------------------------------------------------
# 画像読み込み、顔検出、顔切り出し
# --------------------------------------------------------
def read_image(bin_data) -> Union[np.uint8, np.float32]:
    """画像を読み込む
    
    Arguments:
        bin_data {bytes} -- 画像のバイナリデータ
    
    Returns:
        numpy.array -- 画像
    """
    print("\n----- Read Image Start -----\n")
    
    # バイナリ型で読み込み
    file_bytes = np.asarray(bytearray(bin_data.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    # 初期化
    size = img.shape[:2]
    detect = MTCNN_detect()
    num = 512
    
    # num より大きいサイズならば大きいほうのインデックスを取り出す
    # num より小さいサイズならば小さいほうのインデックスを取り出す
    if size[0] > num or size[1] > num:
        idx = np.abs(np.array(size) - num).argmax()
    else :
        idx = np.abs(np.array(size) - num).argmin()
    
    # 拡縮割合の算出
    ratio = size[idx] / num
    print("ratio -> ", ratio, ", type -> ", type(ratio))
    print("size -> ", size, ", type -> ", type(size))
    
    # 拡縮割合が１より大きいなら縮小、１以下なら拡大
    if ratio > 1:
        resize = tuple(round(s/ratio) for s in reversed(size))
        print("down_resize -> ", resize, ", type -> ", type(resize))
        img = cv2.resize(img, resize, interpolation=cv2.INTER_CUBIC)
    else :
        resize = tuple(round(s+(num*(1-ratio))) for s in reversed(size))
        print("up_resize -> ", resize, ", type -> ", type(resize))
        img = cv2.resize(img, resize, interpolation=cv2.INTER_CUBIC)
    
    # 顔の検出、切り出し、ベクトル算出
    img, face, vector = detect.Crop(img)
    
    print("\n----- Read Image End -----\n")
    return img, vector



# --------------------------------------------------------
# ユーザに対しての顔画像登録（POST時）
# --------------------------------------------------------
paths = {}
async def register_data_post(request: Request, files: List[UploadFile] = File(...)):
    print("===== Register Data Start =====\n")
    
    
    global paths
    
    user = db.session.query(User).all()
    
    # POSTデータ
    data = await request.form()
    num_name = data.get('num_name')
    if num_name is None:
        num_name = '0000:admin'
    number = num_name.split(':')[0]
    username = num_name.split(':')[1]
    user_num = db.session.query(User).filter(User.number == number).first()
    
    print("Number : Name -> ", num_name, ", type -> ", type(num_name))
    
    dir = f'./files/{number}_{username}'
    
    # dir という名前のディレクトリがなければ作成
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    # 初期化
    if paths:
        paths = {}
    
    # dir にファイルがあれば最後のファイルの番号を取り出す
    # ファイルの数の再確認および訂正
    if not os.listdir(dir):
        last_file = 0
        user_num.regist_num = 0
    else :
        last_file = int(os.listdir(dir)[-1].split('.')[0])
        user_num.regist_num = sum(os.path.isfile(os.path.join(dir, name)) for name in os.listdir(dir))
    
    # 重複データ確認のためにハッシュ値を取り出す
    data_hash = db.session.query(User_Data.hash).filter(User_Data.user_id == user_num.id).all()

    # 初期化
    error = []
    count = 0
    no_face = 0
    
    flag = False
    for i, file in enumerate(files, start=last_file+1):
        bin_data = io.BytesIO(file.file.read())
        img, vector = read_image(bin_data)
        
        # ベクトルが無ければカウント
        if vector is None:
            no_face += 1
            continue
        
        # すでに登録されたデータがないか確認、あればカウント
        regist_hash = hashlib.sha256(img).hexdigest().encode()
        if data_hash:
            for d_hash in data_hash:
                if regist_hash == d_hash[0]: # 重複しているか
                    count += 1
                    flag = True
                    break
            if flag:
                flag = False
                continue
        
        # 画像を保存
        path = f'{dir}/{i-count-no_face}.jpg'
        cv2.imwrite(path, img)
        print("Path -> ", path, ", type -> ", type(path))
        
        # 出力用
        paths[number+'_'+username+'_'+str(i-count-no_face)] = path
        
        # 登録画像枚数を増やす
        user_num.regist_num += 1
        
        # データベースに書き込み
        data = User_Data(user_num.id, path, regist_hash, vector.tobytes())
        db.session.add(data)
    
    # エラー確認
    if count > 0:
        error.append(f"{count}個のファイルはすでに存在しています。")
    if no_face > 0:
        error.append(f"{no_face}個のファイルで顔が認識できませんでした。別の画像を選択してください。")
    
    db.session.commit()
    db.session.close()
    
    print("\n===== Register Data End =====")
    
    return templates.TemplateResponse('register_data.html', 
                                    {'request': request,
                                    'user': user,
                                    'number': user_num.number,
                                    'username': user_num.username,
                                    'paths': paths,
                                    'error': error})



# --------------------------------------------------------
# HTML に画像出力
# --------------------------------------------------------
def image_output(key):
    print("===== Image Output Start =====\n")
    
    global paths
    
    print("Key -> ", key, ", type -> ", type(key))
    print("Paths[key] -> ", paths[key], ", type -> ", type(paths[key]))
    
    print("\n===== Image Output End =====")
    return FileResponse(paths[key])



# --------------------------------------------------------
# ユーザ登録データ一覧
# --------------------------------------------------------
async def list_userdata(request: Request, number, username):
    print("===== UserData List Start =====\n")
    
    user = db.session.query(User).filter(User.number == number).first()
    userdata = db.session.query(User_Data).filter(User_Data.user_id == user.id).all() 
    
    data = await request.form()
    category = data.get('category')
    search = data.get('search')
    submit = data.get('submit')
    
    # ファイルが存在するか確認、無ければデータベースから削除
    i = len(userdata)-1
    for data in reversed(userdata):
        if not os.path.exists(data.path):
            db.session.delete(data)
            db.session.commit()
            del userdata[i]
        i -= 1
    
    # DB からキーワードにヒットするものを検索
    error = []
    print("Submit -> ", submit, ", type -> ", type(submit))
    print("Search -> ", search, ", type -> ", type(search))
    print("Category -> ", category, ", type -> ", type(category))
    if submit == "検索":
        data_list = []
        data_list = list_search(search, category, userdata)
        
        if data_list:
            userdata = data_list
        elif search == "":
            error.append("キーワードを入力してください。")
        else:
            error.append("一致する検索結果がありませんでした。")
    
    db.session.close()
    
    all_path = 'list_userdata:' + number + ":" + username
    print("pas: ", all_path)
    
    print("\n===== UserData List End =====")
    return templates.TemplateResponse('list_userdata.html',
                                      {'request': request,
                                       'error': error,
                                       'number': number,
                                       'username': username,
                                       'mail': user.mail,
                                       'userdata': userdata,
                                       'all_path': all_path})



# --------------------------------------------------------
# ユーザ登録データ削除
# --------------------------------------------------------
def delete_userdata(data_id):
    print("===== UserData Delete Start =====\n")
    
    # 該当ユーザ情報を取得
    userdata = db.session.query(User_Data).filter(User_Data.id == data_id).first()
    user = db.session.query(User).filter(User.id == userdata.user_id).first()
    
    
    # ファイル削除
    os.remove(userdata.path)
    
    # 削除してコミット
    db.session.delete(userdata)
    db.session.commit()
    db.session.close()
    
    print("\n===== UserData Delete End =====")
    return RedirectResponse(f'/list_userdata/{user.number}:{user.username}')



# --------------------------------------------------------
# HTML に画像出力
# --------------------------------------------------------
def data_output(data_id):
    print("===== DataImage Output Start =====\n")
    
    data = db.session.query(User_Data).filter(User_Data.id == data_id).first()
    db.session.close()
    print("data.path -> ", data.path, ", type -> ", type(data.path))
    
    print("\n===== DataImage Output End =====")
    return FileResponse(data.path)



# --------------------------------------------------------
# 一覧画面での検索メソッド
# --------------------------------------------------------
def list_search(search, category, db_data) -> str:
    print("\n----- List Search Start -----\n")
    
    # DB からキーワードを検索し、あれば追加
    def add_data(keyword: str) -> None:
        if re.match(rf'.*{search}.*', str(keyword)) and type(keyword) is not bytes:
            if not data in data_list:
                print("keyword -> ", keyword, ", type -> ", type(keyword))
                data_list.append(data)
    
    # DB の情報からカテゴリーと同じものを検索
    data_list = []
    if search != "":
        for data in db_data:
            data_dict = vars(data)
            if category in data_dict.keys():
                add_data(data_dict[category])
            else:
                for i, value in enumerate(data_dict.values()):
                    if i != 0:
                        add_data(value)
    
    print("\n----- List Search End -----\n")
    return data_list



# --------------------------------------------------------
# 編集メソッド
# --------------------------------------------------------
async def edit(request: Request, all_path: Optional[str] = None):
    print("===== Edit Start =====\n")
    
    path: Optional[str] = None
    path_number: Optional[str] = None
    path_username: Optional[str] = None
    info: Dict[int, Tuple(str, str)] = {}
    flag: Optional[str] = None
    
    error: List[str] = []
    
    if len(all_path.split(':')) > 2:
        path, path_number, path_username = all_path.split(':')
        user = db.session.query(User).filter(User.number == path_number, User.username == path_username).first()
        
        print("user: ", vars(user))
        for key, value in vars(user).items():
            if key == 'number':
                info[0] = ['社員番号', value]
            elif key == 'username':
                info[1] = ['名前', value]
            elif key == 'mail':
                info[2] = ['Mail', value]
        info = sorted(info.items())
    else :
        path, path_camera_id = all_path.split(':')
        camera = db.session.query(Camera).filter(Camera.id == path_camera_id).first()
        
        for key, value in vars(camera).items():
            if key == 'cameraname':
                info[0] = ['カメラ', value]
            elif key == 'location':
                info[1] = ['設置場所', value]
            elif key == 'url':
                info[2] = ['URL or 接続番号', value]
        info = sorted(info.items())
        
    # GETデータ
    if request.method == 'GET':
        print("===== Edit GET Start =====\n")
            
        db.session.close()
        
        print("\n===== Edit GET End =====")
        return templates.TemplateResponse('edit.html',
                                        {'request': request,
                                        'path': path,
                                        'number': path_number,
                                        'username': path_username,
                                        'all_path': all_path,
                                        'all_data': info,})
    
    if request.method == 'POST':
        print("===== Edit POST Start =====\n")
        
        data = await request.form()
        
        if len(all_path.split(':')) > 2:
            flag = 'User'
            
            number = data.get('社員番号')
            username = data.get('名前')
            mail = data.get('Mail')
            
            tmp_number = db.session.query(User).filter(User.number == number).first()
            tmp_mail = db.session.query(User).filter(User.mail == mail).first()
            
            # 怒涛のエラー処理
            if tmp_number is not None and number != user.number:
                error.append('同じ社員番号のユーザが存在します。')
            if tmp_mail is not None and mail != user.mail:
                error.append('同じメールアドレスが存在します。')
            if pattern_number.match(number) is None:
                error.append('正しく社員番号を入力してください。')
            if pattern_user.match(username) is None:
                error.append('ユーザ名は４～２０文字の半角英数字にしてください。')
            if pattern_mail.match(mail) is None:
                error.append('正しくメールアドレスを入力してください。')
            if number == user.number and username == user.username and mail == user.mail:
                error.append('変更された項目がありません。')
        else :
            flag = 'Camera'
            
            cameraname = data.get('カメラ')
            location = data.get('設置場所')
            camera_type = data.get('camera-type')
            if camera_type == "Web":
                url = data.get('camera-id')
            elif camera_type == "IP":
                url = data.get('url')
            
            tmp_cameraname = db.session.query(Camera).filter(Camera.cameraname == cameraname).first()
            tmp_url = db.session.query(Camera).filter(Camera.url == url).first()
            
            if tmp_cameraname is not None and cameraname != camera.cameraname:
                error.append('同じカメラ名称が存在します。')
            if tmp_url is not None and url != camera.url:
                error.append("同じURLもしくは同じ接続番号が存在します。")
            if pattern_camera.match(cameraname) is None:
                error.append("カメラの名称を入力してください。")
            if url == "":
                error.append("URLもしくは接続番号が入力されていません。")
            elif camera_type == "IP":
                if pattern_url.match(url) is None:
                    error.append("正しくURLを入力してください。")
            if cameraname == camera.cameraname and location == camera.location and url == camera.url:
                error.append('変更された項目がありません。')
        
        
        if error:
            db.session.close()
            print("\n===== Edit POST verError End =====")
            return templates.TemplateResponse('edit.html', 
                                              {'request': request,
                                               'path': path,
                                               'number': path_number,
                                               'username': path_username,
                                               'error': error,
                                               'all_path': all_path,
                                               'all_data': info,})
        
        
        if flag == 'User':            
            user.number = number
            user.username = username
            user.mail = mail
            
            olddir = f'./files/{path_number}_{path_username}'
            newdir = f'./files/{number}_{username}'
            
            # olddir という名前のディレクトリがあれば名前変更
            if os.path.exists(olddir):
                os.rename(olddir, newdir)
            
            old_data = db.session.query(User_Data).filter(User_Data.user_id == user.id).all()
            for new_data in old_data:
                filepath = new_data.path.split('/')[-1]
                new_data.path = newdir + '/' + filepath
                # new_data.change_time = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
                
            path = path + "/" + number + ":" + username
        
        if flag == 'Camera':
            camera.cameraname = cameraname
            camera.url = url
            camera.location = location
        
        db.session.commit()
        db.session.close()
        
        print("\n===== Edit POST verSuccess End =====")
        return RedirectResponse(f'/{path}')



