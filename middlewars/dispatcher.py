from const import *
from pymysql import Connect
from os import path,getcwd,mkdir
from users import User
from loguru import logger
from middlewars import SysInit
from flask import Response


class RequestParamsCheck:
    # 数据库初始化操作
    def sys_init_params(self,data: dict) -> Response:
        """
        检测系统初始化参数是否正确
        :param data:字典，json
        :return:返回bool,配置字典,用户信息字典
        """
        if "using_db" not in data or "user" not in data:
            return PARAMS_ERROR
        else:
            try:
                sysinit = SysInit()
                user_dict = data.get("user")
                using_db_list = ["sqlite","mysql"]
                # 判断指定使用的的数据库是否允许
                if data.get("using_db") not in using_db_list:
                    return PARAMS_ERROR
                # 判断用户信息字段是否匹配
                key_list = ["user_name", "nick_name", "password", "email"]
                for i in key_list:
                    if i not in user_dict:
                        return PARAMS_ERROR
                    elif user_dict[i] is None or user_dict[i] == "":
                        return PARAMS_ERROR
            except Exception as e:
                logger.error(e)
                return PARAMS_ERROR
            if data.get("using_db") == "sqlite":
                if not path.exists(path.join(getcwd(),"db")):
                    mkdir(path.join(getcwd(),"db"))
            elif data.get("using_db") == "mysql":
                try:
                    db_fields = ["host", "port", "user", "password", "database"]
                    for i in data.get("db").get("mysql"):
                        if i not in db_fields:
                            return PARAMS_ERROR
                        elif data.get("db").get("mysql").get(i) is None or data.get("db").get("mysql").get(i) == "":
                            return PARAMS_ERROR
                except Exception as e:
                    logger.error(e)
                    return PARAMS_ERROR
                try:
                    con = Connect(host=data.get("db").get("mysql").get("host"), port=int(data.get("db").get("mysql").get("port")),
                                user=data.get("db").get("mysql").get("user"), password=data.get("db").get("mysql").get("password"),
                                database="mysql")
                    with con.cursor() as cur:
                        cur.execute("show tables")
                    con.close()
                except Exception as e:
                    logger.error(ConnectionError("sys_init mysql Connect Error."))
                    return MYSQL_ERROR
            # 初始化数据库表
            init_bool = sysinit.sys_init(data,user_dict)
            if init_bool:
                return SYSINIT_SUCCESS
            else:
                return SYSINIT_FAILED
    
    # 用户操作分发
    def user_params(self,data: dict) -> Response:
        if "action" not in data or "user" not in data:
            return PARAMS_ERROR
        action = data.get("action")
        action_keys = ["add","delete","query","modify"]
        if action not in action_keys:
            return PARAMS_ERROR        
        
        user = User()
        # 用户增加操作
        if action == "add":
            user_info_dict = data.get("user")
            user_keys = ["user_name","nick_name","email","password","gender","phone","admin"]
            for key in user_keys:
                if key not in user_info_dict:
                    return PARAMS_ERROR
            return user.user_add(username=user_info_dict.get("user_name"),nickname=user_info_dict.get("nick_name"),
                          password=user_info_dict.get("password"),email=user_info_dict.get("email"),
                          phone=user_info_dict.get("phone"),gender=user_info_dict.get("gender"),
                          admin=user_info_dict.get("admin"))
        # 用户删除操作
        elif action == "delete":
            user_info_dict = data.get("user")
            if "user_id" not in user_info_dict:
                return USERINFO_ERROR
            return user.user_del(user_info_dict.get("user_id"))
    