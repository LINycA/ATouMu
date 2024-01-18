from sqlite3 import connect
from os import path,getcwd


class Sqllite_con:
    def __init__(self):
        self.con = connect(path.join(getcwd(),"db","music.db"))

    def sql2dict(self,sql:str):
        res = self.con.execute(sql)
        return res.fetchall()



if __name__ == '__main__':
    sql_con = Sqllite_con()
    sql_con.sql2dict()