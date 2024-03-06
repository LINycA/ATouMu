from traceback import format_exc
from os import path,getcwd
from datetime import datetime

from flask import Response
from loguru import logger
from shortuuid import uuid

from utils import Sqlite_con
from const import *

class Songs:
    # 从media_file表获取歌曲信息
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

    # 根据歌手获取歌曲信息
    def get_songs_by_artist(self,count:int,artist:str) -> Response:
        sql_con = Sqlite_con()
        sql = f"""
        select id,album_id,title,album,artist,size,suffix,duration,bit_rate,path,created_at,album_id,artist_id from media_file where artist="{artist}" limit {count};
        """
        res = sql_con.sql2commit(sql=sql)
        res_dic = [{
            "subsonic-response": {
                "status": "ok",
                "version": "1.16.1",
                "type": "navidrome",
                "serverVersion": "0.49.3 (8b93962f)",
                "topSongs": {
                    "song": [
                        {
                            "id": s[0],
                            "parent": s[1],
                            "isDir": False,
                            "title": s[2],
                            "album": s[3],
                            "artist": s[4],
                            "coverArt": s[0],
                            "size": s[5],
                            "contentType": "audio/mpeg",
                            "suffix": s[6],
                            "duration": s[7],
                            "bitRate": s[8],
                            "path": s[9],
                            "created": s[10],
                            "albumId": s[11],
                            "artistId": s[12],
                            "type": "music",
                            "isVideo": False
                        }
                    ]
                }
            }
        }for s in res]
        return trans_res(res_dic)

    # 获取相似歌曲
    def get_similar_songs(self,count:int,media_id:str) -> Response:
        sql = f"""
        select 
        """
    
    # 记录歌曲播放次数
    def scrobble_songs(self,f_time:str,media_id:str,username:str) -> Response:
        def timestamp2strftime(timestamp:str) -> str:
            timestamp = float(timestamp)/1000
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        sql_con = Sqlite_con()
        user_info_sql = f"""
        select user_id from users where user_name="{username}";
        """
        # annotation记录歌曲播放次数
        def annotation_check_update(media_id:str,album_id:str,artist_id:str,userid:str,play_date:str) -> Response:
            curdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = f"""select 1 from annotation where item_id="{media_id}" and user_id="{userid}";"""
            if not sql_con.sql2commit(sql=sql):
                ann_id = uuid()
                insert_mid_sql = f"""insert into annotation(ann_id,user_id,item_id,item_type,play_count,play_date) values("{ann_id}","{userid}","{media_id}","media_file",1,"{curdate}");"""
                sql_con.sql2commit(insert_mid_sql)
            else:
                update_sql = f"""update annotation set play_count=play_count+1,play_date="{play_date}" where user_id="{userid}" and item_id="{media_id}";"""
                sql_con.sql2commit(update_sql)
            sql = f"""select 1 from annotation where item_id="{album_id}" and user_id="{userid}";"""
            if not sql_con.sql2commit(sql=sql):
                ann_id = uuid()
                insert_albid_sql = f"""insert into annotation(ann_id,user_id,item_id,item_type,play_count,play_date) values("{ann_id}","{userid}","{album_id}","album",1,"{curdate}");"""
                sql_con.sql2commit(insert_albid_sql)
            else:
                update_sql = f"""update annotation set play_count=play_count+1,play_date="{play_date}" where user_id="{userid}" and item_id="{album_id}";"""
                sql_con.sql2commit(update_sql)
            sql = f"""select 1 from annotation where item_id="{artist_id}" and user_id="{userid}";"""
            if not sql_con.sql2commit(sql=sql):
                ann_id = uuid()
                insert_artid_sql = f"""insert into annotation(ann_id,user_id,item_id,item_type,play_count,play_date) values("{ann_id}","{userid}","{artist_id}","artist",1,"{curdate}");"""
                sql_con.sql2commit(insert_artid_sql)
            else:
                print("play_count+1")
                update_sql = f"""update annotation set play_count=play_count+1,play_date="{play_date}" where user_id="{userid}" and item_id="{artist_id}";"""
                sql_con.sql2commit(update_sql)
            res = {
                "subsonic-response": {
                    "status": "ok",
                    "version": "1.16.1",
                    "type": "navidrome",
                    "serverVersion": "0.49.3 (8b93962f)"
                }
            }
            return trans_res(res) 
        media_info_sql = f"select album_id,artist_id from media_file where id=\"{media_id}\";"
        userid = sql_con.sql2commit(user_info_sql)[0][0]
        album_id,artist_id = sql_con.sql2commit(media_info_sql)[0]
        play_date = timestamp2strftime(f_time)
        try:
            return annotation_check_update(media_id=media_id,album_id=album_id,artist_id=artist_id,userid=userid,play_date=play_date)
        except:
            logger.error(format_exc())
            return PARAMS_ERROR

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