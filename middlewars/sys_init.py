from datetime import datetime
from os import getcwd,path,listdir,mkdir
from traceback import format_exc

from shortuuid import uuid
from loguru import logger
from uuid import uuid4

from middlewars import SqliteInit,MysqlInit
from utils import Sqlite_con,MysqlCon,YamlConfig,Password


class SysInit:
    def __init__(self):
        self.yaml_conf = YamlConfig()
    # 生成jwt密钥
    def _gen_jwt_secret_key(self) -> str:
        secret_key = uuid4()
        yaml_conf = self.yaml_conf.load_yaml
        yaml_conf.update({"jwt_secret_key":str(secret_key)})
        self.yaml_conf.safe_dump_conf(yaml_conf)
    # 初始化管理员
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
    # 系统初始化
    def sys_init(self,conf:dict,user_conf:dict) -> bool:
        """
        初始化系统数据库
        :param conf: 数据库配置信息
        :param user_conf: 用户配置信息
        :return:
        """
        try:
            conf_dict = self.yaml_conf.load_yaml
            self._gen_jwt_secret_key()
            using_db = conf.get("using_db")
            media_path = conf.get("media_path") if conf.get("media_path") else getcwd()
            conf_dict.update({
                "sys_init":True,
                "using_db":using_db,
                "media_path":media_path,
                "db":{using_db:{}}
            })
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
                    res = sqlite_con.sql2commit(user_sql)
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
                    mysql_con.sql2commit(user_sql)
                except Exception as e:
                    logger.error(e)
                return True
            else:
                return False
        except:
            logger.error(format_exc())
            return False
