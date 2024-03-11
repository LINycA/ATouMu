

from loguru import logger

from utils import Sqlite_con

# 计算数值
def calculation_table_info():
    sql_con = Sqlite_con()
    # 清除无用数据
    logger.info("计算开始")
    delete_artist_sql = f"""delete from artist where id not in (select distinct artist_id from media_file);"""
    delete_album_sql = f"""delete from album where id not in (select distinct album_id from media_file);"""
    sql_con.sql2commit(delete_artist_sql)
    sql_con.sql2commit(delete_album_sql)
    album_ids_sql = "select id from album;"
    album_ids = [i[0] for i in sql_con.sql2commit(album_ids_sql)]
    for aid in album_ids:
        try:
            album_song_count_update = f"""update album set
            song_count=(select count(1) from media_file where album_id="{aid}"),
            duration=(select sum(duration) from media_file where album_id="{aid}"),
            size=(select sum(size) from media_file where album_id="{aid}")
            where id="{aid}";
            """
            sql_con.sql2commit(album_song_count_update)
        except Exception as e:
            logger.warning(aid)
            logger.error(e)
    artist_ids_sql = "select id from artist;"
    artist_ids = [i[0] for i in sql_con.sql2commit(artist_ids_sql)]
    for aid in artist_ids:
        try:
            artist_count_update_sql = f"""update artist set
            album_count=(select count(1) from album where artist_id="{aid}"),
            song_count=(select count(1) from media_file where artist_id="{aid}"),
            size=(select sum(size) from media_file where artist_id="{aid}")
            where id="{aid}";
            """
            sql_con.sql2commit(artist_count_update_sql)
        except Exception as e:
            logger.warning(aid)
            logger.error(e)
    logger.success("计算结束")