import functools
from os import getcwd,path
from datetime import datetime

from flask import request
from loguru import logger

from utils import YamlConfig
from const import *


def check_sys_init():
    yaml_conf = YamlConfig()
    if not yaml_conf.check_sys_init():
        return SYSINIT_ERROR
    else:
        return False

# 打印访问地址（来访）
def log_request_info(func):
    @functools.wraps(func)
    def log_wraps(*args,**kwargs):
        curdate = datetime.now().strftime("%Y-%m-%d")
        logger.add(path.join(getcwd(),"log","route_"+curdate+".log"))
        info = f"""
        {request.headers.get("X-Forwarded-For")}  ------>  {request.path}
        访问域名  ------>  {request.headers.get("Host")}
        访问地址  ------>  {request.full_path}
        访问方式  ------>  {request.method}
        """
        logger.info(info)
        return func(*args,**kwargs)
    return log_wraps

# 检测系统是否初始化
def check_sys_init_wrap(func):
    @functools.wraps(func)
    def check_wraps(*args,**kwargs):
        yaml_conf = YamlConfig()
        if yaml_conf.check_sys_init():
            res = func(*args,**kwargs)
            return res
        else:
            return SYSINIT_ERROR
    return check_wraps


if __name__ == '__main__':
    res = check_sys_init()
    print(res)
