import datetime
from random import choice
from hashlib import md5

import jwt

from utils import YamlConfig,Sqlite_con
from const import *

class TokenCheck:
    def __init__(self) -> None:
        self.algorithm = "HS256"
    
    # 获取用户密码
    def get_user_passwd(self,username:str) -> str:
        sql_con = Sqlite_con()
        sql = f"select password from users where user_name=\"{username}\" or email=\"{username}\";"
        res = sql_con.sql2commit(sql=sql)
        password = res[0][0] if res else None
        return password

    # subsonic口令
    def subsonic_token(self,username:str) -> tuple[str,str]:
        def subsonic_salt() -> str:
            salt_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
            salt = ""
            for n in range(6):
                salt += choice(salt_list)
            return salt
        password = self.get_user_passwd(username=username)
        ssalt = subsonic_salt()
        subsonicToken = md5((password+ssalt).encode()).hexdigest()
        return subsonicToken,ssalt

    # 验证subsonic口令
    def subsonic_checktoken(self,sub_token:str,salt:str,username:str) -> bool:
        password = self.get_user_passwd(username=username)
        tk = md5((password+salt).encode()).hexdigest()
        if sub_token == tk:
            return True
        return False

    # 生成token
    def gen_token(self,payload:dict) -> str:
        expire = datetime.timedelta(hours=24)
        curdate = datetime.datetime.now()+expire
        expire_time = curdate.strftime("%Y-%m-%d %H:%M:%S")
        payload.update({"expire":expire_time})
        secret_key = YamlConfig().jwt_secret_key()
        token = jwt.encode(payload=payload,key=secret_key,algorithm=self.algorithm)
        return token
    
    # 检查token
    def check_token(self,token:str) -> tuple[bool,bool]:
        secret_key = YamlConfig().jwt_secret_key()
        try:
            res_dict = jwt.decode(token,secret_key,self.algorithm)
        except:
            return TOKEN_ERROR,False
        admin = res_dict.get("admin")
        expire = res_dict.get("expire")
        expire_time = datetime.datetime.strptime(expire,"%Y-%m-%d %H:%M:%S")
        curdate = datetime.datetime.now()
        if expire_time > curdate:
            return False,admin
        else:
            return True,False

        

if __name__ == "__main__":
    t = TokenCheck()
    # token = t.gen_token({"asdf":"123","admin":True,"expire":"2024-02-06 18:07:11"})
    # print(token)
    print(t.check_token(token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiSzVjZ2FIY2NMdzRjN2RXZzdxRXpBVCIsIm5pY2tfbmFtZSI6ImFybm8iLCJhZG1pbiI6dHJ1ZSwiZXhwaXJlIjoiMjAyNC0wMy0wMiAxNTo0MDo1OSJ9.usE9IKoyPlBdMYkcq2FHe95anw1prwaZ2rPd7L0TXkI"))