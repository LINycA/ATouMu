import jwt
from utils import MysqlCon
from utils import Sqlite_con
from utils import Password

class Login:
    def __init__(self):
        passwd = Password()

    def login(self,username:str,password:str):
        ...