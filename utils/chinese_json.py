from flask import Response
import json

def trans_res(res:dict):
    return Response(json.dumps(res,ensure_ascii=False),mimetype="application/json; charset=UTF-8")