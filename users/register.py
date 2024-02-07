import re
from traceback import format_exc
from datetime import datetime

from flask import Response
from loguru import logger
from shortuuid import uuid

from const import *
from utils import Sqlite_con, MysqlCon, Password, YamlConfig
from users import User


class Register:
    def __init__(self):
        using_db = YamlConfig().check_sys_usingdb()
        if using_db == "sqlite":
            self.sql_con = Sqlite_con()
        elif using_db == "mysql":
            self.sql_con = MysqlCon()
        self.user = User()
        self.passwd = Password()

    def check_user_info(self, username: str, nickname: str, phone: str, email: str, gender: str):
        # 用户名昵称检测
        if username != "":
            if len(username) < 4 or len(username) > 16:
                return USERINFO_ERROR
            elif re.findall(r"\W", username) != [] or re.findall(r"\W", username) != []:
                return USERINFO_ERROR
        # 昵称检测
        if len(nickname) < 4 or len(nickname) > 16:
            return USERINFO_ERROR
        elif re.findall(r"\W", username) != [] or re.findall(r"\W", username) != []:
            return USERINFO_ERROR
        # 邮箱检测
        if "@" not in email:
            return USERINFO_ERROR
        # 手机号码，如果不为空则需要检测
        if phone is not None and phone != "":
            if len(phone) != 11:
                return USERINFO_ERROR
        # 性别信息检测，若非限制值则报错
        gender_value_list = ["男", "女", "其他"]
        if gender not in gender_value_list:
            return USERINFO_ERROR
        return None

    def register(self, username: str, nick_name: str, email: str, password: str, gender: str, phone: str) -> Response:
        if res := self.check_user_info(username=username, nickname=nick_name, email=email,
                                       gender=gender, phone=phone):
            return res
        if self.user.check_user_exists():
            return USER_EXISTS
        try:
            userid = uuid()
            password_hash = self.passwd.pass_hash(password)
            curdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = f"""insert into users(user_id,user_name,nick_name,password,email,phone,gender,create_time) 
            values("{userid}","{username}","{nick_name}","{password_hash}","{email}","{phone}","{gender}","{curdate}");"""
            self.sql_con.sql2commit(sql)
            return USER_REGISTER_SUCCESS
        except:
            logger.error(format_exc())
            return USER_REGISTER_FAILED
