from yaml import safe_load,safe_dump
from os import path,getcwd,mkdir


class YamlConfig:
    def __init__(self):
        config_dir = path.join(getcwd(),"config")
        if not path.exists(config_dir):
            mkdir(config_dir)
        self.config_path = path.join(getcwd(),"config","config.yaml")
        if not path.exists(self.config_path):
            base_conf = {"sys_init":False,"settings":{"registe_allow":True,"registe_auth":False},"scan_regular_time":"00:00","media_path":getcwd()}
            base_conf_yaml = safe_dump(base_conf)
            with open(self.config_path,"w",encoding="utf-8")as f:
                f.write(base_conf_yaml)
        with open(self.config_path,"rb")as f:
            stream = f.read()
        self.load_yaml = safe_load(stream)

    # 检测系统使用的数据库(sqlite or mysql)
    def check_sys_usingdb(self):
        return self.load_yaml.get("using_db")

    # 检测系统是否初始化
    def check_sys_init(self):
        return self.load_yaml.get("sys_init")

    # mysql数据库配置
    def mysql_conf(self):
        return self.load_yaml.get("db").get("mysql")

    # sqlite数据库路径
    def sqlite_conf(self):
        return self.load_yaml.get("db")

    # 配置写入操作
    def safe_dump_conf(self,conf_dict):
        conf_dict = safe_dump(conf_dict)
        with open(self.config_path,"w",encoding="utf-8")as f:
            f.write(conf_dict)

    # 邮件发送配置
    def email_conf(self):
        return self.load_yaml.get("email")

    # 系统设置获取
    def settings_conf(self):
        return self.load_yaml.get("settings")
    
    # 媒体文件夹路径
    def media_path_conf(self) -> str:
        return self.load_yaml.get("media_path")

    # 获取jwt_secret_key
    def jwt_secret_key(self) -> str:
        return self.load_yaml.get("jwt_secret_key")

    # 获取定时扫描世界
    def regular_time(self) -> str:
        return self.load_yaml.get("scan_regular_time")
    



if __name__ == '__main__':
    conf = YamlConfig()
    print(conf.sqlite_conf())

