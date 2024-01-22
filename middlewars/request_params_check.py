from const import *
from pymysql import Connect
from os import path
from loguru import logger


def sys_init_params_check(data: dict) -> (bool,dict):
    """
    检测系统初始化参数是否正确
    :param data:字典，json
    :return:返回bool,配置字典,用户信息字典
    """
    if "using_db" not in data or "db" not in data or "user" not in data:
        return False, PARAMS_ERROR,None
    else:
        try:
            user_dict = data.get("user")
            key_list = ["user_name","nick_name","password","email"]
            for i in key_list:
                if i not in user_dict:
                    return False,PARAMS_ERROR,None
                elif user_dict[i] is None or user_dict[i] == "":
                    return False,PARAMS_ERROR,None
        except Exception as e:
            logger.error(e)
            return False,PARAMS_ERROR,None
        if data.get("using_db") == "sqlite":
            try:
                db_fields = ["path"]
                for i in data.get("db"):
                    if i not in db_fields:
                        return False, PARAMS_ERROR, None
                    elif data.get("db").get(i) is None or data.get("db").get(i) == "":
                        return False, PARAMS_ERROR, None
                dir_path = "/".join(data.get("db").get("path").split("/")[:-1])
                if not path.exists(dir_path):
                    return False, PARAMS_ERROR, None
            except Exception as e:
                logger.error(str(e))
                return False,PARAMS_ERROR,None
            return True, data, user_dict
        elif data.get("using_db") == "mysql":
            try:
                db_fields = ["host","port","user","password","database"]
                for i in data.get("db"):
                    if i not in db_fields:
                        return False,PARAMS_ERROR,None
                    elif data.get("db").get(i) is None or data.get("db").get(i) == "":
                        return False, PARAMS_ERROR, None
            except Exception as e:
                logger.error(e)
                return False,PARAMS_ERROR,None
            try:
                con = Connect(host=data.get("db").get("host"), port=int(data.get("db").get("port")), user=data.get("db").get("user"), password=data.get("db").get("password"), database="mysql")
                with con.cursor() as cur:
                    cur.execute("show tables")
                con.close()
            except Exception as e:
                logger.error(ConnectionError("sys_init mysql Connect Error."))
                return False, PARAMS_ERROR,None
            return True, data, user_dict
        return False, PARAMS_ERROR,None