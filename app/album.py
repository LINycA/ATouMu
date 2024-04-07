from traceback import format_exc

from flask import Response
from loguru import logger

from utils import YamlConfig,Sqlite_con
from const import *


class Album:
    def get_all_Album(self,page:int,limit:int,order_by:str,order:str,name:str) -> Response:
        if type(page) is not int or type(limit) is not int:
            return PARAMS_ERROR
        if page < 0 or limit < 1 or limit > 1000:
            return PARAMS_ERROR
        order_by_dict = {"recently_added":"created_at","createdAt":"created_at","name":"name","artist":"artist"}
        if order_by not in order_by_dict:
            return PARAMS_ERROR
        order_by = order_by_dict.get(order_by)
        filter_name = ""
        if name:
            filter_name = f"""where name like "%{name}%" """
        order_keys = ["ASC","DESC"]
        if order not in order_keys:
            return PARAMS_ERROR
        sql_con = Sqlite_con()
        sql = f"""select 
        album_artist,album_artist_id,all_artist_ids,artist,artist_id,compilation,created_at,duration,embed_art_path,
        external_info_updated_at,full_text,genre,id,max_year,min_year,name,order_album_artist_name,order_album_name,size,song_count,updated_at from album {filter_name} order by {order_by} {order} limit {page},{limit};"""
        res = sql_con.sql2commit(sql=sql)
        res_dic = [{
            "albumArtist": s[0],
            "albumArtistId": s[1],
            "allArtistIds": s[2],
            "artist": s[3],
            "artistId": s[4],
            "compilation": s[5],
            "createdAt": s[6],
            "duration": s[7],
            "embedArtPath": s[8],
            "externalInfoUpdatedAt": s[9],
            "fullText": s[10],
            "genre": s[11],
            "genres": s[11],
            "id": s[12],
            "maxYear": s[13],
            "minYear": s[14],
            "name": s[15],
            "orderAlbumArtistName": s[16],
            "orderAlbumName": s[17],
            "paths": "/Users/cds-dn-589/Development/ATouMu/",
            "playCount": "",
            "playDate": "",
            "rating": "",
            "size": "",
            "songCount": s[18],
            "starred": False,
            "starredAt": "0001-01-01T00:00:00Z",
            "updatedAt": s[19]
        } for s in res]
        total_sql = "select count(1) from album;"
        total_res = sql_con.sql2commit(total_sql)[0][0]
        response = trans_res(res_dic)
        response.headers["x-total-count"] = total_res
        response.headers["x-frame-options"] = "DENY"
        response.headers["permissions-policy"] = "autoplay=(), camera=(), microphone=(), usb=()"
        response.headers["x-content-type-options"] = "nosniff"
        return response
    
    def get_album_detail(self,album_id:str,user_id:str) -> Response:
        sql_con = Sqlite_con()
        album_sql = f"""select artist,artist_id,created_at,duration,full_text,genre,id,max_year,min_year,name,size,song_count,updated_at from album where id = '{album_id}';"""
        album_res = sql_con.sql2commit(sql=album_sql)[0]
        album_play_count_sql = f""" select sum(play_count) from annotation where item_id='{album_id}' and item_type='album'; """
        album_play_count_res = sql_con.sql2commit(sql=album_play_count_sql)
        album_play_count_res = album_play_count_res[0][0] if album_play_count_res[0][0] else 0
        album_play_date_sql = f"""select play_date from annotation where item_id='{album_id}' and item_type='album' order by play_date desc limit 1;"""
        album_play_date_res = sql_con.sql2commit(sql=album_play_date_sql)
        album_play_date_res = album_play_date_res[0] if album_play_date_res else "1970-01-01"
        album_starred_sql = f"""select starred,starred_at from annotation where item_id='{album_id}' and item_type='album' and user_id='{user_id}';"""
        album_starred_res = sql_con.sql2commit(sql=album_starred_sql)
        album_starred_res = album_starred_res if album_starred_res else (False,"1970-01-01")
        logger.info(album_starred_res)
        res_dict = {
            "albumArtist": album_res[0],
            "albumArtistId": album_res[1],
            "allArtistIds": album_res[1],
            "artist": album_res[0],
            "artistId": album_res[0],
            "compilation": False,
            "createdAt": album_res[2],
            "duration": album_res[3],
            "fullText": album_res[4],
            "genre": album_res[5],
            "genres": None,
            "id": album_res[6],
            "maxYear": album_res[7],
            "minYear": album_res[8],
            "name": album_res[9],
            "orderAlbumArtistName": album_res[0],
            "orderAlbumName": album_res[9],
            "playCount": album_play_count_res,
            "playDate": album_play_date_res,
            "size": album_res[10],
            "songCount": album_res[11],
            "starred": album_starred_res[0],
            "starredAt": album_starred_res[1],
            "updatedAt": album_res[12]
        }
        return trans_res(res_dict)