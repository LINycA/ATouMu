from os import path,getcwd,listdir,mkdir
import time
from threading import Thread
from traceback import format_exc
from datetime import datetime

from mutagen import flac,mp3
from shortuuid import uuid
from loguru import logger

from utils import Sqlite_con,MysqlCon,YamlConfig
from const import *

# 音乐文件扫描
class FileScan:
    # 检测文件夹是否存在，不存在则创建
    def _dir_init(self):
        dir_list = listdir(getcwd())
        if "data" not in dir_list:
            mkdir(path.join(getcwd(),"data"))
            mkdir(path.join(getcwd(),"data","album_img"))
            mkdir(path.join(getcwd(),"data","artist_img"))
            mkdir(path.join(getcwd(),"data","lrcs"))
        if "log" not in dir_list:
            mkdir(path.join(getcwd(),"log"))
    # 文件扫描
    def _scan(self):
        self._dir_init()
        curdate = datetime.now().strftime("%Y-%m-%d")
        logger.add(path.join(getcwd(),"log",f"file_scan_{curdate}.log"))
        logger.info("扫描开始")
        yaml_conf = YamlConfig()
        media_path = yaml_conf.media_path_conf()
        lrc_root_path = path.join(getcwd(),"data","lrcs")
        album_img_root_path = path.join(getcwd(),"data","album_img")
        using_db = yaml_conf.check_sys_usingdb()
        if using_db == "sqlite":
            sql_con = Sqlite_con()
        elif using_db == "mysql":
            sql_con = MysqlCon()
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
                lrc_path = path.join(lrc_root_path,artist+"-"+album+"-"+title+".lrc")
                with open(lrc_path,"w",encoding="utf-8")as f:
                    f.write(lrc)
            album_img_path = ""
            if jpeg is not None and album is not None:
                album_img_path = path.join(album_img_root_path,artist+"-"+album+".jpeg")
                with open(album_img_path,"wb")as f:
                    f.write(jpeg)
            try:
                media_sql = f'insert or ignore into media(id,title,artist_name,album_name,media_path,lyric_path,image_path,size,duration,create_at,update_at) values("{media_id}","{title}","{artist}","{album}","{file_path}","{lrc_path}","{album_img_path}","{size}","{duration}","{curdate}","{curdate}");'
                sql_con.sql2commit(media_sql)
            except:
                logger.error(format_exc())
            try:
                artist_sql = f"insert or ignore into artist(name) values(\"{artist}\");"
                sql_con.sql2commit(artist_sql)
            except:
                logger.error(format_exc())
            if album is not None:
                try:
                    album_sql = f'insert or ignore into album(name,artist_name) values("{album}","{artist}");'
                    sql_con.sql2commit(album_sql)
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
                sql_con.sql2commit(media_sql)
            except:
                logger.error(format_exc())
            try:
                album_sql = f'insert or ignore into album(name,artist_name) values("{album}","");'
                sql_con.sql2commit(album_sql)
            except:
                logger.error(format_exc())
        # 文件扫描
        try:
            file_list = [path.join(media_path,i) for i in listdir(media_path)]
            for file in file_list:
                if path.isdir(file):
                    try:
                        for n in listdir(file):
                            file_list.append(path.join(file,n))
                    except:
                        logger.error(format_exc())
                        continue
                else:
                    file_type = file.split(".")[-1].lower()
                    if file_type == "mp3":
                        try:
                            mp3_info_extract(file_path=file)
                        except:
                            logger.error(format_exc())
                    elif file_type == "flac":
                        try:
                            flac_info_extract(file_path=file)
                        except:
                            logger.error(format_exc())
            logger.success("扫描结束")
        except:
            logger.error(format_exc())
    # 文件扫描工具启动函数
    def start_scan(self):
        try:
            t = Thread(target=self._scan)
            t.setDaemon(True)
            t.start()
            return FILE_SCAN_SUCCESS
        except:
            logger.error(format_exc())
            return FILE_SCAN_FAILED
    # 定时扫描
    def regular_time_scan(self):
        def task_thread():
            while True:
                yaml_conf = YamlConfig()
                curtime = datetime.now().strftime("%H:%M")
                regular_time = yaml_conf.regular_time()
                if curtime == regular_time:
                    self._scan()
                time.sleep(60)         
        t = Thread(target=task_thread)
        t.setDaemon(True)
        t.start()


if __name__ == "__main__":
    fs = FileScan()
    fs.start_scan()