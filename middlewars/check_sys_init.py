from utils import YamlConfig
from utils import trans_res
import functools
from const import *


def check_sys_init():
    yaml_conf = YamlConfig()
    if not yaml_conf.check_sys_init():
        return SYSINIT_ERROR
    else:
        return False


def check_sys_init_wrap(func):
    @functools.wraps(func)
    def check_wraps(*args,**kwargs):
        yaml_conf = YamlConfig()
        if yaml_conf.check_sys_init():
            res = func(*args,**kwargs)
            return res
        else:
            return trans_res(SYSINIT_ERROR)
    return check_wraps


if __name__ == '__main__':
    res = check_sys_init()
    print(res)
