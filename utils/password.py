from random import choice
from loguru import logger
from hashlib import sha256

class Password:
    def __init__(self):
        self.salt_str_list = ['~', '`', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', '+', '=', '|', '\\', '{', '[', '}', ']', "'", '"', ',', '.', '<', '>', '?', '/', ':', ';', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    def pass_hash(self,password:str,salt_nums:int=16) -> str:
        salts = password
        for i in range(salt_nums):
            salts += choice(self.salt_str_list)
        salt_str = sha256(salts.encode()).hexdigest()
        salt = salt_str[:salt_nums]
        passwd_encrypt = sha256((password+salt).encode()).hexdigest()
        return f"$sha${salt_nums}${salt}{passwd_encrypt}"

    def check_pass(self,password:str,pass_hash:str) -> bool:
        try:
            pass_str = pass_hash.split("$")
            salt_num = int(pass_str[2])
            pass_str_hash = pass_str[-1]
            salt = pass_str_hash[:salt_num]
            hash_pass_code = pass_str_hash[salt_num:]
            hash_pass = sha256((password+salt).encode()).hexdigest()
            if hash_pass == hash_pass_code:
                return True
            return False
        except Exception as e:
            logger.warning(e)
            return False



if __name__ == '__main__':
    pa = Password()
    res = pa.pass_hash("laolin")
    print(res)
    res1 = pa.check_pass("laolin",res)
    print(res1)
