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
        self.email = Email()
    # 获取配置内容
    def get_settings_info(self) -> Response:
        yaml_conf = YamlConfig()
        return trans_res({"ret":200,"data":yaml_conf.load_yaml})
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
        yaml_conf = YamlConfig()
        if type(registe_allow) is not bool or type(registe_auth) is not bool:
            logger.error("registe conf error")
            return REGIST_ERROR
        conf_yaml = yaml_conf.load_yaml
        conf_yaml.update({
            "settings":{
                "registe_allow":registe_allow,
                "registe_auth":registe_auth
                }
            })
        try:
            yaml_conf.safe_dump_conf(conf_yaml)
            return SETTING_SUCCESS
        except:
            logger.error(format_exc())
            return SETTING_ERROR
    # 设置媒体文件扫描路径
    def scan_path(self,scan_path:str) -> Response:
        yaml_conf = YamlConfig()
        if path.exists(scan_path):
            if path.isdir(scan_path):
                return SCAN_PATH_ERROR
            else:
                conf = yaml_conf.load_yaml
                conf.update({"media_path":scan_path})
                yaml_conf.safe_dump_conf(yaml_conf)
                return SETTING_SUCCESS
        return SCAN_PATH_ERROR
    # 测试邮件配置是否可用
    def email_conf_test(self) -> Response:
        return self.email.send_email_test()