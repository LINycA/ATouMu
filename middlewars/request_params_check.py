from const import *
from pymysql import Connect
from loguru import logger


def sys_init_params_check(data: dict) -> (bool,dict):
    """
    检测系统初始化参数是否正确
    :param data:字典，json
    :return:返回配置字典
    """
    if "using_db" not in data or "db" not in data or "user" not in data:
        return False, PARAMS_ERROR
    else:
        try:
            user_dict = data.get("user")
            key_list = ["username","nickname","password","email"]
            for i in key_list:
                if i not in user_dict:
                    return False,PARAMS_ERROR
        except Exception as e:
            logger.error(e)
            return False,PARAMS_ERROR
        if data.get("using_db") == "sqlite":
            try:
                sqlite_conf = {"using_db":"sqlite","db": {"path":data.get("db").get("path")}}
                if sqlite_conf.get("db").get("path") is None or sqlite_conf.get("db").get("path") == "" or ".db" not in sqlite_conf.get("db").get("path"):
                    return False, PARAMS_ERROR
            except Exception as e:
                logger.error(str(e))
                return False,PARAMS_ERROR
            return True, sqlite_conf, user_dict
        elif data.get("using_db") == "mysql":
            try:
                host, port, user, password, database = data.get("db").get("host"), int(data.get("db").get("port")), data.get("db").get("user"), data.get("db").get(
                    "password"), data.get("db").get("database")
                mysql_conf = {
                    "using_db":"mysql",
                    "host": host,
                    "port": port,
                    "user": user,
                    "password": password,
                    "database": database
                }
            except Exception as e:
                logger.error(e)
                return False,PARAMS_ERROR
            try:
                con = Connect(host=host, port=port, user=user, password=password, database="mysql")
                with con.cursor() as cur:
                    cur.execute("show tables")
                con.close()
            except Exception as e:
                logger.error(ConnectionError("sys_init mysql Connect Error."))
                return False, PARAMS_ERROR
            return True, mysql_conf, user_dict
        return False, PARAMS_ERROR


