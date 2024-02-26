from random import randint
from datetime import datetime,timedelta

from utils import Sqlite_con,MysqlCon,YamlConfig

class VerifyCode:
    def __init__(self):
        self.yaml_conf = YamlConfig()
        self.using_db = self.yaml_conf.check_sys_usingdb()

    
    # 生成验证码
    def generate_code(self,email:str) -> str:
        if self.using_db == "sqlite":
            self.sql_con = Sqlite_con()
        elif self.using_db == "mysql":
            self.sql_con = MysqlCon()
        code = randint(100000,999999)
        now = datetime.now()
        expire = int((now + timedelta(minutes=30)).timestamp())
        sql = f"select expire from verify_code_temp where email=\"{email}\";"
        res = self.sql_con.sql2commit(sql=sql)
        if res != []:
            if now.timestamp() < res[0][0]:
                return None
        if self.using_db == "sqlite":
            sql1 = f'insert or replace into verify_code_temp(email,code,expire) values("{email}","{code}","{expire}");'
        elif self.using_db == "mysql":
            sql1 = f'insert ignore into verify_code_temp(email,code,expire) values("{email}","{code}","{expire}")as t on duplicate key update email=t.email,code=t.code,expire=t.expire'
        self.sql_con.sql2commit(sql1)
        return str(code)

    # 验证验证码
    def match_code(self,email:str,code_:str) -> bool:
        if self.using_db == "sqlite":
            self.sql_con = Sqlite_con()
        elif self.using_db == "mysql":
            self.sql_con = MysqlCon()
        sql = f"select code,expire from verify_code_temp where email=\"{email}\";"
        res = self.sql_con.sql2commit(sql=sql)
        if res != []:
            code = res[0][0]
            expire = res[0][1]
        now = datetime.now()
        expire_timestamp = datetime.fromtimestamp(float(expire))
        if now > expire_timestamp:
            return False
        if code != code_:
            return False
        return True


if __name__ == "__main__":
    vc = VerifyCode()
    # print(vc.generate_code("test"))
    print(vc.match_code("1002941793@qq.com","489606"))