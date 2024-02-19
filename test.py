import re

a = "a123sdf@asdf.gmail"

if b := re.findall(r"\s",a):
    print(b)