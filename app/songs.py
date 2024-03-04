from traceback import format_exc

from flask import Response
from loguru import logger

from utils import YamlConfig,Sqlite_con
from const import *

class Songs:
    def get_all_song(self,page:int,limit:int,order_by:str,order:str) -> Response:
        print(page,limit,order_by,order)
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
         album,album_artist,album_artist_id,album_id,artist,artist_id,bit_rate,channels,compilation,created_at,disc_number,duration,full_text,
         genre,has_cover_art,id,order_album_artist_name,order_album_name,order_artist_name,order_title,path,rg_album_gain,
         rg_track_gain,rg_track_peak,size,suffix,title,track_number,updated_at,year from media_file order by {order_by} {order} limit {page},{limit};"""
        media_file_res = sql_con.sql2commit(sql=media_file_sql)
        res_dic = [{
            "album": s[0],
            "albumArtist": s[1],
            "albumArtistId": s[2],
            "albumId": s[3],
            "artist": s[4],
            "artistId": s[5],
            "bitRate": s[6],
            "bookmarkPosition": ...,
            "channels": s[7],
            "compilation": s[8],
            "createdAt": s[9],
            "discNumber": s[10],
            "duration": s[11],
            "fullText": s[12],
            "genre": s[13],
            "genres": "",
            "hasCoverArt": s[14],
            "id": s[15],
            "orderAlbumArtistName": s[16],
            "orderAlbumName": s[17],
            "orderArtistName": s[18],
            "orderTitle": s[19],
            "path": s[20],
            "playCount": '',
            "playDate": '',
            "rating": '',
            "rgAlbumGain": s[21],
            "rgAlbumPeak": s[22],
            "rgTrackGain": s[23],
            "rgTrackPeak": s[24],
            "size": s[25],
            "starred": '',
            "starredAt": '',
            "suffix": s[26],
            "title": s[27],
            "trackNumber": s[28],
            "updatedAt": s[29],
            "year": s[30]
        } for s in media_file_res]
        for f in res_dic:
            mid = f.get("id")
            annotation_sql = f"select play_count,play_date,rating,starred,starred_at where item_id = \"{mid}\";"
            annotation_res = sql_con.sql2commit(annotation_sql)
            f.update({
                "playCount":annotation_res[0],
                "playDate":annotation_res[1],
                "rating":annotation_res[2],
                "starred":annotation_res[3],
                "starred_at":annotation_res[4]
            })
        return trans_res(res_dic)