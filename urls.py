"""
urls.py
ルーティング用ファイル
"""

from controllers import *


# FastAPIのルーティング用関数
# app.add_api_route('/', index, methods=['GET', 'POST'])
app.add_api_route('/', admin, methods=['GET', 'POST'])
# app.add_api_route('/admin', admin, methods=['GET', 'POST'])

# app.add_api_route('/login', login, methods=['GET'])
# app.add_api_route('/login', login_auth, methods=['POST'])
# app.add_api_route('/logout', logout, methods=['GET'])

# カメラ関係
app.add_api_route('/stream', stream, methods=['GET', 'POST'])
app.add_api_route('/register_camera', register_camera, methods=['GET', 'POST'])
app.add_api_route('/list_camera', list_camera, methods=['GET', 'POST'])
app.add_api_route('/delete_camera/{c_id}', delete_camera)
app.add_api_route('/video_feed/{cameraname}', video_feed)
app.add_api_route('/stop', stop)

# ユーザ関係
app.add_api_route('/register_user', register_user, methods=['GET', 'POST'])
app.add_api_route('/list_user', list_user, methods=['GET', 'POST'])
app.add_api_route('/delete_user/{u_id}', delete_user)
app.add_api_route('/register_data', register_data, methods=['GET'])
app.add_api_route('/register_data_post', register_data_post, methods=['POST'])
app.add_api_route('/image_output/{key}', image_output)
app.add_api_route('/list_userdata/{number}:{username}', list_userdata, methods=['GET', 'POST'])
app.add_api_route('/delete_userdata/{data_id}', delete_userdata)
app.add_api_route('/data_output/{data_id}', data_output)

app.add_api_route('/edit/{all_path}', edit, methods=['GET', 'POST'])
