from yaml import safe_load,safe_dump
from os import path,getcwd


class YamlConfig:
    def __init__(self):
        self.config_path = path.join(getcwd(),"config","config.yaml")
        if not path.exists(self.config_path):
            base_conf = {"sys_init":False}
            base_conf_yaml = safe_dump(base_conf)
            with open(self.config_path,"w",encoding="utf-8")as f:
                f.write(base_conf_yaml)
        with open(self.config_path,"rb")as f:
            stream = f.read()
        self.load_yaml = safe_load(stream)

    def check_sys_usingdb(self):
        return self.load_yaml.get("using_db")

    def check_sys_init(self):
        return self.load_yaml.get("sys_init")

    def mysql_conf(self):
        return self.load_yaml.get("db").get("mysql")

    def sqlite_conf(self):
        return self.load_yaml.get("db").get("sqlite")

    def safe_dump_conf(self,conf_dict):
        conf_dict = safe_dump(conf_dict)
        with open(self.config_path,"w",encoding="utf-8")as f:
            f.write(conf_dict)


if __name__ == '__main__':
    conf = YamlConfig()
    print(conf.sqlite_conf())

