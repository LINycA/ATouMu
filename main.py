import json
from flask import Flask,send_file,request
from const import *
from middlewars import check_sys_init,SysInit,check_sys_init_wrap,RequestParamsCheck

dispatcher = RequestParamsCheck()


app = Flask(__name__)

@app.get("/index")
@check_sys_init_wrap
def index():
    res = {"ret":200,"msg":"你好"}
    return res

@app.post("/api/sys_init")
def sys_init_api():
    """
    初始化数据库，管理员用户
    :return: 初始化结果
    """
    data = json.loads(request.data)
    check_sys_init_bool = check_sys_init()
    if check_sys_init_bool:
        res = dispatcher.sys_init_params(data)
        return res
    else:
        return SYSINIT_INITED

@app.post("/api/user")
@check_sys_init_wrap
def User():
    data = json.loads(request.data)
    res = dispatcher.user_params(data)
    return res


@app.get("/api/music")
@check_sys_init_wrap
def get_musics():
    mid = request.args.get("mid")
    return send_file(mid+".mp3",mimetype="audio/mpeg")


if __name__ == '__main__':
    app.run(port=8981)