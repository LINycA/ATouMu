from os import path,getcwd,listdir
from threading import Thread
import wave

from mutagen import id3,flac,mp3
from shortuuid import uuid

from utils import Sqlite_con,MysqlCon,YamlConfig


# 音乐文件扫描
class FileScan:
    def __init__(self):
        self.yaml_conf = YamlConfig()
        self.media_path = self.yaml_conf.media_path_conf()
        self.using_db = self.yaml_conf.check_sys_usingdb()

    def scan(self):
        if self.using_db == "sqlite":
            self.sql_con = Sqlite_con()
        elif self.using_db == "mysql":
            self.sql_con = MysqlCon()
        # mp3文件信息提取
        def mp3_info_extract(file_path:str):
            info = mp3.MP3(file_path)
            duration = info.info.length
            title = str(info.get("TIT2"))
            artist = str(info.get("TPE1"))
            lrc = str(info.get("USLT::eng"))
            album = str(info.get("TALB"))
            jpeg = info.get("APIC:").__dict__.get("data")
            if lrc is not None:
                with open(path.join(getcwd(),"data","lrcs",artist+"-"+album+"-"+title+".lrc"),"w",encoding="utf-8")as f:
                    f.write(lrc)
            if jpeg is not None and album is not None:
                with open(path.join(getcwd(),"data","album_img",artist+"-"+album+".jpeg"),"wb")as f:
                    f.write(jpeg)
            # media_id = uuid()
            # media_sql = f'insert into media(id,title,artist_name,album_name,media_path,lyric_path,image_path,)'
            # artist_sql = f"insert into artist(name) values(\"{artist}\");"

            
        # 文件扫描
        file_list = [path.join(self.media_path,i) for i in listdir(self.media_path)]
        for file in file_list:
            if path.isdir(file):
                for n in listdir(file):
                    file_list.append(path.join(file,n))
            else:
                file_type = file.split(".")[-1]
                if file_type == "mp3":
                    mp3_info_extract(file_path=file)

if __name__ == "__main__":
    fs = FileScan()
    fs.scan()