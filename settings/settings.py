from traceback import format_exc
from os import path

from flask import Response
from utils import trans_res
from loguru import logger
from const import *

from utils import YamlConfig
from middlewars import Email

class Settings:
    def __init__(self):
        self.yaml_conf = YamlConfig()
        self.email = Email()
    # 获取配置内容
    def get_settings_info(self) -> Response:
        return trans_res({"ret":200,"data":self.yaml_conf.load_yaml})
    # 用户注册设置，是否允许注册，注册是否需要认证
    def register_allow(self,registe_allow:bool,email_conf:dict,registe_auth:bool) -> Response:
        keys = ["server","port","username","password"]
        for key in keys:
            if key not in email_conf:
                logger.error("email conf error")
                return EMAIL_ERROR
            elif email_conf.get(key) is None or email_conf.get(key) == "":
                logger.error("email conf error")
                return EMAIL_ERROR
        self.email.conf_email(email_conf.get("server"),port=email_conf.get("port"),username=email_conf.get("username"),password=email_conf.get("password"))
        if type(registe_allow) is not bool or type(registe_auth) is not bool:
            logger.error("registe conf error")
            return REGIST_ERROR
        conf_yaml = self.yaml_conf.load_yaml
        conf_yaml.update({
            "settings":{
                "registe_allow":registe_allow,
                "registe_auth":registe_auth
                }
            })
        try:
            self.yaml_conf.safe_dump_conf(conf_yaml)
            return SETTING_SUCCESS
        except:
            logger.error(format_exc())
            return SETTING_ERROR
    # 设置媒体文件扫描路径
    def scan_path(self,scan_path:str) -> Response:
        if path.exists(scan_path):
            if path.isdir(scan_path):
                return SCAN_PATH_ERROR
            else:
                yaml_conf = self.yaml_conf.load_yaml
                yaml_conf.update({"media_path":scan_path})
                self.yaml_conf.safe_dump_conf(yaml_conf)
                return SETTING_SUCCESS
        return SCAN_PATH_ERROR
    # 测试邮件配置是否可用
    def email_conf_test(self) -> Response:
        return self.email.send_email_test()