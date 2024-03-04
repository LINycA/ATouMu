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
        def subsonic_salt() -> str:
            salt_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
            salt = ""
            for n in range(6):
                salt += choice(salt_list)
            return salt
        sql = f"select user_id,nick_name,password,admin from users where user_name=\"{username}\";"
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
            subsonicsalt = subsonic_salt()
            subsonicToken = md5((password+subsonicsalt).encode()).hexdigest()
            response = trans_res({"id":tk_dict.get("user_id"),"name":nickname,"isAdmin":tk_dict.get("admin"),"token":token,"username":username,"lastFMApiKey":"","subsonicSalt":subsonicsalt,"subsonicToken":subsonicToken})
            response.headers["Authentization"] = token
        else:
            response = trans_res({"ret":201,"msg":"用户名或密码错误"})
        return response       