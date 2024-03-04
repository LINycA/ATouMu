from sqlite3 import connect
import sqlite3.dump
from os import path,getcwd
from loguru import logger
from traceback import format_exc
from utils import YamlConfig

class Sqlite_con:
    def __init__(self):
        self.con = connect(path.join(getcwd(),"db","ATouMu.db"))

    def sql2commit(self,sql:str):
        res = self.con.execute(sql)
        self.con.commit()
        return res.fetchall()


if __name__ == '__main__':
    import datetime
    sql_con = Sqlite_con()
    curdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql_test = f"insert into users(user_id,user_name,nick_name,password,email,create_time) values(1,1,1,1,1,\"{curdate}\");"
    # sql_test = "select * from users;"
    try:
        res = sql_con.sql2commit(sql_test)
    except:
        logger.error(format_exc())
    print(res)