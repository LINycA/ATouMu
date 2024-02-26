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

    # 用户数据检测
    def user_info_check(self,nickname:str,email:str,phone:str,gender:str,username:str=""):
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

    # 检测用户是否存在
    def check_user_exists(self,userid:str="",username:str="",email:str="") -> bool:
        sql = f"select 1 from users where user_id=\"{userid}\" or user_name=\"{username}\" or email=\"{email}\";"
        sql_res = self.sql_con.sql2commit(sql=sql)
        if sql_res:
            return True
        return False

    # 获取用户详细信息
    def user_detail(self, userid: str) -> Response:
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
            return trans_res({"ret":200,"msg":"成功","data":user_dict})
        except:
            logger.error(format_exc() + "    get user failed.")
            return USERQUERY_ERROR

    # 获取用户简略信息
    def user_query(self) -> Response:
        sql = f"select user_id,nick_name,user_name,admin,create_time,last_login from users;"
        try:
            res = self.sql_con.sql2commit(sql)
            user_result = []
            for user in res:
                user_dict = {
                    "userid": user[0],
                    "nickname": user[1],
                    "username": user[2],
                    "admin": user[3],
                    "create_time": user[4],
                    "last_login": user[5]
                }
                user_result.append(user_dict)
            return trans_res({"ret":200,"msg":"成功","data":user_result})
        except Exception as e:
            logger.error(e)
            return USERQUERY_ERROR

    # 获取用户昵称
    def user_nickname(self,email:str) -> str:
        sql = f'select nick_name from users where email="{email}";'
        try:
            res = self.sql_con.sql2commit(sql=sql)
            return res[0][0]
        except:
            logger.error(format_exc())
            return None 

    # user_add 增加用户
    def user_add(self, username: str, nickname: str, password: str, email: str, phone: str = None, gender: str = "其他",
                 admin: bool = False) -> Response:
        if res := self.user_info_check(username=username,nickname=nickname,
                                email=email,phone=phone,gender=gender):
            return res
        # 生成用户id
        userid = uuid()
        # 生成用户创建时间
        curdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 构造用户添加sql语句，sqlite与mysql通用
        user_add_sql = f"""
        insert into users(user_id,nick_name,user_name,email,password,gender,phone,create_time,admin)
        values("{userid}","{nickname}","{username}","{email}","{password}","{gender}","{phone}","{curdate}","{admin}");
        """
        if self.check_user_exists(username=username):
            return USER_EXISTS
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
        if not self.check_user_exists(userid=userid):
            return USER_UNEXISTS
        try:
            self.sql_con.sql2commit(sql=user_del_sql)
            return USERDEL_SUCCESS
        except:
            logger.error(format_exc() + "   user delete failed.")
            return USERDEL_FAILED

    # 用户信息修改
    def user_modify(self, userid: str, nickname: str, email: str, phone: str, gender: str, admin: bool) -> Response:
        if res := self.user_info_check(nickname=nickname,email=email,phone=phone,gender=gender):
            return res
        user_modify_sql = f"""
        update users set nick_name="{nickname}",email="{email}",phone="{phone}",gender="{gender}",admin="{admin}" where user_id="{userid}";
        """
        if not self.check_user_exists(userid=userid):
            return USER_UNEXISTS
        try:
            self.sql_con.sql2commit(user_modify_sql)
            return USERMODIFY_SUCCESS
        except:
            logger.error(format_exc() + "  user modify failed.")
            return USERMODIFY_FAILED
