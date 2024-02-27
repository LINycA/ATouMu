from os import path,getcwd,listdir
from threading import Thread
from traceback import format_exc
from datetime import datetime

from mutagen import id3,flac,mp3
from hashlib import md5
from shortuuid import uuid
from loguru import logger

from utils import Sqlite_con,MysqlCon,YamlConfig


# 音乐文件扫描
class FileScan:
    def __init__(self):
        self.yaml_conf = YamlConfig()
        self.media_path = self.yaml_conf.media_path_conf()
        self.using_db = self.yaml_conf.check_sys_usingdb()
        self.lrc_root_path = path.join(getcwd(),"data","lrcs")
        self.album_img_root_path = path.join(getcwd(),"data","album_img")

    def scan(self):
        if self.using_db == "sqlite":
            self.sql_con = Sqlite_con()
        elif self.using_db == "mysql":
            self.sql_con = MysqlCon()
        # mp3文件信息提取
        def mp3_info_extract(file_path:str):
            size = round(path.getsize(file_path)/(1024**2),1)
            info = mp3.MP3(file_path)
            duration = info.info.length
            media_id = uuid(file_path)
            title = str(info.get("TIT2"))
            artist = str(info.get("TPE1"))
            lrc = str(info.get("USLT::eng"))
            album = str(info.get("TALB"))
            jpeg = info.get("APIC:").__dict__.get("data")
            curdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lrc_path = ""
            if lrc is not None and album is not None:
                lrc_path = path.join(self.lrc_root_path,artist+"-"+album+"-"+title+".lrc")
                with open(lrc_path,"w",encoding="utf-8")as f:
                    f.write(lrc)
            album_img_path = ""
            if jpeg is not None and album is not None:
                album_img_path = path.join(self.album_img_root_path,artist+"-"+album+".jpeg")
                with open(album_img_path,"wb")as f:
                    f.write(jpeg)
            try:
                media_sql = f'insert or ignore into media(id,title,artist_name,album_name,media_path,lyric_path,image_path,size,duration,create_at,update_at) values("{media_id}","{title}","{artist}","{album}","{file_path}","{lrc_path}","{album_img_path}","{size}","{duration}","{curdate}","{curdate}");'
                self.sql_con.sql2commit(media_sql)
            except:
                logger.error(format_exc())
            try:
                artist_sql = f"insert or ignore into artist(name) values(\"{artist}\");"
                self.sql_con.sql2commit(artist_sql)
            except:
                logger.error(format_exc())
            if album is not None:
                try:
                    album_sql = f'insert or ignore into album(name,artist_name) values("{album}","{artist}");'
                    self.sql_con.sql2commit(album_sql)
                except:
                    logger.error(format_exc())
        # flac文件信息提取
        def flac_info_extract(file_path:str):
            size = round(path.getsize(file_path)/(1024**2),1)
            info = flac.FLAC(file_path)
            duration = info.info.length
            media_id = uuid(file_path)
            title = str(info.get("title")[0])
            album = str(info.get("album")[0])
            curdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if album is None:
                logger.warning(file_path+"缺少专辑名称")
            try:
                media_sql = f'insert or ignore into media(id,title,album_name,media_path,size,duration,create_at,update_at) values("{media_id}","{title}","{album}","{file_path}","{size}","{duration}","{curdate}","{curdate}");'
                self.sql_con.sql2commit(media_sql)
            except:
                logger.error(format_exc())
            try:
                album_sql = f'insert or ignore into album(name,artist_name) values("{album}","");'
                self.sql_con.sql2commit(album_sql)
            except:
                logger.error(format_exc())

        # 文件扫描
        file_list = [path.join(self.media_path,i) for i in listdir(self.media_path)]
        curdate = datetime.now().strftime("%Y-%m-%d")
        logger.add(path.join(getcwd(),"log",f"file_scan_{curdate}.log"),colorize=True)
        for file in file_list:
            if path.isdir(file):
                for n in listdir(file):
                    file_list.append(path.join(file,n))
            else:
                file_type = file.split(".")[-1].lower()
                if file_type == "mp3":
                    mp3_info_extract(file_path=file)
                elif file_type == "flac":
                    flac_info_extract(file_path=file)


if __name__ == "__main__":
    fs = FileScan()
    fs.scan()