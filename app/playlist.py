from datetime import datetime
from os import path

from flask import Response
from shortuuid import uuid

from utils import Sqlite_con,trans_res

class Playlist:
    # 新增歌单
    def playlist_add(self,name:str,comment:str,public:bool,user_id:str) -> Response:
        sql_con = Sqlite_con()
        curdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pid = uuid()
        playlist_insert_sql = f"""insert into playlist(id,name,comment,public,created_time,updated_time,owner_id,evaluated_at) values("{pid}","{name}","{comment}",{public},"{curdate}","{curdate}","{user_id}","{curdate}");"""
        sql_con.sql2commit(playlist_insert_sql)
        res_dict = {"id":pid}
        return trans_res(res_dict)

    # 歌单查询
    def playlist_get(self,order_by:str,limit:int,offset:int) -> Response:
        sql_con = Sqlite_con()
        playlist_sql = f"""select id,name,comment,duration,size,song_count,owner_id,public,path,sync,created_time,updated_time,rules,evaluated_at from playlist order by {order_by};"""
        playlist_res = sql_con.sql2commit(playlist_sql)
        res_dict = [{
        "id": s[0],
        "name": s[1],
        "comment": s[2],
        "duration": s[3],
        "size": s[4],
        "songCount": s[5],
        "ownerName": "",
        "ownerId": s[6],
        "public": bool(s[7]),
        "path": s[8],
        "sync": bool(s[9]),
        "createdAt": s[10],
        "updatedAt": s[11],
        "rules": s[12],
        "evaluatedAt": s[13]
        }for s in playlist_res]
        for p in res_dict:
            oid = p.get("ownerId")
            get_name_sql = f"""select user_name from users where user_id="{oid}";"""
            name_res = sql_con.sql2commit(get_name_sql)[0]
            p.update({"ownerName":name_res[0]})
        return trans_res(res_dict)

    # 歌单删除
    def playlist_delete(self,pid:str) -> Response:
        sql_con = Sqlite_con()
        delete_playlist_sql = f"""delete from playlist where id="{pid}";"""
        deltele_playlist_track_sql = f"""delete from playlist_track where playlist_id="{pid}";"""
        sql_con.sql2commit(deltele_playlist_track_sql)
        sql_con.sql2commit(delete_playlist_sql)
        return trans_res({"ret":200,"msg":"删除成功"})

    # 歌单增加歌曲
    def playlist_song_add(self,sids:list,pid:str) -> Response:
        sql_con = Sqlite_con()
        num_res_sql = f"""select count(1) from playlist_track where playlist_id="{pid}";"""
        num_res = sql_con.sql2commit(num_res_sql)[0][0]
        for sid in sids:
            num_res += 1
            playlist_songs_id = f"""insert or replace into playlist_track(id,playlist_id,media_file_id) values({num_res},"{pid}","{sid}");"""
            sql_con.sql2commit(playlist_songs_id)
        return trans_res({"added":len(sids)})
    
    # 歌单歌曲查询
    def playlist_song_get(self,pid:str,offset:int,limit:int,order:str,order_by:str,user_id:str) -> Response:
        sql_con = Sqlite_con()
        get_mid_sql = f"""select id,media_file_id from playlist_track where playlist_id="{pid}" order by {order_by} {order};"""
        mid_res = sql_con.sql2commit(get_mid_sql)
        res_dict = [{
            "bookmarkPosition": 0,
            "genres": None,
            "id": str(m[0]),
            "mediaFileId": m[1],
            "playCount": 0,
            "playDate": "",
            "playlistId": pid,
            "rating": 0,
            "starred": False,
            "starredAt": "0001-01-01T00:00:00Z",
        }for m in mid_res]
        for m in res_dict:
            mid = m.get("mediaFileId")
            media_sql = f"""select 
            album,album_artist,album_artist_id,album_id,artist,
            artist_id,bit_rate,channels,compilation,created_at,
            disc_number,duration,full_text,genre,has_cover_art,
            lyrics,order_album_artist_name,order_album_name,order_artist_name,order_title,
            path,rg_album_gain,rg_album_peak,rg_track_gain,rg_track_peak,
            size,suffix,title,track_number,updated_at,
            year
            from media_file where id="{mid}";
            """
            anno_sql = f"""select 
            play_count,play_date,rating,starred,starred_at from annotation where item_id="{mid}" and user_id="{user_id}";
            """
            anno_res = sql_con.sql2commit(anno_sql)
            if anno_res:
                anno_res = anno_res[0]
                m.update({
                    "playCount":anno_res[0],
                    "playDate":anno_res[1],
                    "rating":anno_res[2],
                    "starred":bool(anno_res[3]),
                    "starredAt":anno_res[4]
                })
            media_res = sql_con.sql2commit(media_sql)[0]
            lyrics = ""
            if path.exists(media_res[15]):
                with open(media_res[15],"r",encoding="utf-8")as f:
                    lyrics = f.read()
            m.update({
                "album": media_res[0],
                "albumArtist": media_res[1],
                "albumArtistId": media_res[2],
                "albumId": media_res[3],
                "artist": media_res[4],
                "artistId": media_res[5],
                "bitRate": int(media_res[6]),
                "channels": int(media_res[7]),
                "compilation": bool(media_res[8]),
                "createdAt": media_res[9],
                "discNumber": int(media_res[10]),
                "duration": round(float(media_res[11]),2),
                "fullText": media_res[12],
                "genre": media_res[13],
                "hasCoverArt": bool(media_res[14]),
                "lyrics": lyrics,
                "orderAlbumArtistName": media_res[16],
                "orderAlbumName": media_res[17],
                "orderArtistName": media_res[18],
                "orderTitle": media_res[19],
                "path": media_res[20],
                "rgAlbumGain": media_res[21],
                "rgAlbumPeak": media_res[22],
                "rgTrackGain": media_res[23],
                "rgTrackPeak": media_res[24],
                "size": media_res[25],
                "suffix": media_res[26],
                "title": media_res[27],
                "trackNumber": media_res[28],
                "updatedAt": media_res[29],
                "year": media_res[30]
            })
        return trans_res(res_dict)

    # 歌单歌曲删除
    def playlist_song_delete(self,pid:str,sid:str) -> Response:
        sql_con = Sqlite_con()
        delete_song_sql = f"""delete from playlist_track where id="{sid}" and playlist_id="{pid}";"""
        sql_con.sql2commit(delete_song_sql)
        return trans_res({"ret":200,"msg":"歌曲移除成功"})