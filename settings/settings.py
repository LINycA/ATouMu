from traceback import format_exc

from flask import Response
from loguru import logger
from const import *

from utils import YamlConfig,Email

class Settings:
    def __init__(self):
        self.yaml_conf = YamlConfig()
        self.email = Email()

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