from utils import MysqlCon


class MysqlInit:
    def __init__(self):
        self.mysql_con = MysqlCon(mode="")

    def _create_database(self):
        """
        初始化数据库
        :return:
        """
        mysql_con = MysqlCon(mode="init")
        sql = "create database ATouMu;"
        mysql_con.sql2commit(sql)

    def _init_tables(self):
        # 用户信息表
        self.mysql_con.sql2commit("drop table if exists users;")
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
            primary key(user_id) using BTREE,
            unique(email),
            unique(user_name),
            index user_pass (password),
            index user_email (email),
            index index_uname (user_name));
        """
        self.mysql_con.sql2commit(users_table_sql)

        # 用户会话表
        self.mysql_con.sql2commit("drop table if exists player;")
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