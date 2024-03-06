import json
from traceback import format_exc
import re

from loguru import logger
from flask import Flask,request

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
@app.route("/sys_init",methods=["POST"])
def sys_init():
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
    
# rest接口
@app.route("/rest/<action>",methods=["GET","POST"])
@check_sys_init_wrap
def Rest(action):
    token = request.headers.get("Authorization") if request.headers.get("Authorization") else request.headers.get("X-Nd-Authorization")
    data = {
            "id":request.args.get("id"),
            "username":request.args.get("u"),
            "sub_token":request.args.get("t"),
            "sub_salt":request.args.get("s"),
            "token": token.replace("Bearer ","") if token else ""
        }
    try:
        # 文件扫描状态
        if action == "getScanStatus":
            res = dispatcher.scan_status_params(data=data)
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
            res = dispatcher.gettopsons_params(data=data)
            return res
        # 记录歌曲播放
        elif action == "scrobble":
            data.update({
                "time":request.args.get("time"),
                "id":request.args.get("id")
            })
            res = dispatcher.scrobble_params(data=data)
            return res
        # 根据歌曲获取相似歌曲（当前支持返回歌手相同歌手的歌曲，暂未加入风格）
        elif action == "getSimilarSongs":
            data.update({
                "id":request.args.get("id"),
                "count":request.args.get("count")
            })
            res = dispatcher.getsimilarsongs_params(data=data)
            return res
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

@app.route("/api/song/<action>")
@check_sys_init_wrap
def api_song(action):
    print("song_action",action)
    token = request.headers.get("Authorization") if request.headers.get("Authorization") else request.headers.get("X-Nd-Authorization")
    data = {"token":token.replace("Bearer ","") if token else "","id":action}
    try:
        res = dispatcher.song_single_params(data=data)
        return res
    except:
        logger.error(format_exc())
        return PARAMS_ERROR

# api接口
@app.route("/api/<action>",methods=["GET","POST"])
@check_sys_init_wrap
def Api(action):
    token = request.headers.get("Authorization") if request.headers.get("Authorization") else request.headers.get("X-Nd-Authorization")
    data = {"token":token.replace("Bearer ","") if token else ""}
    try:
        # 验证码接口
        if action == "verifycode":
            try:
                data = json.loads(request.data)
                res = dispatcher.verifycode_params(data=data)
                return res
            except:
                logger.error(format_exc())
                return PARAMS_ERROR
        # 艺术家接口
        elif action == "artist":
            data.update({
                "limit":int(request.args.get("_end")),
                "offset":int(request.args.get("_start")),
                "sort":request.args.get("_sort"),
                "order":request.args.get("_order"),
            })
            res = dispatcher.artist_params(data=data)
            return res
        # 专辑接口
        elif action == "album":
            data.update({
                        "limit":int(request.args.get("_end")),
                        "offset":int(request.args.get("_start")),
                        "sort":request.args.get("_sort"),
                        "order":request.args.get("_order"),
                    })
            res = dispatcher.album_params(data=data)
            return res
        # 歌曲信息接口
        elif action == "song":
            data.update({
                "limit":int(request.args.get("_end")),
                "offset":int(request.args.get("_start")),
                "sort":request.args.get("_sort"),
                "order":request.args.get("_order"),
            })
            res = dispatcher.songs_params(data=data)
            return res
        # 音乐信息刮削接口
        elif action == "info_completion":
            res = dispatcher.completion_params(data=data)
            return res
        # 用户注册接口
        elif action == "register":
            try:
                data = json.loads(request.data)
                res = dispatcher.register_params(data)
                return res
            except:
                logger.error(format_exc())
                return PARAMS_ERROR
        # 文件扫描接口
        elif action == "scan":
            res = dispatcher.scan_params(data=data)
            return res
        # 系统设置接口
        elif action == "settings":
            try:
                post_data = json.loads(request.data)
                data.update(post_data)
                res = dispatcher.settings_params(data=data)
                return res
            except:
                logger.error(format_exc())
                return PARAMS_ERROR
        # 用户管理接口
        elif action == "user":
            try:
                postdata = json.loads(request.data)
                data.update(postdata)
                res = dispatcher.user_params(data=data)
                return res
            except:
                logger.error(format_exc())
                return PARAMS_ERROR
        logger.warning("action:  "+action+"  未找到功能")
        return PARAMS_ERROR
    except:
        logger.error(format_exc())
        return PARAMS_ERROR


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8981)
