from flask import Response
from const import *
from utils import Sqlite_con,Password,MysqlCon,YamlConfig,trans_res
from users import TokenCheck

class Login:
    def __init__(self):
        using_db = YamlConfig().check_sys_usingdb()
        if using_db == "sqlite":
            self.sql_con = Sqlite_con()
        elif using_db == "mysql":
            self.sql_con = MysqlCon()
        self.passwd = Password()
        self.token_check = TokenCheck()

    def login(self,username:str,password:str) -> Response:
        sql = f"select user_id,nick_name,password,admin from users where user_name=\"{username}\";"
        sql_res = self.sql_con.sql2commit(sql)
        if sql_res == []:
            return LOGIN_ERROR
        tk_dict = {
            "user_id":sql_res[0][0],
            "nick_name":sql_res[0][1],
            "admin":sql_res[0][3]
        }
        nickname = tk_dict.get("nick_name")
        password_hash = sql_res[0][2]
        if self.passwd.check_pass(password=password,pass_hash=password_hash):
            token = self.token_check.gen_token(payload=tk_dict)
            response = trans_res({"ret":200,"msg":f"你好，{nickname}!"})
            response.headers["Authentization"] = token
        else:
            response = trans_res({"ret":201,"msg":"用户名或密码错误"})
        return response       