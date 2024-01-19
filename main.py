import json

from flask import Flask,request,jsonify,Response
from middlewars import check_sys_init
from utils import trans_res
import jwt


app = Flask(__name__)

@app.route("/")
@check_sys_init
def index():
    res = {"ret":200,"msg":"测试一下"}
    return trans_res(res)




if __name__ == '__main__':
    app.run(port=8819)