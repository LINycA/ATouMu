import json
from flask import Flask,send_file,request,make_response
from const import *
from middlewars import check_sys_init,check_sys_init_wrap,RequestParamsCheck

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

@app.post("/api/login")
@check_sys_init_wrap
def Login():
    data = json.loads(request.data)
    res = dispatcher.login_params(data=data)
    return res

@app.post("/api/user")
@check_sys_init_wrap
def User():
    token = request.headers["Authorization"]
    data = json.loads(request.data)
    res = dispatcher.user_params(data,token)
    return res


@app.get("/api/music")
@check_sys_init_wrap
def get_musics():
    response = make_response("Authorization")
    response.headers["Authentization"] = "asdf"
    return response


if __name__ == '__main__':
    app.run(port=8981)