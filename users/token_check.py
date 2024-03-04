import jwt
import datetime
from utils import YamlConfig
from const import *

class TokenCheck:
    def __init__(self) -> None:
        self.algorithm = "HS256"
    # 生成token
    def gen_token(self,payload:dict):
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