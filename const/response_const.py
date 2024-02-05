from utils import trans_res

PARAMS_ERROR = trans_res({"ret": 306, "msg": "参数错误"})

MYSQL_ERROR = trans_res({"ret": 306, "msg": "mysql连接错误"})
SQLITE_ERROR = trans_res({"ret": 306, "msg": "sqlite存储路径错误"})

SYSINIT_ERROR = trans_res({"ret": 101, "msg": "配置文件未初始化"})
SYSINIT_SUCCESS = trans_res({"ret": 200, "msg": "配置文件初始化完成"})
SYSINIT_FAILED = trans_res({"ret": 102, "msg": "配置文件初始化失败"})
SYSINIT_INITED = trans_res({"ret": 201, "msg": "配置文件已初始化"})

USERINFO_ERROR = trans_res({"ret": 306, "msg": "用户信息错误"})
USERADD_SUCCESS = trans_res({"ret": 200, "msg": "用户增加成功"})
USERADD_FAILED = trans_res({"ret": 201, "msg": "用户增加成功"})
USERDEL_SUCCESS = trans_res({"ret": 200, "msg": "用户删除成功"})
USERDEL_FAILED = trans_res({"ret": 201, "msg": "用户删除失败"})
USERMODIFY_FAILED = trans_res({"ret": 201, "msg": "用户修改失败"})
USERMODIFY_SUCCESS = trans_res({"ret": 200, "msg": "用户修改成功"})
USERQUERY_ERROR = trans_res({"ret":201,"msg":"用户查询错误"})