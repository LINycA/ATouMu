from datetime import datetime
from os import getcwd,path,listdir,mkdir
from traceback import format_exc

from shortuuid import uuid
from loguru import logger
from uuid import uuid4

from middlewars import SqliteInit
from utils import Sqlite_con,YamlConfig,Password


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
    def sys_init(self,user_conf:dict) -> bool:
        """
        初始化系统数据库
        :param conf: 数据库配置信息
        :param user_conf: 用户配置信息
        :return:
        """
        try:
            conf_dict = self.yaml_conf.load_yaml
            self._gen_jwt_secret_key()
            conf_dict.update({
                "sys_init":True,
                "db":path.join(getcwd(),"db","ATouMu.db")
            })
            try:
                # 初始化sqlite数据库
                self.yaml_conf.safe_dump_conf(conf_dict)
                sqlite_inti = SqliteInit()
                sqlite_inti.db_init()
                try:
                    # sqlite初始化管理员信息
                    sqlite_con = Sqlite_con()
                    user_sql = self._adminuserInit(user_conf)
                    res = sqlite_con.sql2commit(user_sql)
                except Exception as e:
                    logger.error(e)
                    return False
            except Exception as e:
                # 初始化失败则回退
                conf_dict["sys_init"] = False
                self.yaml_conf.safe_dump_conf(conf_dict)
                logger.error(format_exc())
                return False
            return True
        except:
            logger.error(format_exc())
            return False
