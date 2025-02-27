from os import path,getcwd,listdir,mkdir
import time
from hashlib import md5
from threading import Thread
from traceback import format_exc
from datetime import datetime
from base64 import b64decode

from mutagen import flac,mp3
from loguru import logger

from utils import Sqlite_con,YamlConfig
from middlewars import calculation_table_info
from const import *

# 音乐文件扫描
class FileScan:
    # 检测文件夹是否存在，不存在则创建
    def _dir_init(self):
        data_path = path.join(getcwd(),"data")
        if not path.exists(data_path):
            mkdir(data_path)
        dir_list = listdir(data_path)
        if "album_img" not in dir_list:
            mkdir(path.join(getcwd(),"data","album_img"))
        if "artist_img" not in dir_list:
            mkdir(path.join(getcwd(),"data","artist_img"))
        if "lrcs" not in dir_list:
            mkdir(path.join(getcwd(),"data","lrcs"))
        if "background" not in dir_list:
            mkdir(path.join(getcwd(),"data","background"))
        if not path.exists(path.join(getcwd(),"log")):
            mkdir(path.join(getcwd(),"log"))
        self.unkown_artist = "unkown"
        self.unkown_artist_id = md5(self.unkown_artist.encode()).hexdigest()
    # 文件扫描
    def _scan(self):
        self._dir_init()
        curdate = datetime.now().strftime("%Y-%m-%d")
        logger.add(path.join(getcwd(),"log",f"file_scan_{curdate}.log"))
        yaml_conf = YamlConfig()
        media_path = yaml_conf.media_path_conf()
        lrc_root_path = path.join(getcwd(),"data","lrcs")
        album_img_root_path = path.join(getcwd(),"data","album_img")
        sql_con = Sqlite_con()

        # 写入数据库
        def insert2db(media_id:str,file_path:str,title:str,album:str,album_id:str,artist:str,artist_id:str,has_cover_art:bool,size:int,suffix:str,duration:float,bitrate:int,full_text:str,channels:int,lrc_path:str,image_path:str):
            curdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                media_sql = f"""insert or replace into media_file
                (id,path,title,album,album_id,artist,artist_id,album_artist,has_cover_art,size,suffix,duration,bit_rate,created_at,updated_at,full_text,album_artist_id,order_album_name,
                order_album_artist_name,order_artist_name,lyrics,channels,order_title,rg_album_gain,rg_album_peak,rg_track_gain,rg_track_peak,image_path)
                values
                ("{media_id}","{file_path}","{title}","{album}","{album_id}","{artist}","{artist_id}","{artist}",{has_cover_art},"{size}","{suffix}","{duration}",
                {bitrate},"{curdate}","{curdate}","{full_text}","{artist_id}","{album}","{artist}","{artist}","{lrc_path}","{channels}","{title}",0,1,0,1,"{image_path}");"""
                sql_con.sql2commit(media_sql)
            except:
                logger.error(format_exc())
            try:
                artist_sql = f"""insert or ignore into artist
                (id,name,full_text,order_artist_name,external_info_updated_at) 
                values("{artist_id}","{artist}","{artist}","{artist}","{curdate}");"""
                sql_con.sql2commit(artist_sql)
            except:
                logger.error(format_exc())
            if album is not None:
                try:
                    album_sql = f"""insert or ignore into album
                    (id,name,artist_id,embed_art_path,artist,album_artist,created_at,updated_at,full_text,album_artist_id,order_album_name,order_album_artist_name,all_artist_ids,external_info_updated_at) 
                    values
                    ("{album_id}","{album}","{artist_id}","{file_path}","{artist}","{artist}","{curdate}","{curdate}","{full_text}","{artist_id}","{album}","{artist}","{artist_id}","{curdate}");"""
                    sql_con.sql2commit(album_sql)
                except:
                    logger.error(format_exc())

        # 生成id
        def get_media_id(file_path:str) -> str:
            with open(file_path,"rb")as f:
                mid = md5(f.read()).hexdigest()
            return mid
        
        # mp3文件信息提取
        def mp3_info_extract(file_path:str):
            size = path.getsize(file_path)
            info = mp3.MP3(file_path)
            bitrate = info.info.bitrate // 1000
            channels = info.info.channels
            suffix = "mp3"
            duration = info.info.length
            media_id = get_media_id(file_path=file_path)
            title = str(info.get("TIT2"))
            artist = str(info.get("TPE1")) if info.get("TPE1") else self.unkown_artist
            artist_id = md5(artist.encode()).hexdigest()
            if not artist:
                artist = self.unkown_artist
                artist_id = self.unkown_artist_id
            lrc = str(info.get("USLT::eng"))
            album = str(info.get("TALB")) if info.get("TALB") else self.unkown_artist
            album_id = md5(album.encode()).hexdigest()
            try:
                jpeg = info.get("APIC:").__dict__.get("data")
            except:
                jpeg = None
            has_cover_art = False
            if jpeg:
                has_cover_art = True
            lrc_path = "none"
            album_img_path = "none"
            if lrc:
                lrc_path = path.join(lrc_root_path,media_id+".lrc")
                with open(lrc_path,"w",encoding="utf-8")as f:
                    f.write(lrc)
            if jpeg:
                album_img_path = path.join(album_img_root_path,album_id+".jpeg")
                if not path.exists(album_img_path):
                    with open(album_img_path,"wb")as f:
                        f.write(jpeg)
            full_text = " ".join([artist,album,title])
            insert2db(media_id=media_id,file_path=file_path,title=title,album=album,album_id=album_id,artist=artist,artist_id=artist_id,
                      has_cover_art=has_cover_art,size=size,suffix=suffix,duration=duration,bitrate=bitrate,full_text=full_text,channels=channels,lrc_path=lrc_path,image_path=album_img_path)
            
        # flac文件信息提取
        def flac_info_extract(file_path:str):
            suffix = "flac"
            size = path.getsize(file_path)
            info = flac.FLAC(file_path)
            bitrate = info.info.bitrate // 1000
            channels = info.info.channels
            duration = info.info.length
            media_id = get_media_id(file_path=file_path)
            title = str(info.get("title")[0])
            album = info.get("album")[0] if info.get("album") else self.unkown_artist
            img_data = info.get("images") if info.get("images") else None
            lrc_data = info.get("lrc") if info.get("lrc") else None
            artist = info.get("artist")[0] if info.get("artist") else self.unkown_artist
            album_id = md5(album.encode()).hexdigest()
            has_cover_art = False
            artist_id = md5(artist.encode()).hexdigest()
            lrc_path = None
            img_path = None
            if lrc_data:
                lrc_path = path.join(getcwd(),"data","lrcs",media_id+".lrc")
                with open(lrc_path,"w",encoding="utf-8")as f:
                    f.write(lrc_data[0])
            if img_data:
                img_path = path.join(getcwd(),"data","album_img",album_id+".jpeg")
                img_data = b64decode(img_data[0])
                with open(img_path,"rb")as f:
                    f.write(img_data)
            insert2db(media_id=media_id,file_path=file_path,title=title,album=album,album_id=album_id,artist=artist,artist_id=artist_id,has_cover_art=has_cover_art,
                      size=size,suffix=suffix,duration=duration,bitrate=bitrate,full_text=artist,channels=channels,lrc_path=lrc_path,image_path=img_path)
            
        # 文件扫描
        try:
            file_list = [path.join(media_path,i) for i in listdir(media_path)]
            logger.info("扫描开始")
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
                            logger.error(format_exc()+file)
                    elif file_type == "flac":
                        try:
                            flac_info_extract(file_path=file)
                        except:
                            logger.error(format_exc())
            calculation_table_info()
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
    # 获取扫描状态，
    def get_scan_status(self):
        sql_con = Sqlite_con()
        curtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql_media_count = "select count(1) from media_file;"
        media_count = sql_con.sql2commit(sql_media_count)[0][0]
        data = trans_res({
            "subsonic-response":{
                "status":"ok",
                "version":"1.16.1",
                "type":"navidrome",
                "serverVersion":"0.49.3 (8b93962f)",
                "openSubsonic":True,
                "scanStatus":{
                    "scanning":False,
                    "count":media_count,
                    "folderCount":1,
                    "lastScan":curtime
                }
            }
        })
        return data

if __name__ == "__main__":
    fs = FileScan()
    fs._scan()