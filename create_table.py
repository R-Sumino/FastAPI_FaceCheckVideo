from random import sample
from models import *
import db
import os


if __name__ == "__main__":
    path = SQLITE3_NAME
    if not os.path.isfile(path):

        # テーブルを作成する
        Base.metadata.create_all(db.engine)

    # サンプルユーザ(admin)を作成
    sample = Camera(cameraname='sample', url='http://sample.com', location='sample_location')
    db.session.add(sample)  # 追加
    db.session.commit()  # データベースにコミット

    admin = User(number='000000', username='admin', mail='hoge@example.com', regist_num='0')
    db.session.add(admin)   # 追加
    db.session.commit()
    
    sample_data = User_Data(user_id=admin.id, path='files/000000_admin', hash=None, vector=None)
    db.session.add(sample_data)
    db.session.commit()
    
    db.session.close()  # セッションを閉じる
