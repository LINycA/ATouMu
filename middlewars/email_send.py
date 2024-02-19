import smtplib
from os import path,getcwd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from traceback import format_exc

from loguru import logger

from middlewars import VerifyCode
from utils import YamlConfig
from const import *


class Email:
    def __init__(self):
        self.yaml_conf = YamlConfig()
        self.verify_code = VerifyCode()
        self.email_conf = self.yaml_conf.email_conf()

    def _message(self,from_email:str,send_to:str,nickname:str,code:str):
        # 构建邮件内容
        subject = "ATouMu音乐注册验证码"
        with open(path.join(getcwd(),"template","email_template.html"),"r",encoding="utf-8")as f:
            message = f.read().replace("nickname",nickname).replace("code",code)
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = send_to
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "html","utf-8"))
        return msg

    def send_email(self,send_to:str,nickname:str):
        try:
            code = self.verify_code.generate_code(send_to)
            if not code:
                return EMAIL_VERIFY_CODE_ERROR
            message = self._message(self.email_conf.get("username"),send_to=send_to,nickname=nickname,code=code)
            server = smtplib.SMTP(self.email_conf.get("server"),int(self.email_conf.get("port")))
            server.starttls()
            server.login(self.email_conf.get("username"),self.email_conf.get("password"))
            server.sendmail(self.email_conf.get("username"),send_to,message.as_string())
            server.quit()
            return EMAIL_VERIFY_CODE_SUCCESS
        except:
            logger.error(format_exc())
            return EMAIL_VERIFY_CODE_ERROR

    def conf_email(self,server:str,port:int,username:str,password:str):
        conf_dict = self.yaml_conf.load_yaml
        print(conf_dict)
        conf_dict.update({"email":{
            "server":server,
            "port":port,
            "username":username,
            "password":password
        }})
        try:
            self.yaml_conf.safe_dump_conf(conf_dict)
        except:
            logger.error(format_exc())

if __name__ == '__main__':
    e = Email()
    # print(e.send_email("1002941793@qq.com","hello laolin").data.decode("utf-8"))
    e.conf_email("smtp.qq.com",587,"1002941793@qq.com","fdnjyltkwsrybbdf")