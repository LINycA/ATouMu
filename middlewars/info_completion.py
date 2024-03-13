import asyncio
import time
from os import path,getcwd
from base64 import b64encode
from traceback import format_exc
from datetime import datetime
from threading import Thread
from hashlib import md5
from parsel import Selector

import httpx
from mutagen import mp3,flac,id3
from loguru import logger
from requests import get

from utils import Sqlite_con
from middlewars import calculation_table_info
from const import *


class InfoCompletion:
    def __init__(self):
        self.base_url = "http://git.znana.top:4000"
    
    # 异步请求
    async def get_info(self,info:dict,url:str):
        async with httpx.AsyncClient()as cli:
            try:
                res = await cli.get(url=url)
                return info,res
            except:
                logger.error(format_exc())
                return info,None
    # 歌曲照片保存
    def save_img(self,pic_name:str,url:str) -> str:
        img_path = path.join(getcwd(),"data","album_img",pic_name+".jpeg")
        if path.exists(img_path):
            return img_path
        res = get(url=url)
        with open(img_path,"wb")as f:
            f.write(res.content)
        return img_path
    # 歌曲歌词保存
    def save_lyric(self,lrc_name:str,netease_id:str) -> str:
        lrc_path = path.join(getcwd(),"data","lrcs",lrc_name+".lrc")
        lyric_url = self.base_url+f"/lyric/new?id={netease_id}"
        res = get(lyric_url).json()
        lrc = res.get("lrc").get("lyric")
        with open(lrc_path,"w",encoding="utf-8")as f:
            f.write(lrc)
        logger.warning(lrc_name+"  歌词写入")
        return lrc_path
    
    # 获取歌手图片url
    def get_artist_img_url(self,artist_id:str) -> str:
        url = f"https://music.163.com/artist?id={artist_id}"
        headers = {
            "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        }
        res = get(url=url,headers=headers)
        html = Selector(res.text)
        img_path = html.xpath('//*[@class="n-artist f-cb"]/img/@src')
        img_url = img_path.extract_first()
        return img_url
    # 匹配歌曲基础信息
    def search_song_info(self,info_list:list):
        sql_con = Sqlite_con()
        # 根据歌曲名称，歌曲专辑匹配歌曲信息
        def match_music_info_by_title_album(info:dict,res:dict):
            try:
                mid = info.get("id")
                album_id = info.get("album_id")
                title = info.get("title")
                album = str(info.get("album")).lower()
                arname = str(info.get("artist_name")).lower()
                pic_url = None
                for n in res.get("result").get("songs"):
                    name = n.get("name")
                    ar_name = n.get("ar")[0].get("name").lower()
                    ar_netease_id = n.get("ar")[0].get("id")
                    if title != name:
                        continue
                    al = n.get("al")
                    alname = al.get("name").lower()
                    al_netease_id = al.get("id")
                    if ar_name not in arname and alname not in album:
                        continue
                    pic_url = al.get("picUrl")
                    publish_time = int(n.get("publishTime"))/1000
                    publish_time_str = datetime.fromtimestamp(publish_time).strftime("%Y-%m-%d %H:%M:%S")
                    netease_id = n.get("id")
                    break
                if pic_url:
                    artist_id = md5(ar_name.encode()).hexdigest()
                    img_path = self.save_img(album_id,pic_url)
                    lrc_path = self.save_lyric(mid,netease_id=netease_id)
                    artist_img_url = self.get_artist_img_url(artist_id=ar_netease_id)
                    self.save_img(artist_id,artist_img_url)
                    curdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    full_text = ar_name+"  "+album
                    # 更新媒体，歌手，专辑表
                    media_sql = f'update media_file set netease_id="{netease_id}",artist="{ar_name}",artist_id="{artist_id}",album_artist="{ar_name}",album_artist_id="{artist_id}",order_album_artist_name="{ar_name}",order_artist_name="{ar_name}",image_path="{img_path}",lyrics="{lrc_path}",updated_at="{curdate}" where id="{mid}";'
                    album_sql = f'update album set artist_id="{artist_id}",netease_id="{al_netease_id}",album_artist="{ar_name}",album_artist_id="{artist_id}",order_album_artist_name="{ar_name}",all_artist_ids="{artist_id}" where id="{album_id}";'
                    artist_sql = f'insert or ignore into artist(id,netease_id,name,full_text,order_artist_name) values("{artist_id}","{ar_netease_id}","{ar_name}","{full_text}","{ar_name}");'
                    sql_con.sql2commit(artist_sql)
                    sql_con.sql2commit(album_sql)
                    sql_con.sql2commit(media_sql)
                else:
                    logger.warning(mid+"  "+title+" not match")
            except:
                logger.error(format_exc())
        # 根据歌曲名称，歌曲作者匹配歌曲信息
        def match_music_info_by_title_artist(info:dict,res:dict):
            try:
                mid = info.get("id")
                artist_id = info.get("artist_id")
                title = info.get("title")
                arname = str(info.get("artist_name")).lower()
                pic_url = None
                for n in res.get("result").get("songs"):
                    name = n.get("name")
                    ar_name = n.get("ar")[0].get("name").lower()
                    ar_netease_id = n.get("ar")[0].get("id")
                    if title != name:
                        continue
                    al = n.get("al")
                    alname = al.get("name").lower()
                    al_netease_id = al.get("id")
                    if ar_name not in arname:
                        continue
                    pic_url = al.get("picUrl")
                    publish_time = int(n.get("publishTime"))/1000
                    publish_time_str = datetime.fromtimestamp(publish_time).strftime("%Y-%m-%d %H:%M:%S")
                    netease_id = n.get("id")
                    break
                if pic_url:
                    album_id = md5(alname.encode()).hexdigest()
                    img_path = self.save_img(album_id,pic_url)
                    artist_img_url = self.get_artist_img_url(artist_id=ar_netease_id)
                    self.save_img(artist_id,artist_img_url)
                    lrc_path = self.save_lyric(mid,netease_id=netease_id)
                    curdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    full_text = ar_name+"  "+album
                    # 更新媒体，歌手，专辑表
                    media_sql = f'update media_file set netease_id="{netease_id}",album="{alname}",album_id="{album_id}",order_album_name="{alname}",image_path="{img_path}",lyrics="{lrc_path}",updated_at="{curdate}" where id="{mid}";'
                    album_sql = f'insert or ignore into album(id,netease_id,name,artist_id,artist,album_artist,updated_at,full_text,order_album_name,order_album_artist_name,all_artist_ids,external_info_updated_at) values("{album_id}","{al_netease_id}","{alname}","{artist_id}","{ar_name}","{ar_name}","{curdate}","{full_text}","{alname}","{ar_name}","{artist_id}","{curdate}");'
                    artist_sql = f'update artist set netease_id="{ar_netease_id}" where id="{artist_id}";'
                    sql_con.sql2commit(album_sql)
                    sql_con.sql2commit(media_sql)
                    sql_con.sql2commit(artist_sql)
                else:
                    logger.warning(mid+"  "+title+" not match")
            except:
                logger.error(format_exc())
        while info_list:
            info_list_cp = info_list.copy()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = []
            for i in info_list_cp[:50]:
                info_list.remove(i)
                title = i.get("title")
                album = i.get("album").replace("none","")
                artist = i.get("artist").replace("none","")
                url = self.base_url + f"/cloudsearch?keywords={title} {album} {artist}&offset=0&limit=100"
                tasks.append(asyncio.ensure_future(self.get_info(info=i,url=url)))
            loop.run_until_complete(asyncio.wait(tasks))
            for r in tasks:
                info,res = r.result()
                try:
                    match_music_info_by_title_album(info=info,res=res.json())
                    match_music_info_by_title_artist(info=info,res=res.json())
                except:
                    logger.error(format_exc())
    # 歌曲信息回放至文件
    def info_back2file(self):
        # mp3信息回存
        def mp3_info_save(path_f:str,album_id:str,mid:str,title:str,album:str,artist:str):
            info = mp3.MP3(path_f)
            info.clear()
            info.tags.add(id3.TIT2(encoding=3,text=title))
            info.tags.add(id3.TPE1(encoding=3,text=artist))
            info.tags.add(id3.TALB(encoding=3,text=album))
            # 歌词写入
            with open(path.join("data","lrcs",mid+".lrc"),"r",encoding="utf-8")as f:
                lrc = f.read()
            info.tags.add(id3.Frames["USLT"](encoding=id3.Encoding.UTF8,lang="eng",text=lrc))
            # 图片写入
            try:
                with open(path.join(getcwd(),"data","album_img",album_id+".jpeg"),"rb")as f:
                    img_content = f.read()
                info.tags.add(id3.APIC(encoding=id3.Encoding.LATIN1,mime="image/jpeg",type=id3.PictureType.COVER_FRONT,data=img_content))
            except Exception as e:
                logger.error(e)
                pass
            info.save()
        # flac信息回存
        def flac_info_save(path_f:str,album_id:str,mid:str,title:str,album:str,artist:str):
            info = flac.FLAC(path_f)
            info["album"] = album
            info["title"] = title
            info["artist"] = artist
            # 歌词写入
            try:
                with open(path.join(getcwd(),"data","lrcs",mid+".lrc"),"r",encoding="utf-8")as f:
                    lrc = f.read()
                info["lrc"] = lrc
            except Exception as e:
                logger.error(e)
                pass
            # 图片写入 
            try:
                with open(path.join(getcwd(),"data","album_img",album_id+".jpeg"),"rb")as f:
                    img_content = f.read()
                info["image"] = b64encode(img_content).decode("utf-8")
            except Exception as e:
                logger.error(e)
                pass
            info.save()

        sql_con = Sqlite_con()
        get_media_file_sql = f"""select suffix,album,artist,album_id,id,title,path from media_file;"""
        media_file_res = [{
            "suffix":i[0],
            "album":i[1],
            "artist":i[2],
            "album_id":i[3],
            "id":i[4],
            "title":i[5],
            "path":i[6]
        } for i in sql_con.sql2commit(get_media_file_sql)]
        for i in media_file_res:
            suffix = i.get("suffix")
            if suffix == "mp3":
                mp3_info_save(path_f=i["path"],album_id=i["album_id"],mid=i["id"],title=i["title"],album=i["album"],artist=i["artist"])
            elif suffix == "flac":
                flac_info_save(path_f=i["path"],album_id=i["album_id"],mid=i["id"],title=i["title"],album=i["album"],artist=i["artist"])
                
    # 音乐信息刮削，目前支持网易云音乐
    def _completion(self):
        curdate = datetime.now().strftime("%Y-%m-%d")
        logger.add(path.join(getcwd(),"log",f"info_completion_{curdate}.log"))
        logger.info("信息收集开始")
        try:
            sql_con = Sqlite_con()
            get_lack_info_sql = 'select id,album_id,title,artist,album,artist,artist_id from media_file where artist = "none" or lyrics = "None" or image_path = "None" or album = "none";'
            res = sql_con.sql2commit(get_lack_info_sql)
            need_completion_info_list = []
            for i in res:
                need_completion_info_list.append({"id":i[0],"album_id":i[1],"title":i[2],"artist_name":i[3],"album":i[4],"artist":i[5],"artist_id":i[6]})
            self.search_song_info(need_completion_info_list)
            calculation_table_info()
            # 信息回放至文件
            self.info_back2file()
        except:
            logger.error(format_exc())
        logger.success("信息收集结束")
    # 定时启动刮削系统
    def regular_start_completion(self):
        def start_fun():
            while True:
                curtime = datetime.now().strftime("%H:%M")
                if curtime == "01:30":
                    self._completion()
                time.sleep(60)
        p = Thread(target=start_fun)
        p.setDaemon(True)
        p.start()
    # 手动启动刮削功能
    def start_completion(self):
        try:
            p = Thread(target=self._completion)
            p.setDaemon(True)
            p.start()
            return INFO_COMPLETION_SUCCESS
        except:
            logger.error(format_exc())
            return INFO_COMPLETION_FAILED
        
    
if __name__ == "__main__":
    info_com = InfoCompletion()
    info_com._completion()