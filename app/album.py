from traceback import format_exc

from flask import Response
from loguru import logger

from utils import YamlConfig,Sqlite_con
from const import *


class Album:
    def get_all_Album(self,page:int,limit:int,order_by:str,order:str) -> Response:
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
        sql = f'select name,artist_name,duration,genre,song_count,full_text,release_time from album {order} limit {page},{limit};'
        res = sql_con.sql2commit(sql=sql)
        res_dic = [{
            "albumArtist":s[1],
            "duration":s[2],
            "name":s[0],
            "fullText":s[5],
            "songCount":s[4]
        } for s in res]
        return trans_res(res_dic)