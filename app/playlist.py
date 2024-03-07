from datetime import datetime

from flask import Response
from shortuuid import uuid

from utils import Sqlite_con,trans_res

class Playlist:
    # 新增歌单
    def playlist_add(self,name:str,comment:str,public:bool,user_id:str) -> Response:
        sql_con = Sqlite_con()
        curdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pid = uuid()
        playlist_insert_sql = f"""insert into playlist(id,name,comment,public,created_time,updated_time,owner_id) values("{pid}","{name}","{comment}",{public},"{curdate}","{curdate}","{user_id}");"""
        sql_con.sql2commit(playlist_insert_sql)
        res_dict = {"id":pid}
        return trans_res(res_dict)

    # 