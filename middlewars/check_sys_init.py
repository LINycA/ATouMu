from loguru import logger
from utils import YamlConfig
from utils import trans_res

def check_sys_init(func,*wargs,**kwargs):
    yaml_conf = YamlConfig()
    if yaml_conf.check_sys_init():
        def wrapper(*wargs, **kwargs):
            result = func(*wargs, **kwargs)
            return result
        return wrapper
    else:
        def wrapper(*wargs,**kwargs):
            logger.error("配置文件未初始化")
            result = {"ret":302,"msg":"配置文件未初始化"}
            return trans_res(result)
        return wrapper


@check_sys_init
def test():
    print("yes")
if __name__ == '__main__':
    print(test())