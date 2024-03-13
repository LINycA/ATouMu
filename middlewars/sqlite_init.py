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
        create_time datetime not null,
        admin bool default false not null,
        last_login datetime default null,
        primary key (user_id),
        unique(email),
        unique(user_name));
        """
        con.sql2commit(user_table_sql)

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
        netease_id varchar(255) default null,
        name varchar(255) not null,
        artist_id varchar(255) default '' not null,
        embed_art_path varchar(255) default '' not null,
        artist varchar(255) default '' not null,
        album_artist varchar(255) default '' not null,
        min_year int default 0 not null,
        max_year integer default 0 not null,
        compilation bool default FALSE not null,
        song_count integer default 0 not null,
        duration real default 0 not null,
        genre varchar(255) default '' not null,
        created_at datetime,
        updated_at datetime,
        full_text text default null,
        album_artist_id varchar(255) default '',
        order_album_name varchar(255) default '',
        order_album_artist_name varchar(255) default '',
        size integer default 0 not null,
        all_artist_ids varchar(255),
        external_info_updated_at datetime default (datetime('now')),
        primary key(id));
        """
        con.sql2commit(album_table_sql)

        # 专辑风格表
        con.sql2commit("drop table if exists album_genres;")
        album_genre_table_sql = """
        create table album_genres(
        album_id varchar not null,
        genre_id varchar not null,
        constraint album_genre_ux unique (album_id,genre_id));
        """
        con.sql2commit(album_genre_table_sql)

        # 注释表（用户收藏歌曲）
        con.sql2commit("drop table if exists annotation;")
        annotation_table_sql = """
        create table annotation(
        ann_id varchar(255) default '' not null,
        user_id varchar(255) default '' not null,
        item_id varchar(255) default '' not null,
        item_type varchar(255) default '' not null,
        play_count integer default 0,
        play_date datetime,
        rating integer default 0,
        starred bool default FALSE not null,
        starred_at datetime,
        unique (user_id,item_id,item_type));
        """
        con.sql2commit(annotation_table_sql)

        # 艺术家信息表
        con.sql2commit("drop table if exists artist;")
        artist_table_sql = """
        create table artist(
        id varchar(255) not null,
        netease_id varchar(255) default null,
        name varchar(255) not null,
        album_count integer default 0 not null,
        full_text varchar(255) default '',
        order_artist_name varchar(255) default '' not null,
        song_count integer default 0 not null,
        size integer default 0 not null,
        external_info_updated_at datetime default (datetime('now')),
        primary key(id));
        """
        con.sql2commit(artist_table_sql)

        # 艺术家风格信息表
        con.sql2commit("drop table if exists artist_genre;")
        artist_genre_table_sql = """
        create table artist_genre(
        artist_id varchar(255) not null,
        genre_id varchar(255) not null,
        constraint artist_genre_ux unique (artist_id,genre_id));
        """
        con.sql2commit(artist_genre_table_sql)

        # 书签表
        con.sql2commit("drop table if exists bookmark;")
        book_mark_table_sql = """
        create table bookmark(
        user_id varchar(255) not null,
        item_id varchar(255) not null,
        item_type varchar(255) not null,
        comment varchar(255),
        position integer,
        changed_by varchar(255),
        created_at datetime,
        updated_at datetime,
        constraint bookmark_pk unique (user_id,item_id,item_type));
        """
        con.sql2commit(book_mark_table_sql)

        # 风格信息表
        con.sql2commit("drop table if exists genre;")
        genre_table_sql = """
        create table genre(
        id varchar(255) not null,
        name varchar(255) not null,
        constraint genre_name_ux unique (name));
        """
        con.sql2commit(genre_table_sql)

        # 歌曲信息表
        con.sql2commit("drop table if exists media_file;")
        media_table_sql = """
        create table media_file(
        id varchar(255) not null,
        netease_id varchar(255) default null,
        path varchar(255) not null,
        title varchar(255) not null,
        album varchar(255) default '' not null,
        artist varchar(255) default '' not null,
        artist_id varchar(255) default "" not null,
        album_artist varchar(255) default '' not null,
        album_id varchar(255) default "" not null,
        has_cover_art bool default FALSE not null,
        track_number integer default 0 not null,
        disc_number integer default 0 not null,
        year integer default 0 not null,
        size integer default 0 not null,
        suffix varchar(255) default '' not null,
        duration real default 0 not null,
        bit_rate integer default 0 not null,
        genre varchar(255) default '' not null,
        compilation bool default FALSE not null,
        created_at datetime,
        updated_at datetime,
        lyric_path text default "" not null,
        image_path text default "" not null,
        full_text varchar(255) default '',album_artist_id varchar(255) default '', order_album_name varchar(255) collate nocase,
        order_album_artist_name varchar(255) collate nocase,
        order_artist_name varchar(255) collate nocase, 
        sort_album_name varchar(255) collate nocase, 
        sort_artist_name varchar(255) collate nocase, 
        sort_album_artist_name varchar(255) collate nocase, 
        sort_title varchar(255) collate nocase, disc_subtitle varchar(255), 
        mbz_track_id varchar(255), mbz_album_id varchar(255), 
        mbz_artist_id varchar(255), mbz_album_artist_id varchar(255), 
        mbz_album_type varchar(255), mbz_album_comment varchar(255), 
        catalog_num varchar(255), comment varchar, lyrics varchar, bpm integer, channels integer,
        order_title varchar null collate NOCASE, 
        mbz_release_track_id varchar(255), rg_album_gain real, 
        rg_album_peak real, rg_track_gain real, rg_track_peak real,
        primary key(id),
        unique(path));
        """
        con.sql2commit(media_table_sql)

        # 歌曲风格表
        con.sql2commit("drop table if exists media_file_genres;")
        media_genre_table_sql = """
        create table media_file_genres(
        media_file_id varchar(255) not null,
        genre_id varchar(255) not null,
        constraint media_file_genre_ux unique (media_file_id,genre_id));
        """
        con.sql2commit(media_genre_table_sql)

         # 用户会话表，用户客户端日志
        con.sql2commit("drop table if exists player;")
        player_table_sql = """
        create table player(
        id varchar(255) not null,
        name varchar(255) not null,
        user_agent varchar,
        user_name varchar(255) not null,
        client varchar not null,
        ip_address varchar,
        last_seen timestamp,
        max_bit_rate int default 0,
        transcoding_id varchar,
        report_real_path bool default FALSE not null,
        primary key (id));
        """
        con.sql2commit(player_table_sql)

        # 歌单基础信息
        con.sql2commit("drop table if exists playlist;")
        playlist_table_sql = """
        create table playlist(
        id varchar(255) not null,
        name varchar(255) not null,
        comment text default "" not null,
        duration real default 0 not null,
        song_count integer default 0 not null,
        public bool default false not null,
        created_time datetime,
        updated_time datetime,
        path string default '' not null,
        sync bool default false not null,
        size integer default 0 not null,
        rules varchar,
        evaluated_at datetime,
        owner_id varchar(255) not null,
        primary key(id));
        """
        con.sql2commit(playlist_table_sql)

        # 歌单文件表(好像没用)
        con.sql2commit("drop table if exists playlist_fields;")
        playlist_fields_table_sql = """
        create table playlist_fields(
        field varchar(255) not null,
        playlist_id varchar(255) not null);
        """
        con.sql2commit(playlist_fields_table_sql)

        # 歌单内容,有哪些歌曲
        con.sql2commit("drop table if exists playlist_track;")
        playlist_track_table_sql = """
        create table playlist_track(
        id integer default 0 not null,
        playlist_id varchar(255) not null,
        media_file_id varchar(255) not null,
        constraint playlist_tracks_pos unique(playlist_id,id));
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