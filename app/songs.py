from traceback import format_exc
from os import path,getcwd
from datetime import datetime

from flask import Response
from loguru import logger

from utils import Sqlite_con
from const import *

class Songs:
    def get_all_song(self,page:int,limit:int,order_by:str,order:str) -> Response:
        if type(page) is not int or type(limit) is not int:
            return PARAMS_ERROR
        order_by_keys = ["id","title","artist_name","genre_id"]
        if order_by not in order_by_keys:
            return PARAMS_ERROR
        order_keys = ["ASC","DESC"]
        if order not in order_keys:
            return PARAMS_ERROR
        sql_con = Sqlite_con()
        media_file_sql = f"""select 
         album,album_artist,album_artist_id,album_id,artist,
         artist_id,bit_rate,channels,compilation,created_at,
         disc_number,duration,full_text,genre,has_cover_art,
         id,order_album_artist_name,order_album_name,order_artist_name,order_title,
         path,rg_album_gain,rg_album_peak,rg_track_gain,rg_track_peak,
         size,suffix,title,track_number,updated_at,
         year from media_file order by {order_by} {order} limit {page},{limit};"""
        media_file_res = sql_con.sql2commit(sql=media_file_sql)
        curdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        res_dic = [{
            "album": s[0],
            "albumArtist": s[1],
            "albumArtistId": s[2],
            "albumId": s[3],
            "artist": s[4],
            "artistId": s[5],
            "bitRate": s[6],
            "bookmarkPosition": "",
            "channels": s[7],
            "compilation": s[8],
            "createdAt": s[9],
            "discNumber": s[10],
            "duration": s[11],
            "fullText": s[12],
            "genre": s[13],
            "genres": None,
            "hasCoverArt": bool(s[14]),
            "id": s[15],
            "lyrics":"",
            "orderAlbumArtistName": s[16],
            "orderAlbumName": s[17],
            "orderArtistName": s[18],
            "orderTitle": s[19],
            "path": s[20],
            "playCount": 0,
            "playDate": curdate,
            "rating": 0,
            "rgAlbumGain": s[21],
            "rgAlbumPeak": s[22],
            "rgTrackGain": s[23],
            "rgTrackPeak": s[24],
            "size": s[25],
            "starred": False,
            "starredAt": curdate,
            "suffix": s[26],
            "title": s[27],
            "trackNumber": s[28],
            "updatedAt": s[29],
            "year": s[30]
        } for s in media_file_res]
        for f in res_dic:
            mid = f.get("id")
            lrc_path = path.join(getcwd(),"data","lrcs",mid+".lrc")
            if path.exists(lrc_path):
                with open(lrc_path,"r",encoding="utf-8")as lrcf:
                    lrc = lrcf.read()
                f.update({"lyrics":lrc})
            annotation_sql = f"select play_count,play_date,rating,starred,starred_at from annotation where item_id = \"{mid}\";"
            annotation_res = sql_con.sql2commit(annotation_sql)
            if annotation_res:
                f.update({
                    "playCount":annotation_res[0],
                    "playDate":annotation_res[1],
                    "rating":annotation_res[2],
                    "starred":annotation_res[3],
                    "starred_at":annotation_res[4]
                })
        total_sql = "select count(1) from media_file;"
        total = sql_con.sql2commit(total_sql)[0][0]

        response = trans_res(res_dic)
        response.headers["x-total-count"] = total
        response.headers["x-frame-options"] = "DENY"
        response.headers["permissions-policy"] = "autoplay=(), camera=(), microphone=(), usb=()"
        response.headers["x-content-type-options"] = "nosniff"
        return response

    # 获取媒体文件路径
    def get_song_path(self,id:str) -> str:
        get_path_sql = f"select path,duration from media_file where id=\"{id}\""
        sql_con = Sqlite_con()
        res = sql_con.sql2commit(get_path_sql)[0]
        try:
            res_data = {
                "file_path":res[0],
                "duration":res[1]
            }
            return res_data
        except:
            logger.error(format_exc())
            return None