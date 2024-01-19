from sqlite3 import connect
from os import path
from loguru import logger
from utils import YamlConfig

class Sqlite_con:
    def __init__(self):
        sqlite_conf = YamlConfig().sqlite_conf()
        if sqlite_conf:
            self.con = connect(path.join(sqlite_conf.get("path"),"ATouMu.db"))

    def sql2list(self,sql:str):
        try:
            res = self.con.execute(sql)
            return res.fetchall()
        except Exception as e:
            logger.error("配置文件未初始化"+str(e))
            return False


if __name__ == '__main__':
    sql_con = Sqlite_con()
    print(sql_con)
    res = sql_con.sql2list("select name from sqlite_master where type='table';")
    for table in res:
        table = table[0]
        res1 = sql_con.sql2list(f"pragma table_info('{table}')")
        cloumn_list = tuple([i[1] for i in res1])
        sql_create_index = f"create index {table}_index on {table} {str(cloumn_list)}"
        sql_con.sql2list(sql_create_index)