import json
from traceback import format_exc

from loguru import logger
from flask import Flask,send_file,request,make_response

from const import *
from middlewars import check_sys_init,check_sys_init_wrap,RequestParamsCheck,FileScan


dispatcher = RequestParamsCheck()

app = Flask(__name__)

# index页面，后期考虑改其他用途或删除
@app.get("/index")
@check_sys_init_wrap
def index():
    res = {"ret":200,"msg":"你好"}
    return res

# 系统初始化接口
@app.post("/api/sys_init")
def sys_init_api():
    """
    初始化数据库，管理员用户
    :return: 初始化结果
    """
    try:
        data = json.loads(request.data)
    except:
        logger.error(format_exc())
        return PARAMS_ERROR
    check_sys_init_bool = check_sys_init()
    if check_sys_init_bool:
        res = dispatcher.sys_init_params(data)
        return res
    else:
        return SYSINIT_INITED

# 用户登陆接口
@app.post("/api/login")
@check_sys_init_wrap
def Login():
    try:
        data = json.loads(request.data)
        res = dispatcher.login_params(data=data)
        return res
    except:
        logger.error(format_exc())
        return PARAMS_ERROR

# 验证码接口
@app.post("/api/verifycode")
@check_sys_init_wrap
def VerifyCode():
    try:
        data = json.loads(request.data)
        res = dispatcher.verifycode_params(data=data)
        return res
    except:
        logger.error(format_exc())
        return PARAMS_ERROR
    
# 用户注册接口，等待添加系统设置验证
@app.post("/api/register")
@check_sys_init_wrap
def register():
    try:
        data = json.loads(request.data)
        res = dispatcher.register_params(data)
        return res
    except:
        logger.error(format_exc())
        return PARAMS_ERROR

# 用户管理接口，用于用户的增删改查
@app.post("/api/user")
@check_sys_init_wrap
def User():
    """
    用户管理
    """
    try:
        token = request.headers["Authorization"]
    except:
        return TOKEN_ERROR
    try:
        data = json.loads(request.data)
        res = dispatcher.user_params(data,token)
        return res
    except:
        logger.error(format_exc())
        return PARAMS_ERROR

# 系统设置接口
@app.post("/api/settings")
@check_sys_init_wrap
def Settings():
    try:
        token = request.headers["Authorization"]
    except:
        return TOKEN_ERROR
    try:
        date = json.loads(request.data)
        res = dispatcher.settings_params(data=date,token=token)
        return res
    except:
        logger.error(format_exc())
        return PARAMS_ERROR
# 文件扫描
fs = FileScan()
fs.regular_time_scan()
@app.get("/api/scan")
@check_sys_init_wrap
def Scan():
    try:
        token = request.headers["Authorization"]
    except:
        return TOKEN_ERROR
    res = dispatcher.scan_params(token=token)
    return res
# 媒体接口，未完成
@app.get("/api/music")
@check_sys_init_wrap
def get_musics():
    response = make_response("Authorization")
    response.headers["Authentization"] = "asdf"
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8981)
