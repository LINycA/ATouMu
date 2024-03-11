from os import path, getcwd
from functools import wraps
import re
from traceback import format_exc

from flask import Response,send_file,make_response
from loguru import logger

from const import *
from users import User,Login,TokenCheck,Register
from app import Songs,Album,Artist,Playlist
from middlewars import SysInit,Email,FileScan,InfoCompletion,Keepalive
from utils import YamlConfig,Sqlite_con
from settings import Settings


class RequestParamsCheck:
    def __init__(self):
        self.email = Email()
        file_scan = FileScan()
        file_scan.start_scan()  # 后端启动就开始扫描文件
        file_scan.regular_time_scan() # 定时扫描文件变化
        InfoCompletion().regular_start_completion() # 定时刮削音乐信息，定时暂不可修改

    # subsonic口令验证装饰器
    def subsonic_token_check_wrap(func):
        @wraps(func)
        def wrap(*args,**kwargs):
            tk_check = TokenCheck()
            data = kwargs.get("data")
            username = data.get("username")
            sub_token = data.get("sub_token")
            sub_salt = data.get("sub_salt")
            if not tk_check.subsonic_checktoken(sub_token=sub_token,salt=sub_salt,username=username):
                return PERMISSION_ERROR
            return func(*args,**kwargs)
        return wrap

    # 浏览器token检测装饰器
    def request_token_check_wrap(func):
        @wraps(func)    
        def wrap(*wargs,**kwargs):
            tk_check = TokenCheck()
            token = kwargs.get("data").get("token")
            if not token:
                return TOKEN_ERROR
            expire,admin,user_id = tk_check.check_token(token=token)
            if expire:
                if type(expire) is bool:
                    return TOKEN_EXPIRE
                return expire
            kwargs["data"]["admin"] = admin
            kwargs["data"]["user_id"] = user_id
            return func(*wargs,**kwargs)
        return wrap

    # 数据库初始化操作
    def sys_init_params(self, data: dict) -> Response:
        """
        检测系统初始化参数是否正确
        :param data:字典，json
        :return:返回bool,配置字典,用户信息字典
        """
        if "user" not in data:
            return PARAMS_ERROR
        else:
            try:
                sysinit = SysInit()
                user_dict = data.get("user")
                # 判断用户信息字段是否匹配
                key_list = ["user_name", "nick_name", "password", "email"]
                for i in key_list:
                    if i not in user_dict:
                        return PARAMS_ERROR
                    elif user_dict[i] is None or user_dict[i] == "":
                        return PARAMS_ERROR
            except Exception as e:
                logger.error(e)
                return PARAMS_ERROR
            # 初始化数据库表
            init_bool = sysinit.sys_init(data, user_dict)
            if init_bool:
                return SYSINIT_SUCCESS
            else:
                return SYSINIT_FAILED

    # 登陆操作
    def login_params(self,data:dict) -> Response:
        login_c = Login()
        keys = ["username","password"]
        for i in keys:
            if i not in data:
                return PARAMS_ERROR
        username = data.get("username")
        password = data.get("password")
        res = login_c.login(username=username,password=password)
        return res

        # 验证码请求
    
    # 验证码操作
    def verifycode_params(self,data: dict) -> Response:
        yaml_conf = YamlConfig()
        settings_conf = yaml_conf.settings_conf()
        if not settings_conf.get("registe_allow"):
            return REGIST_UNALLOW
        action = data.get("action")
        email = data.get("email")
        self.user = User()
        if not re.match(r"^[0-9a-zA-Z._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+$",email):
            return PARAMS_ERROR        
        # 用户注册获取验证码
        if action == "regist_get_code":
            if self.user.check_user_exists(email=email):
                return USER_EXISTS
            nickname = data.get("nick_name")
            if nickname is None or nickname == "":
                return PARAMS_ERROR
            if res := self.email.send_email(send_to=email,nickname=nickname):
                return res
        # 用户找回密码获取验证码
        elif action == "forget_password_get_code":
            if not self.user.check_user_exists(email=email):
                return USER_UNEXISTS
            else:
                nickname = self.user.user_nickname(email=email)
            if res := self.email.send_email(send_to=email,nickname=nickname):
                return res
        return PARAMS_ERROR

    # 注册操作
    def register_params(self,data: dict) -> Response:
        settings_conf = self.yaml_conf.settings_conf()
        keys = ["user_name","nick_name","password","email","phone","gender"]
        if not settings_conf.get("registe_allow"):
            return REGIST_UNALLOW
        if registe_auth := settings_conf.get("registe_auth"):
            keys.append("code")
        for key in keys:
            if key not in data:
                return PARAMS_ERROR
        if registe_auth:
            email = data.get("email")
            code = data.get("code")
            verify_res = self.email.verify_code.match_code(email=email,code_=code)
            if not verify_res:
                return VERIFY_CODE_FAILED
        register = Register()

        res = register.register(username=data.get("user_name"),nick_name=data.get("nick_name"),
                          password=data.get("password"),email=data.get("email"),
                          phone=data.get("phone"),gender=data.get("gender"))
        return res

    # 用户操作分发
    @request_token_check_wrap
    def user_params(self, data: dict) -> Response:
        if "action" not in data:
            return PARAMS_ERROR
        action = data.get("action")
        action_keys = ["add", "delete", "query", "modify", "detail","check"]
        admin = data.get("admin")
        if action not in action_keys:
            return PARAMS_ERROR

        user = User()
           
        # 用户增加操作
        if action == "add":
            if admin:
                user_info_dict = data.get("user")
                user_keys = ["user_name", "nick_name", "email", "password", "gender", "phone", "admin"]
                for key in user_keys:
                    if key not in user_info_dict:
                        return PARAMS_ERROR
                return user.user_add(username=user_info_dict.get("user_name"), nickname=user_info_dict.get("nick_name"),
                                    password=user_info_dict.get("password"), email=user_info_dict.get("email"),
                                    phone=user_info_dict.get("phone"), gender=user_info_dict.get("gender"),
                                    admin=user_info_dict.get("admin"))
            return PERMISSION_ERROR

        # 用户删除操作
        elif action == "delete":
            if admin:
                user_info_dict = data.get("user")
                if "user_id" not in user_info_dict:
                    return USERINFO_ERROR
                return user.user_del(user_info_dict.get("user_id"))
            return PERMISSION_ERROR

        # 用户信息修改操作
        elif action == "modify":
            user_info_dict = data.get("user")
            user_keys = ["user_id", "nick_name", "email", "phone", "gender", "admin"]
            for key in user_info_dict:
                if key not in user_keys:
                    return PARAMS_ERROR
            return user.user_modify(userid=user_info_dict.get("user_id"), nickname=user_info_dict.get("nick_name"),
                                    email=user_info_dict.get("email"), phone=user_info_dict.get("phone"),
                                    gender=user_info_dict.get("gender"), admin=user_info_dict.get("admin"))
        # 用户简单信息
        elif action == "query":
            if admin:
                page_keys = ["page","limit"]
                for key in page_keys:
                    if key not in data:
                        return PARAMS_ERROR
                try:
                    page = int(data.get("page"))
                    limit = int(data.get("limit"))
                    res = user.user_query(page=page,limit=limit)
                    return res
                except:
                    logger.error(format_exc())
                    return PARAMS_ERROR
            return PERMISSION_ERROR
        # 用户详细信息
        elif action == "detail":
            if admin:
                user_info_dict = data.get("user")
                if "user_id" not in user_info_dict:
                    return PARAMS_ERROR
                res = user.user_detail(user_info_dict.get("user_id"))
                return res
            return PERMISSION_ERROR

    # 系统设置
    @request_token_check_wrap
    def settings_params(self,data: dict) -> Response:
        if not data.get("admin"):
            return PERMISSION_ERROR
        if "action" not in data:
            return PARAMS_ERROR
        settings = Settings()
        action_keys = ["get","modify","email_test"]
        action = data.get("action")
        if action not in action_keys:
            return PARAMS_ERROR
        if action == "get":
            return settings.get_settings_info()
        elif action == "modify":
            if "regist" in data:
                regist_keys = ["regist_allow","regist_auth","email_conf"]
                for key in regist_keys:
                    if key not in data.get("regist"):
                        return PARAMS_ERROR
                regist_allow = data.get("regist").get("regist_allow")
                regist_auth = data.get("regist").get("regist_auth")
                email_conf = data.get("regist").get("email_conf")
                return settings.register_allow(registe_allow=regist_allow,registe_auth=regist_auth,email_conf=email_conf)
            if "media" in data:
                if "scan_path" not in data.get("media") or "scan_regular_time" not in data.get("media"):
                    return PARAMS_ERROR
                scan_path = data.get("media").get("scan_path")
                scan_regular_time = data.get("media").get("scan_regular_time")
                return settings.scan_path(scan_path=scan_path,scan_regular_time=scan_regular_time)
        elif action == "email_test":
            return settings.email_conf_test()
    
    # 音乐文件扫描
    @request_token_check_wrap
    def scan_params(self,data:dict) -> Response:
        if not data.get("admin"):
            return PERMISSION_ERROR
        return FileScan().start_scan()

    # 返回扫描状态
    @request_token_check_wrap
    def scan_status_params(self,data:dict) -> Response:
        return FileScan().get_scan_status()

    # 音乐信息刮削
    @request_token_check_wrap
    def completion_params(self,data:dict) -> Response:
        if not data.get("admin"):
            return PERMISSION_ERROR
        return InfoCompletion().start_completion()

    # 获取媒体信息
    @request_token_check_wrap
    def songs_params(self,data:dict) -> Response:
        limit = int(data.get("limit"))
        offset = int(data.get("offset"))
        order = data.get("order")
        sort = data.get("sort")
        title = data.get("title")
        res = Songs().get_all_song(offset,limit,sort,order,title)
        return res
    
    # 获取专辑信息
    @request_token_check_wrap
    def album_params(self,data:dict) -> Response:
        limit = int(data.get("limit"))
        offset = int(data.get("offset"))
        order = data.get("order")
        sort = data.get("sort")
        name = data.get("name")
        res = Album().get_all_Album(offset,limit,sort,order,name)
        return res
    
    # 获取艺术家信息
    @request_token_check_wrap
    def artist_params(self,data:dict) -> Response:
        limit = int(data.get("limit"))
        offset = int(data.get("offset"))
        order = data.get("order")
        sort = data.get("sort")
        user_id = data.get("user_id")
        name = data.get("name")
        res = Artist().get_all_artist(user_id,offset,limit,sort,order,name)
        return res

    # 歌单
    @request_token_check_wrap
    def playlist_params(self,data:dict) -> Response:
        method = data.get("method")
        p = Playlist()
        if method == "POST":
            name = data.get("name")
            user_id = data.get("user_id")
            comment = data.get("comment")
            public = data.get("public")
            res = p.playlist_add(name=name,comment=comment,public=public,user_id=user_id)
            return res
        elif method == "GET":
            limit = data.get("limit")
            offset = data.get("offset")
            order_by = data.get("order_by")
            res = p.playlist_get(order_by=order_by,limit=limit,offset=offset)
            return res
        elif method == "DELETE":
            playlist_id = data.get("playlist_id")
            res = p.playlist_delete(pid=playlist_id)
            return res
        else:
            return PARAMS_ERROR
    
    # 歌单歌曲
    @request_token_check_wrap
    def playlist_song_params(self,data:dict) -> Response:
        p = Playlist()
        method = data.get("method")
        if method == "POST":
            pid = data.get("playlist_id")
            song_ids = data.get("ids")
            return p.playlist_song_add(sids=song_ids,pid=pid)
        elif method == "GET":
            pid = data.get("playlist_id")
            offset = data.get("offset")
            limit = data.get("limit")
            order = data.get("order")
            order_by = data.get("order_by")
            user_id = data.get("user_id")
            return p.playlist_song_get(pid=pid,offset=offset,limit=limit,order=order,order_by=order_by,user_id=user_id)
        elif method == "DELETE":
            sid = data.get("id")
            pid = data.get("playlist_id")
            res = p.playlist_song_delete(pid=pid,sid=sid)
            return res

    # 获取相似歌曲
    @subsonic_token_check_wrap
    def getsimilarsongs_params(self,data:dict) -> Response:
        count = data.get("count")
        media_id = data.get("id")
        user_name = data.get("username")
        res = Songs().get_similar_songs(count=count,media_id=media_id,user_name=user_name)
        return res

    # 获取歌手高播放量的歌曲
    @subsonic_token_check_wrap
    def gettopsons_params(self,data:dict) -> Response:
        artist = data.get("artist")
        count = data.get("count")
        user_name = data.get("username")
        res = Songs().get_songs_by_artist(artist=artist,count=count,user_name=user_name)
        return res

    # 记录音乐播放次数
    @subsonic_token_check_wrap
    def scrobble_params(self,data:dict) -> Response:
        username = data.get("username")
        media_id = data.get("id")
        f_time = data.get("time")
        user_id = data.get("user_id")
        return Songs().scrobble_songs(f_time=f_time,media_id=media_id,username=username)

    # 获取专辑封面
    @subsonic_token_check_wrap
    def cover_art_params(self,data:dict) -> Response:
        sql_con = Sqlite_con()
        def get_album_id(mid:str) -> str:
            get_albumid_sql = f"""select album_id from media_file where id="{mid}";"""
            alb_id = sql_con.sql2commit(get_albumid_sql)
            print(alb_id)
            if alb_id:
                return alb_id[0][0]
            else:
                return "tl"
        id = data.get("id")
        img_path = path.join(getcwd(),"data","album_img",id+".jpeg")
        if not path.exists(img_path):
            album_id = str(get_album_id(id))
            img_path = path.join(getcwd(),"data","album_img",album_id+".jpeg")
        with open(img_path,"rb")as f:
            img_byte = f.read()
        response = make_response(img_byte)
        response.headers["Content-Type"] = "image/jpeg"
        return response

    # 获取单一歌曲文件详细信息
    @request_token_check_wrap
    def song_single_params(self,data:dict) -> Response:
        id = data.get("id")
        res = Songs().get_song_info(id=id)
        return res

    # 媒体流
    @subsonic_token_check_wrap
    def media_stream_params(self,data:dict):
        id = data.get("id")
        songs = Songs()
        res_dict = songs.get_song_path(id=id)
        if res_dict:
            response = send_file(res_dict.get("file_path"))
            response.headers["X-Content-Duration"] = res_dict.get("duration")
            return response
        return PARAMS_ERROR
            
    # 系统心跳
    def keepalive_params(self) -> Response:
        return Keepalive().keepalive()