from dbutils.pooled_db import PooledDB
import pymysql
from pymysql.cursors import DictCursor
from . import YamlConfig


class MysqlCon:
    def __init__(self,mode:str=""):
        mysql_conf = YamlConfig().mysql_conf()
        if mode == "init":
            db = "mysql"
        else:
            db = mysql_conf.get("database")
        self.pool = PooledDB(
            creator=pymysql,
            mincached=10,
            maxcached=200,
            blocking=True,
            host=mysql_conf.get("host"),
            port=mysql_conf.get("port"),
            user=mysql_conf.get("user"),
            password=mysql_conf.get("password"),
            database=db
        )

    def sql2dict(self,sql:str) -> dict:
        """
        执行sql语句，并返回dict结果
        :param sql:
        :return:
        """
        con = self.pool.connection()
        with con.cursor(cursor=DictCursor) as cur:
            cur.execute(sql)
            res = cur.fetchall()
        con.close()
        return res

    def sql2commit(self,sql:str) -> int:
        """
        执行sql语句并提交结果，返回执行条目数
        :param sql:
        :return:
        """
        con = self.pool.connection()
        with con.cursor()as cur:
            res = cur.execute(sql)
            con.commit()
        con.close()
        return res

    def manysql2commit(self,sql:str,values:list[list]) -> int:
        """
        执行批量sql语句并提交事务
        :param sql:
        :param values:
        :return:
        """
        con = self.pool.connection()
        with con.cursor()as cur:
            res = cur.executemany(sql,values)
            con.commit()
        con.close()
        return res

if __name__ == '__main__':
    con = MysqlCon(mode="init")
    sql = "show tables;"
    res = con.sql2dict(sql)
    print(res)
