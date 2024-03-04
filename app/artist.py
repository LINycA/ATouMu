from traceback import format_exc

from flask import Response
from loguru import logger

from utils import YamlConfig,Sqlite_con
from const import *


class Artist:
    def get_all_artist(self,page:int,limit:int,order_by:str,order:str) -> Response:
        print(page,limit,order_by,order)
        if type(page) is not int or type(limit) is not int:
            return PARAMS_ERROR
        # order_by_keys = ["id","title","artist_name","genre_id"]
        # if order_by not in order_by_keys:
            # return PARAMS_ERROR
        order_keys = ["ASC","DESC"]
        if order not in order_keys:
            return PARAMS_ERROR
        sql_con = Sqlite_con()
        sql = f'select name from artist {order} limit {page},{limit};'
        res = sql_con.sql2commit(sql=sql)
        res_dic = [{
            "name":s[0]
        } for s in res]
        print(res_dic)
        return trans_res(res_dic)