from os import path, getcwd, mkdir
import re

from flask import Response
from pymysql import Connect
from loguru import logger

from const import *
from users import User,Login,TokenCheck,Register
from middlewars import SysInit,Email,FileScan
from utils import YamlConfig
from settings import Settings


class RequestParamsCheck:
    def __init__(self):
        self.tk_check = TokenCheck()
        self.email = Email()
    # 数据库初始化操作
    def sys_init_params(self, data: dict) -> Response:
        """
        检测系统初始化参数是否正确
        :param data:字典，json
        :return:返回bool,配置字典,用户信息字典
        """
        if "using_db" not in data or "user" not in data:
            return PARAMS_ERROR
        else:
            try:
                sysinit = SysInit()
                user_dict = data.get("user")
                using_db_list = ["sqlite", "mysql"]
                # 判断指定使用的的数据库是否允许
                if data.get("using_db") not in using_db_list:
                    return PARAMS_ERROR
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
            if data.get("using_db") == "sqlite":
                if not path.exists(path.join(getcwd(), "db")):
                    mkdir(path.join(getcwd(), "db"))
            elif data.get("using_db") == "mysql":
                try:
                    db_fields = ["host", "port", "user", "password", "database"]
                    for i in data.get("db").get("mysql"):
                        if i not in db_fields:
                            return PARAMS_ERROR
                        elif data.get("db").get("mysql").get(i) is None or data.get("db").get("mysql").get(i) == "":
                            return PARAMS_ERROR
                except Exception as e:
                    logger.error(e)
                    return PARAMS_ERROR
                try:
                    con = Connect(host=data.get("db").get("mysql").get("host"),
                                  port=int(data.get("db").get("mysql").get("port")),
                                  user=data.get("db").get("mysql").get("user"),
                                  password=data.get("db").get("mysql").get("password"),
                                  database="mysql")
                    with con.cursor() as cur:
                        cur.execute("show tables")
                    con.close()
                except Exception as e:
                    logger.error(ConnectionError("sys_init mysql Connect Error."))
                    return MYSQL_ERROR
            # 初始化数据库表
            init_bool = sysinit.sys_init(data, user_dict)
            if init_bool:
                return SYSINIT_SUCCESS
            else:
                return SYSINIT_FAILED

    # 登陆操作
    def login_params(self,data:dict) -> Response:
        login_c = Login()
        keys = ["user_name","password"]
        for i in keys:
            if i not in data:
                return PARAMS_ERROR
        username = data.get("user_name")
        password = data.get("password")
        res = login_c.login(username=username,password=password)
        return res

    # 用户操作分发
    def user_params(self, data: dict,token:str) -> Response:
        expire,admin = self.tk_check.check_token(token=token)
        if expire:
            if type(expire) is bool:
                return TOKEN_EXPIRE
            return expire
        if "action" not in data or "user" not in data:
            return PARAMS_ERROR
        action = data.get("action")
        action_keys = ["add", "delete", "query", "modify", "detail","check"]
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
            res = user.user_query()
            return res
        # 用户详细信息
        elif action == "detail":
            if admin:
                user_info_dict = data.get("user")
                if "user_id" not in user_info_dict:
                    return PARAMS_ERROR
                res = user.user_detail(user_info_dict.get("user_id"))
                return res
            return PERMISSION_ERROR

    # 验证码请求
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

    # 系统设置
    def settings_params(self,data: dict,token: str) -> Response:
        expire,admin = self.tk_check.check_token(token=token)
        if expire:
            if type(expire) is bool:
                return TOKEN_EXPIRE
            return expire
        if not admin:
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
    def scan_params(self,token:str) -> Response:
        expire,admin = self.tk_check.check_token(token=token)
        if expire:
            if type(expire) is bool:
                return TOKEN_EXPIRE
            return expire
        if not admin:
            return PERMISSION_ERROR
        return FileScan().start_scan()