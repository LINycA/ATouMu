from utils import Sqlite_con


class SqliteInit:
    def __init__(self):
        self.sql_con = Sqlite_con()
    def _create_index(self):
        """
        为所有的表所有字段创建索引
        :return:
        """
        table_name_list = self.sql_con.sql2commit("select name from sqlite_master where type='table';")
        for table in table_name_list:
            table_name = table[0]
            column_list = self.sql_con.sql2commit(f"pragma table_info('{table_name}');")
            column_tuple = tuple([i[1] for i in column_list])
            sql_create_index = f"create index {table_name}_index on {table_name} {str(column_tuple)};"
            self.sql_con.sql2commit(sql_create_index)

    def db_init(self):
        """
        初始化数据库与表
        :return:
        """
        con = self.sql_con

        # 用户信息表
        con.sql2commit("drop table if exists users;")
        user_table_sql = """
        create table users(
        user_id varchar(255) not null,
        nick_name varchar(255) not null,
        user_name varchar(255) not null,
        email varchar(255) not null,
        password varchar(255) not null,
        gender varchar(255) default "其他",
        phone varchar(255) default null,
        create_time datetime not null,
        admin bool default false not null,
        last_login datetime default null,
        primary key (user_id),
        unique(email),
        unique(user_name));
        """
        con.sql2commit(user_table_sql)

        # 用户会话表，管理用户cookie，或token
        con.sql2commit("drop table if exists player;")
        player_table_sql = """
        create table player(
        id varchar(255) not null,
        name varchar(255) not null,
        user_agent varchar,
        user_name varchar(255) not null,
        ip_address varchar default null,
        last_seen timestamp,
        primary key (id));
        """
        con.sql2commit(player_table_sql)

        # 用户注册，邮箱验证码缓存表
        con.sql2commit("drop table if exists verify_code_temp;")
        verify_code_temp_table_sql = """
        create table verify_code_temp(
        email varchar(255) not null,
        code varchar(7) not null,
        expire int(20) not null,
        primary key(email));
        """
        con.sql2commit(verify_code_temp_table_sql)

        # 专辑信息表
        con.sql2commit("drop table if exists album;")
        album_table_sql = """
        create table album(
        id varchar(255) not null,
        name varchar(255) not null,
        artist_id varchar(255) default null,
        duration real default 0 not null,
        genre varchar(255) default null,
        song_count integer default 0 not null,
        full_text text default null,
        release_time date,
        primary key(id));
        """
        con.sql2commit(album_table_sql)

        # 艺术家信息表
        con.sql2commit("drop table if exists artist;")
        artist_table_sql = """
        create table artist(
        id varchar(255) not null,
        name varchar(255) not null,
        gender varchar(3) default "0" not null,
        primary key(id));
        """
        con.sql2commit(artist_table_sql)

        # 艺术家风格信息表
        con.sql2commit("drop table if exists artist_genre;")
        artist_genre_table_sql = """
        create table artist_genre(
        artist_id varchar(255) not null,
        genre_id varchar(255) not null,
        primary key(artist_id,genre_id));
        """
        con.sql2commit(artist_genre_table_sql)

        # 风格信息表
        con.sql2commit("drop table if exists genre;")
        genre_table_sql = """
        create table genre(
        id varchar(255) not null,
        name varchar(255) not null,
        primary key(id));
        """
        con.sql2commit(genre_table_sql)

        # 歌曲信息表
        con.sql2commit("drop table if exists media;")
        media_table_sql = """
        create table media(
        id varchar(255) not null,
        title varchar(255) not null,
        artist_id varchar(255) default "" not null,
        album_id varchar(255) default "" not null,
        genre_id varchar(255) default "" not null,
        media_path text not null,
        lyric_path text default "" not null,
        image_path text default "" not null,
        size integer default 0 not null,
        duration real default 0 not null,
        create_at datetime,
        update_at datetime,
        primary key(id));    
        """
        con.sql2commit(media_table_sql)

        # 歌曲风格表
        con.sql2commit("drop table if exists media_genre;")
        media_genre_table_sql = """
        create table media_genre(
        media_id varchar(255) not null,
        genre_id varchar(255) not null,
        primary key(media_id,genre_id));
        """
        con.sql2commit(media_genre_table_sql)

        # 歌单基础信息
        con.sql2commit("drop table if exists playlist;")
        playlist_table_sql = """
        create table playlist(
        id varchar(255) default null,
        name varchar(255) not null,
        comment text default "" not null,
        owner_id varchar(255) not null,
        public bool default false not null,
        create_time datetime,
        update_time datetime,
        size integer default 0 not null,
        duration real default 0 not null,
        song_count integer default 0 not null,
        primary key(id));
        """
        con.sql2commit(playlist_table_sql)

        # 歌单内容,有哪些歌曲
        con.sql2commit("drop table if exists playlist_track;")
        playlist_track_table_sql = """
        create table playlist_track(
        playlist_id varchar(255) not null,
        media_id varchar(255) not null,
        primary key(playlist_id,media_id));
        """
        con.sql2commit(playlist_track_table_sql)

        # 固有字段
        con.sql2commit("drop table if exists property;")
        property_table_sql = """
        create table property(
        name varchar(255) not null,
        value varchar(255) not null,
        primary key(name));
        """
        con.sql2commit(property_table_sql)

        # 为所有的表，所有字段创建索引
        self._create_index()



if __name__ == '__main__':
    sqlite_init = SqliteInit()
    sqlite_init.db_init()