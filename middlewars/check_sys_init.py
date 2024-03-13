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
