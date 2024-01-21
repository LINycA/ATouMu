from utils import YamlConfig
from loguru import logger
from middlewars import SqliteInit,MysqlInit
from traceback import format_exc

class SysInit:
    def __init__(self):
        self.yaml_conf = YamlConfig()

    def _user_init(self):
        ...
    def sys_init(self,conf:dict):
        try:
            using_db = conf.get("using_db")
            conf_dict = {
                "sys_init":True,
                "using_db":using_db,
                "db":{using_db:{}}
            }
            if using_db == "sqlite":
                try:
                    conf_dict.get("db").get(using_db).update({
                        "path":conf.get("db").get("path")
                    })
                    self.yaml_conf.safe_dump_conf(conf_dict)
                    sqlite_inti = SqliteInit()
                    sqlite_inti.db_init()
                except Exception as e:
                    conf_dict["sys_init"] = False
                    self.yaml_conf.safe_dump_conf(conf_dict)
                    logger.error(e)
                    return False
                return True
            elif using_db == "mysql":
                conf_dict.get("db").get(using_db).update({
                    "host": conf.get("host"),
                    "port": conf.get("port"),
                    "user": conf.get("user"),
                    "password": conf.get("password"),
                    "database": conf.get("database")
                })
                self.yaml_conf.safe_dump_conf(conf_dict)
                try:
                    mysql_init = MysqlInit()
                    mysql_init.createdatabase(conf_dict.get("db").get(using_db).get("database"))
                    mysql_init.init_tables()
                except Exception as e:
                    logger.error(str(e))
                    conf_dict["sys_init"] = False
                    self.yaml_conf.safe_dump_conf(conf_dict)
                    return False
                return True
            else:
                return False
        except:
            logger.error(format_exc())
            return False
