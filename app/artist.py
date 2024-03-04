from traceback import format_exc

from flask import Response
from loguru import logger

from utils import YamlConfig,Sqlite_con
from const import *


class Artist:
    def get_all_artist(self,page:int,limit:int,order_by:str,order:str) -> Response:
        if type(page) is not int or type(limit) is not int:
            return PARAMS_ERROR
        # order_by_keys = ["id","title","artist_name","genre_id"]
        # if order_by not in order_by_keys:
            # return PARAMS_ERROR
        order_keys = ["ASC","DESC"]
        if order not in order_keys:
            return PARAMS_ERROR
        sql_con = Sqlite_con()
        sql = f'select album_count,external_info_updated_at,full_text,id,name,order_artist_name,song_count from artist {order} limit {page},{limit};'
        res = sql_con.sql2commit(sql=sql)
        print(res)
        res_dic = [{
            "albumCount": s[0],
            "externalInfoUpdatedAt": s[1],
            "fullText": s[2],
            "genres": "",
            "id": s[3],
            "name": s[4],
            "orderArtistName": s[5],
            "playCount": 1,
            "playDate": "2024-03-04T05:00:39Z",
            "rating": 0,
            "size": 81752024,
            "songCount": s[6],
            "starred": False,
            "starredAt": "0001-01-01T00:00:00Z"
        } for s in res]
        total_sql = "select count(1) from artist;"
        total_res = sql_con.sql2commit(total_sql)[0][0]
        response = trans_res(res_dic)
        response.headers["x-total-count"] = total_res
        response.headers["x-frame-options"] = "DENY"
        response.headers["permissions-policy"] = "autoplay=(), camera=(), microphone=(), usb=()"
        response.headers["x-content-type-options"] = "nosniff"
        return response