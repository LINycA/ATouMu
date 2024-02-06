import jwt
import datetime
from utils import Sqlite_con,MysqlCon,YamlConfig
from middlewars import check_sys_init
from const import *

class TokenCheck:
    def __init__(self) -> None:
        if not check_sys_init():
            using_db = YamlConfig().check_sys_usingdb()
            if using_db == "sqlite":
                self.sql_con = Sqlite_con()
            elif using_db == "mysql":
                self.sql_con = MysqlCon()
            sql = "select value from property where name=\"secret_key\";"
            sql_res = self.sql_con.sql2commit(sql=sql)
            self.secret_key = sql_res[0][0]
            self.algorithm = "HS256"
    # 生成token
    def gen_token(self,payload:dict):
        expire = datetime.timedelta(hours=24)
        curdate = datetime.datetime.now()+expire
        expire_time = curdate.strftime("%Y-%m-%d %H:%M:%S")
        payload.update({"expire":expire_time})
        token = jwt.encode(payload=payload,key=self.secret_key,algorithm=self.algorithm)
        return token
    # 检查token
    def check_token(self,token:str) -> tuple[bool,bool]:
        try:
            res_dict = jwt.decode(token,self.secret_key,self.algorithm)
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
    token = t.gen_token({"asdf":"123","admin":True,"expire":"2024-02-06 18:07:11"})
    print(token)
    print(t.check_token(token=token))