"""
run.py
サーバ立ち上げ用ファイル
"""

from urls import app
import uvicorn

if __name__ == '__main__':
    # uvicorn.runさせることでpythonファイルを実行させるだけでよくなる
    uvicorn.run(app=app, port=8088, host='0.0.0.0', log_level='info')
    # uvicorn.run("run:app", port=8088, host='127.0.0.1', reload=True)
    # uvicorn.run("run:app", port=8088, host='127.0.0.1', log_level='info', reload=True)
