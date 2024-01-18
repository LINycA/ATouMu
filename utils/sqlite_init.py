from middlewars import Sqllite_con

def db_init():
    con = Sqllite_con()

    # 用户信息表
    con.sql2dict("drop table if exists users;")
    user_table_sql = """
    create table users(
    user_id varchar(255) not null,
    nick_name varchar(255) not null,
    user_name varchar(255) not null,
    email varchar(255) not null,
    password varchar(255) not null,
    gender varchar(255) default null,
    phone varchar(255) default null,
    create_time datetime not null,
    last_login_time datetime default null,
    last_login_ip varchar(255) default null,
    admin bool default false not null,
    primary key (user_id),
    unique(email,user_name));
    """
    con.sql2dict(user_table_sql)

    # 用户会话表，管理用户cookie，或token
    con.sql2dict("drop table if exists player;")
    player_table_sql = """
    create table player(
    id varchar(255) not null,
    name varchar(255) not null,
    user_agent varchar,
    user_name varchar(255) not null,
    ip_address varchar default null,
    last_seen timestamp,
    cookie varchar(255) not null,
    expire_time datetime not null,
    primary key (id));
    """
    con.sql2dict(player_table_sql)

    # 专辑信息表
    con.sql2dict("drop table if exists album;")
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
    con.sql2dict(album_table_sql)

    # 艺术家信息表
    con.sql2dict("drop table if exists artist;")
    artist_table_sql = """
    create table artist(
    id varchar(255) not null,
    name varchar(255) not null,
    gender varchar(3) default "0" not null,
    primary key(id));
    """
    con.sql2dict(artist_table_sql)

    # 艺术家风格信息表
    con.sql2dict("drop table if exists artist_genre;")
    artist_genre_table_sql = """
    create table artist_genre(
    artist_id varchar(255) not null,
    genre_id varchar(255) not null);
    """
    con.sql2dict(artist_genre_table_sql)

    # 风格信息表
    con.sql2dict("drop table if exists genre;")
    genre_table_sql = """
    create table genre(
    id varchar(255) not null,
    name varchar(255) not null,
    primary key(id));
    """
    con.sql2dict(genre_table_sql)

    # 歌曲信息表
    con.sql2dict("drop table if exists media;")
    medis_table_sql = """
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
    con.sql2dict(medis_table_sql)

    # 歌曲风格表
    con.sql2dict("drop table if exists media_genre;")
    media_genre_table_sql = """
    create table media_genre(
    media_id varchar(255) not null,
    genre_id varchar(255) not null);
    """
    con.sql2dict(media_genre_table_sql)

    # 歌单基础信息
    con.sql2dict("drop table if exists playlist;")
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
    con.sql2dict(playlist_table_sql)

    # 歌单内容,有哪些歌曲
    con.sql2dict("drop table if exists playlist_track")
    playlist_track_table_sql = """
    create table playlist_track(
    playlist_id varchar(255) not null,
    medis_id varchar(255) not null);
    """
    con.sql2dict(playlist_track_table_sql)

    # 固有字段
    con.sql2dict("drop table if exists property;")
    property_table_sql = """
    create table property(
    name varchar(255),
    value varchar(255),
    primary key(name));
    """
    con.sql2dict(property_table_sql)



if __name__ == '__main__':
    db_init()