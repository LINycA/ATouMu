import re


username = "-? 12!@#@%^&(*%*)\\|/.,.<>:;'asd_f123"

res = re.findall(r"\W",username)
print(res)