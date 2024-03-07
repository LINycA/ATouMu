from datetime import datetime

from flask import Response
from loguru import logger

from utils import YamlConfig,Sqlite_con
from const import *


class Artist:
    def get_all_artist(self,user_id:str,page:int,limit:int,order_by:str,order:str,name:str) -> Response:
        if type(page) is not int or type(limit) is not int:
            return PARAMS_ERROR
        order_keys = ["ASC","DESC"]
        if order not in order_keys:
            return PARAMS_ERROR
        sql_con = Sqlite_con()
        filter_name = ""
        if name:
            filter_name = f"""where name like "%{name}%" """
        sql = f'select album_count,external_info_updated_at,full_text,id,name,order_artist_name,size,song_count from artist {filter_name} order by {order_by};'
        curdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        res = sql_con.sql2commit(sql=sql)
        res_dic = [{
                "albumCount": ar[0],
                "externalInfoUpdatedAt": ar[1],
                "fullText": ar[2],
                "genres": None,
                "id": ar[3],
                "name": ar[4],
                "orderArtistName": ar[5],
                "playCount": 0,
                "playDate": curdate,
                "rating": 0,
                "size": ar[6],
                "songCount": ar[7],
                "starred": False,
                "starredAt": curdate
            } for ar in res]
        for ar in res_dic:
            arid = ar.get("id")
            ann_sql = f"""select play_count,rating,starred,starred_at from annotation where user_id="{user_id}" and item_id="{arid}";"""
            ann_res = sql_con.sql2commit(ann_sql)
            print(ann_res)
            if ann_res:
                ann_res = ann_res[0]
                ar.update({
                    "playCount":ann_res[0],
                    "rating":int(ann_res[1]),
                    "starred":bool(ann_res[2]),
                    "starredAt":ann_res[3]
                })
        total_sql = "select count(1) from artist;"
        total_res = sql_con.sql2commit(total_sql)[0][0]
        response = trans_res(res_dic)
        response.headers["x-total-count"] = total_res
        response.headers["x-frame-options"] = "DENY"
        response.headers["permissions-policy"] = "autoplay=(), camera=(), microphone=(), usb=()"
        response.headers["x-content-type-options"] = "nosniff"
        return response