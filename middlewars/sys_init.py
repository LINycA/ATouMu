from utils import YamlConfig
from loguru import logger
from datetime import datetime
from shortuuid import uuid
from uuid import uuid4
from utils import Password
from middlewars import SqliteInit,MysqlInit
from os import getcwd,path
from utils import Sqlite_con,MysqlCon
from traceback import format_exc

class SysInit:
    def __init__(self):
        self.yaml_conf = YamlConfig()

    def _gen_jwt_secret_key(self) -> str:
        secret_key = uuid4()
        sql = f"insert into property(name,value) values(\"secret_key\",\"{secret_key}\");"
        return sql

    def _adminuserInit(self,userconf:dict) -> str:
        id = uuid()
        create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pa = Password()
        pass_ = pa.pass_hash(userconf.get("password"))
        nick_name = userconf.get("nick_name")
        user_name = userconf.get("user_name")
        email = userconf.get("email")
        sql = f'insert into users(user_id,nick_name,user_name,email,password,admin,create_time) values("{id}","{nick_name}","{user_name}","{email}","{pass_}",1,"{create_time}");'
        return sql

    def sys_init(self,conf:dict,user_conf:dict) -> bool:
        """
        初始化系统数据库
        :param conf: 数据库配置信息
        :param user_conf: 用户配置信息
        :return:
        """
        try:
            using_db = conf.get("using_db")
            conf_dict = {
                "sys_init":True,
                "using_db":using_db,
                "db":{using_db:{}}
            }
            if using_db == "sqlite":
                try:
                    # 初始化sqlite数据库
                    conf_dict.get("db").get(using_db).update({
                        "path":path.join(getcwd(),"db","ATouMu.db")
                    })
                    self.yaml_conf.safe_dump_conf(conf_dict)
                    sqlite_inti = SqliteInit()
                    sqlite_inti.db_init()
                except Exception as e:
                    # 初始化失败则回退
                    conf_dict["sys_init"] = False
                    self.yaml_conf.safe_dump_conf(conf_dict)
                    logger.error(e)
                    return False
                try:
                    # sqlite初始化管理员信息
                    sqlite_con = Sqlite_con()
                    user_sql = self._adminuserInit(user_conf)
                    secret_key_sql = self._gen_jwt_secret_key()
                    res = sqlite_con.sql2commit(user_sql)
                    sqlite_con.sql2commit(secret_key_sql)
                except Exception as e:
                    logger.error(e)
                    return False
                return True
            elif using_db == "mysql":
                # 初始化mysql数据库
                conf_dict.get("db").get(using_db).update({
                    "host": conf.get("db").get(using_db).get("host"),
                    "port": conf.get("db").get(using_db).get("port"),
                    "user": conf.get("db").get(using_db).get("user"),
                    "password": conf.get("db").get(using_db).get("password"),
                    "database": conf.get("db").get(using_db).get("database")
                })
                self.yaml_conf.safe_dump_conf(conf_dict)
                try:
                    # 测试数据库连接
                    mysql_init = MysqlInit()
                    mysql_init.createdatabase(conf_dict.get("db").get(using_db).get("database"))
                    mysql_init.init_tables()
                except Exception as e:
                    # 数据库连接失败则回退
                    logger.error(str(format_exc()))
                    conf_dict["sys_init"] = False
                    self.yaml_conf.safe_dump_conf(conf_dict)
                    return False
                try:
                    # mysql初始化管理员信息
                    mysql_con = MysqlCon()
                    user_sql = self._adminuserInit(user_conf)
                    secret_key_sql = self._gen_jwt_secret_key()
                    mysql_con.sql2commit(user_sql)
                    mysql_con.sql2commit(secret_key_sql)
                except Exception as e:
                    logger.error(e)
                return True
            else:
                return False
        except:
            logger.error(format_exc())
            return False
