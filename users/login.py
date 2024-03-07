from random import choice
from hashlib import md5

from flask import Response

from const import *
from utils import Sqlite_con,Password,YamlConfig,trans_res
from users import TokenCheck

class Login:
    def __init__(self):
        self.sql_con = Sqlite_con()
        self.passwd = Password()
        self.token_check = TokenCheck()

    def login(self,username:str,password:str) -> Response:
        
        sql = f"select user_id,nick_name,password,admin from users where user_name=\"{username}\" or email=\"{username}\";"
        sql_res = self.sql_con.sql2commit(sql)
        if sql_res == []:
            return LOGIN_ERROR
        tk_dict = {
            "user_id":sql_res[0][0],
            "nick_name":sql_res[0][1],
            "admin":True if sql_res[0][3] else False
        }
        nickname = tk_dict.get("nick_name")
        password_hash = sql_res[0][2]
        if self.passwd.check_pass(password=password,pass_hash=password_hash):
            token = self.token_check.gen_token(payload=tk_dict)
            subsonicToken,subsonicsalt = self.token_check.subsonic_token(username=username)
            response = trans_res({"id":tk_dict.get("user_id"),"name":nickname,"isAdmin":tk_dict.get("admin"),"token":token,"username":username,"lastFMApiKey":"","subsonicSalt":subsonicsalt,"subsonicToken":subsonicToken})
            response.headers["Authentization"] = token
        else:
            response = trans_res({"ret":201,"msg":"用户名或密码错误"})
        return response       