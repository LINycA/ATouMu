from utils import YamlConfig
from loguru import logger
from middlewars import SqliteInit
from traceback import format_exc

class SysInit:
    def __init__(self):
        self.yaml_conf = YamlConfig()

    def _user_init(self):
        ...
    def sys_init(self,use_db:str,**conf:dict):
        try:
            conf_dict = {
                "sys_init":True,
                "using_db":use_db,
                "db":{use_db:{}}
            }
            if use_db == "sqlite":
                conf_dict.get("db").get(use_db).update({
                    "path":conf.get("path")
                })
                self.yaml_conf.safe_dump_conf(conf_dict)
                sqlite_inti = SqliteInit()
                sqlite_inti.db_init()
            elif use_db == "mysql":
                conf_dict.get("db").get(use_db).update({
                    "host":conf.get("host"),
                    "port":conf.get("port"),
                    "user":conf.get("user"),
                    "password":conf.get("password"),
                    "database":conf.get("database")
                })
                self.yaml_conf.safe_dump_conf(conf_dict)
            else:
                return False
        except:
            logger.error(format_exc())