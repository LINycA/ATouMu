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
        self.verify_code = VerifyCode()
    # 消息构建
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
    # 邮件发送功能
    def email_send_fun(self,send_to:str,message:MIMEMultipart):
        email_conf = YamlConfig().email_conf()
        server = smtplib.SMTP(email_conf.get("server"),int(email_conf.get("port")))
        server.starttls()
        server.login(email_conf.get("username"),email_conf.get("password"))
        server.sendmail(email_conf.get("username"),send_to,message.as_string())
        server.quit()
    # 邮件发送功能
    def send_email(self,send_to:str,nickname:str):
        email_conf = YamlConfig().email_conf()
        try:
            code = self.verify_code.generate_code(send_to)
            if not code:
                return EMAIL_VERIFY_CODE_ERROR
            message = self._message(email_conf.get("username"),send_to=send_to,nickname=nickname,code=code)
            self.email_send_fun(send_to=send_to,message=message)
            return EMAIL_VERIFY_CODE_SUCCESS
        except:
            logger.error(format_exc())
            return EMAIL_VERIFY_CODE_ERROR
    # 测试邮件配置是否正确
    def send_email_test(self):
        email_conf = YamlConfig().email_conf()
        try:
            email = email_conf.get("username")
            msg = MIMEMultipart()
            msg["From"] = email
            msg["To"] = email
            msg["Subject"] = "ATouMu音乐测试邮件"
            msg.attach(MIMEText("这是一封测试邮件，邮箱配置可用，⚠️请勿回复邮件","plain","utf-8"))
            self.email_send_fun(send_to=email,message=msg)
            return EMAIL_SEND_SUCCESS
        except:
            logger.error(format_exc())
            return EMAIL_SEND_ERROR

    # 邮件配置功能
    def conf_email(self,server:str,port:int,username:str,password:str):
        yaml_conf = YamlConfig()
        conf_dict = yaml_conf.load_yaml
        conf_dict.update({"email":{
            "server":server,
            "port":port,
            "username":username,
            "password":password
        }})
        try:
            yaml_conf.safe_dump_conf(conf_dict)
        except:
            logger.error(format_exc())

if __name__ == '__main__':
    e = Email()
    # print(e.send_email("1002941793@qq.com","hello laolin").data.decode("utf-8"))
    e.conf_email("smtp.qq.com",587,"1002941793@qq.com","fdnjyltkwsrybbdf")