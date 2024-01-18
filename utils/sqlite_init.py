from middlewars import Sqllite_con

def db_init():
    user_table_sql = """
    create table users(
    user_id TEXT not null,
    nick_name TEXT not null,
    user_name TEXT not null,
    email TEXT not null,
    password TEXT not null,
    gender TEXT default null,
    phone TEXT default null,
    create_time TEXT not null,
    last_login_time TEXT default null,
    last_login_ip TEXT default null,
    primary key (user_id),
    unique(email,user_name));
    """
    album_table_sql = """
    id varchar(255) not null,
    name varchar(255) not null,
    artist_id 
    """
    con = Sqllite_con()
    con.sql2dict(user_table_sql)

if __name__ == '__main__':
    db_init()