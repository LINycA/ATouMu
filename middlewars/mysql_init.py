from utils import MysqlCon


class MysqlInit:
    def createdatabase(self,database:str):
        """
        初始化数据库
        :return:
        """
        mysql_con = MysqlCon(mode="init")
        sql = f"create database {database};"
        mysql_con.sql2commit(sql)

    def init_user(self):
        mysql_con = MysqlCon()
        mysql_con.sql2commit("insert into users()")

    def init_tables(self):
        # 用户信息表
        mysql_con = MysqlCon()
        mysql_con.sql2commit("drop table if exists users;")
        users_table_sql = """
            create table users(
            user_id varchar(255) not null comment"用户id,uuid",
            nick_name varchar(255) not null comment"用户昵称",
            user_name varchar(255) not null comment"用户名",
            email varchar(255) not null comment"邮箱",
            password varchar(255) not null comment"用户密码",
            gender varchar(255) default null comment"用户性别，不一定用",
            phone varchar(255) default null comment"用户手机号",
            create_time datetime not null comment"用户创建时间",
            admin bool default false not null comment"是否管理员",
            last_login datetime default null comment"账号最后一次登陆时间",
            primary key(user_id) using BTREE,
            unique(email),
            unique(user_name),
            index user_pass (password),
            index user_email (email),
            index index_uname (user_name));
        """
        mysql_con.sql2commit(users_table_sql)

        # 用户注册验证码缓存表
        mysql_con.sql2commit("drop table if exists verify_code_temp;")
        verify_code_temp_table = """
        create table verify_code_temp(
        email varchar(255) not null comment "用户邮箱",
        code varchar(7) not nul comment "验证码",
        expire int(20) not null comment "验证码过期时间戳",
        primary key(email) using BTREE);
        """
        mysql_con.sql2commit(verify_code_temp_table)

        # 用户会话表
        mysql_con.sql2commit("drop table if exists player;")
        player_table_sql = """
        create table player(
        id varchar(255) not null comment"会话id",
        name varchar(255) not null comment"会话名称",
        user_agent longtext default null comment"用户浏览器头",
        user_name varchar(255) not null comment"用户名",
        ip_address varchar(255) default null comment"会话ip地址",
        last_seen datetime comment"上次浏览时间",
        primary key (id) using btree,
        index player_id (id),
        index player_name (name),
        index player_agent (user_agent(255)),
        index player_user (user_name),
        index player_ip_address (ip_address));
        """
        mysql_con.sql2commit(player_table_sql)

        # 专辑信息表
        mysql_con.sql2commit("drop table if exists album;")
        album_table_sql = """
        create table album(
        id varchar(255) not null comment "专辑id",
        name varchar(255) not null comment "专辑名称",
        artist_id varchar(255) default null comment "艺术家id",
        duration real default 0 not null comment"持续时间",
        genre varchar(255) default null comment "专辑风格",
        song_count integer default 0 not null comment "歌曲数量",
        full_text text default null comment "专辑描述",
        release_time date comment"发行时间",
        primary key(id) using btree,
        index album_id (id),
        index album_name (name),
        index album_artist_id (artist_id),
        index album_genre (genre),
        index album_release_time (release_time));
        """
        mysql_con.sql2commit(album_table_sql)

        # 艺术家信息表
        mysql_con.sql2commit("drop table if exists artist;")
        artist_table_sql = """
        create table artist(
        id varchar(255) not null comment "艺术家id",
        name varchar(255) not null comment "艺术家名称",
        gender varchar(3) default "其他" comment "艺术家性别",
        primary key(id) using btree,
        index artist_name (name),
        index artist_gender (gender));
        """
        mysql_con.sql2commit(artist_table_sql)

        # 艺术家风格信息表
        mysql_con.sql2commit("drop table if exists artist_genre;")
        artist_genre_table_sql = """
        create table artist_genre(
        artist_id varchar(255) not null comment"艺术家id",
        genre_id varchar(255) not null comment "风格id",
        primary key(artist_id,genre_id));
        """
        mysql_con.sql2commit(artist_genre_table_sql)

        # 风格信息表
        mysql_con.sql2commit("drop table if exists genre;")
        genre_table_sql = """
        create table genre(
        id varchar(255) not null comment "风格id",
        name varchar(255) not null comment "风格名称",
        primary key(id),
        index genre_name(name));
        """
        mysql_con.sql2commit(genre_table_sql)

        # 歌曲信息表
        mysql_con.sql2commit("drop table if exists media;")
        media_table_sql = """
        create table media(
        id varchar(255) not null comment"歌曲文件id,文件的sha256值",
        title varchar(255) not null comment"歌曲名称",
        artist_id varchar(255) default "" not null comment "艺术家id",
        album_id varchar(255) default "" not null comment"专辑id",
        genre_id varchar(255) default "" not null comment"歌曲风格",
        media_path text not null comment"音乐文件路径",
        lyric_path text default null comment"歌词文件路径",
        image_path text default null comment"图片文件路径",
        size integer default 0 not null comment"文件大小",
        duration real default 0 not null comment"歌曲时长",
        create_at datetime comment"数据创建时间",
        update_at datetime comment"数据更新时间",
        primary key(id),
        index me_title (title),
        index me_aid (artist_id),
        index me_albid (album_id),
        index me_genre (genre_id),
        index me_mepath (media_path(255)),
        index me_lypath (lyric_path(255)),
        index me_imgpath (image_path(255)));
        """
        mysql_con.sql2commit(media_table_sql)

        # 歌曲风格表
        mysql_con.sql2commit("drop table if exists media_genre;")
        media_genre_table_sql = """
        create table media_genre(
        media_id varchar(255) not null comment "歌曲id",
        genre_id varchar(255) not null comment "风格id",
        index meid (media_id),
        index genid (genre_id));
        """
        mysql_con.sql2commit(media_genre_table_sql)

        # 歌单基础信息表
        mysql_con.sql2commit("drop table if exists playlists;")
        playlist_table_sql = """
        create table playlist(
        id varchar(255) not null comment "歌单id",
        name varchar(255) not null comment "歌单名称",
        comment text default null comment "歌单描述",
        owner_id varchar(255) not null comment "歌单拥有者，用户id",
        public bool default false not null comment "歌单是否公开",
        create_time datetime comment "歌单创建时间",
        update_time datetime comment "歌单更新时间",
        size integer default 0 comment "歌单歌曲总数据",
        duration real default 0 comment "歌单总时长",
        song_count integer default 0 comment "歌曲数量",
        primary key(id),
        index pl_name (name),
        index pl_owid (owner_id),
        index pl_public (public));
        """
        mysql_con.sql2commit(playlist_table_sql)

        # 歌单内容
        mysql_con.sql2commit("drop table if exists playlist_track;")
        playlist_track_table_sql = """
        create table playlist_track(
        playlist_id varchar(255) not null comment"歌单id",
        media_id varchar(255) not null comment"歌曲id",
        primary key(playlist_id,media_id)) ;
        """
        mysql_con.sql2commit(playlist_track_table_sql)

        # 固有字段表
        mysql_con.sql2commit("drop table if exists property;")
        property_table_sql = """
        create table property(
        name varchar(255) not null comment "固定配置名称",
        value varchar(255) not null comment "固定配置值",
        primary key(name),
        index pro_va (value));
        """
        mysql_con.sql2commit(property_table_sql)