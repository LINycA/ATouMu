from datetime import datetime
from traceback import format_exc
import re

from loguru import logger
from flask import Response
from shortuuid import uuid

from const import *
from utils import Sqlite_con, MysqlCon, YamlConfig


class User:
    def __init__(self):
        using_db = YamlConfig().check_sys_usingdb()
        if using_db == "sqlite":
            self.sql_con = Sqlite_con()
        elif using_db == "mysql":
            self.sql_con = MysqlCon()

    # 获取用户详细信息
    def user_detail(self, userid: str):
        sql = f"select nick_name,password,email,phone,gender,admin,create_time,user_name,last_login from users where user_id=\"{userid}\";"
        try:
            res = self.sql_con.sql2commit(sql=sql)
            user_dict = {
                "nickname": res[0][0],
                "email": res[0][2],
                "phone": res[0][3],
                "gender": res[0][4],
                "admin": res[0][5],
                "create_time": res[0][6],
                "username": res[0][7],
                "last_login": res[0][8],
                "userid": userid
            }
            return user_dict
        except:
            logger.error(format_exc() + "    get user failed.")
            return USERQUERY_ERROR

    # 获取用户简略信息
    def user_query(self):
        sql = f"select user_id,nick_name,user_name,admin,create_time,last_login from users;"
        try:
            res = self.sql_con.sql2commit(sql)
            user_dict = {
                "userid": res[0][0],
                "nickname": res[0][1],
                "username": res[0][2],
                "admin": res[0][3],
                "create_time": res[0][4],
                "last_login": res[0][5]
            }
            return user_dict
        except Exception as e:
            logger.error(e)
            return USERQUERY_ERROR
    # user_add 增加与修改用户
    def user_add(self, username: str, nickname: str, password: str, email: str, phone: str = None, gender: str = "其他",
                 admin: bool = False) -> Response:
        if username is None or nickname is None or password is None or email is None:
            return USERINFO_ERROR
        # 用户名昵称检测
        if len(username) < 4 or len(username) > 16 or len(nickname) < 4 or len(nickname) > 16:
            return USERINFO_ERROR
        elif re.findall(r"\W", username) != [] or len(nickname) != []:
            return USERINFO_ERROR
        # 邮箱检测
        if "@" not in email:
            return USERINFO_ERROR
        # 手机号码，如果不为空则需要检测
        if phone is not None or phone != "":
            if len(phone) != 11:
                return USERINFO_ERROR
        # 性别信息检测，若非限制值则报错
        gender_value_list = ["男", "女", "其他"]
        if gender not in gender_value_list:
            return USERINFO_ERROR
        # 生成用户id
        userid = uuid()
        # 生成用户创建时间
        curdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 构造用户添加sql语句，sqlite与mysql通用
        user_add_sql = f"""
        insert into users(user_id,nick_name,user_name,email,password,gender,phone,create_time,admin)
        values("{userid}","{nickname}","{username}","{email}","{password}","{gender}","{phone}","{curdate}","{admin}");
        """
        try:
            self.sql_con.sql2commit(sql=user_add_sql)
            return USERADD_SUCCESS
        except:
            logger.error(format_exc() + "  user add failed.")
            return USERADD_FAILED

    # 用户删除
    def user_del(self, userid: str) -> Response:
        user_del_sql = f"""
        delete from users where user_id="{userid}";
        """
        try:
            self.sql_con.sql2commit(sql=user_del_sql)
            return USERDEL_SUCCESS
        except:
            logger.error(format_exc() + "   user delete failed.")
            return USERDEL_FAILED

    # 用户信息修改
    def user_modify(self, userid: str, nickname: str, email: str, phone: str, gender: str, admin: bool) -> Response:
        user_modify_sql = f"""
        update from users set nick_name="{nickname}",email="{email}",phone="{phone}",gender="{gender}",admin="{admin}" where user_id="{userid}";
        """
        try:
            self.sql_con.sql2commit(user_modify_sql)
            return USERMODIFY_SUCCESS
        except:
            logger.error(format_exc() + "  user modify failed.")
            return USERMODIFY_FAILED
