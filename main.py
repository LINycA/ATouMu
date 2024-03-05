import json
from traceback import format_exc
import re

from loguru import logger
from flask import Flask,send_file,request,make_response

from const import *
from middlewars import check_sys_init,check_sys_init_wrap,RequestParamsCheck


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

# 系统心跳包
@app.get("/api/keepalive/keepalive")
@check_sys_init_wrap
def Keepalive():
    try:
        return dispatcher.keepalive_params()
    except:
        logger.error(format_exc())
        return PARAMS_ERROR

# 用户登陆接口
@app.post("/auth/login")
@check_sys_init_wrap
def Login():
    try:
        data = json.loads(request.data)
        print(data)
        res = dispatcher.login_params(data=data)
        return res
    except:
        logger.error(format_exc())
        return PARAMS_ERROR

# 验证码接口
@app.route("/api/verifycode",methods=["POST","GET"])
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
@app.get("/api/scan")
@check_sys_init_wrap
def Scan():
    try:
        token = request.headers["Authorization"]
    except:
        return TOKEN_ERROR
    res = dispatcher.scan_params(token=token)
    return res
# rest接口
@app.route("/rest/<action>",methods=["GET","POST"])
def ScanStatus(action):
    data = {
            "id":request.args.get("id"),
            "username":request.args.get("u"),
            "sub_token":request.args.get("t"),
            "sub_salt":request.args.get("s")
        }
    try:
        token = request.headers.get("X-Nd-Authorization")
        # 不同的token方式
        if token:
            token = token.replace("Bearer ","")
        # 文件扫描状态
        if action == "getScanStatus":
            res = dispatcher.scan_status_params(token=token)
            return res
        # 专辑封面
        elif action == "getCoverArt":
            res = dispatcher.cover_art_params(data=data)
            return res
        # 获取歌手播放量高的歌曲
        elif action == "getTopSongs":
            data.update({
                "artist":request.args.get("artist"),
                "count":request.args.get("count")
            })
            res = dispatcher.gettopsons_params(token=token,data=data)
        # /rest/scrobble?id=28fa6c30f9a6905aa7a2e2fdfdb11a53&submission=true&time=1709630991856&u=arno&t=406da93d43afdf070b4a877e1a0dc698&s=3o0h8l&f=json&v=1.8.0&c=Stream+Music 
        # 记录音乐播放次数
        elif action == "scrobble":
            data.update({
                "time":request.args.get("time"),
                "id":request.args.get("id")
            })
            res = dispatcher.scrobble_params(data=data)
        # 媒体流
        elif action == "stream":
            res = dispatcher.media_stream_params(data=data)
            res.headers["x-frame-options"] = "DENY"
            res.headers["permissions-policy"] = "autoplay=(), camera=(), microphone=(), usb=()"
            res.headers["x-content-type-options"] = "nosniff"
            return res
        logger.warning("action: "+action+"  找不到对应功能")
        return PARAMS_ERROR
    except:
        logger.error(format_exc())
        return PARAMS_ERROR

# 音乐信息刮削
@app.get("/api/info_completion")
@check_sys_init_wrap
def InfoCompletion():
    try:
        token = request.headers["Authorization"]
    except:
        return TOKEN_ERROR
    res = dispatcher.completion_params(token=token)
    return res

# 获取音乐信息
@app.get("/api/song")
@check_sys_init_wrap
def Songs():
    try:
        if "X-Nd-Authorization" in request.headers:
            token = request.headers.get("X-Nd-Authorization").replace("Bearer ","")
        else:
            token = request.headers.get("Authorization")
        data = {
            "limit":int(request.args.get("_end")),
            "offset":int(request.args.get("_start")),
            "sort":request.args.get("_sort"),
            "order":request.args.get("_order")
        }
        res = dispatcher.songs_params(token=token,data=data)
        return res
    except:
        logger.error(format_exc())
        return PARAMS_ERROR

# 获取专辑信息
@app.get("/api/album")
@check_sys_init_wrap
def Album():
    try:
        if "X-Nd-Authorization" in request.headers:
            token = request.headers.get("X-Nd-Authorization").replace("Bearer ","")
        else:
            token = request.headers.get("Authorization")
        data = {
            "limit":int(request.args.get("_end")),
            "offset":int(request.args.get("_start")),
            "sort":request.args.get("_sort"),
            "order":request.args.get("_order")
        }
        res = dispatcher.album_params(token=token,data=data)
        return res
    except:
        logger.error(format_exc())
        return PARAMS_ERROR
    
# 获取艺术家信息
@app.get("/api/artist")
@check_sys_init_wrap
def Artist():
    try:
        if "X-Nd-Authorization" in request.headers:
            token = request.headers.get("X-Nd-Authorization").replace("Bearer ","")
        else:
            token = request.headers.get("Authorization")
        data = {
            "limit":int(request.args.get("_end")),
            "offset":int(request.args.get("_start")),
            "sort":request.args.get("_sort"),
            "order":request.args.get("_order")
        }
        res = dispatcher.artist_params(token=token,data=data)
        return res
    except:
        logger.error(format_exc())
        return PARAMS_ERROR


# /rest/getTopSongs?u=arno&t=1a3ef32a51e7ae37d54625adc87aa153&s=5ec2y2&f=json&v=1.8.0&c=Stream+Music&artist=&count=30


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8981)
