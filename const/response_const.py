from utils import trans_res

# 统一参数错误
PARAMS_ERROR = trans_res({"ret": 306, "msg": "参数错误"})
# 数据库连接错误
MYSQL_ERROR = trans_res({"ret": 306, "msg": "mysql连接错误"})
SQLITE_ERROR = trans_res({"ret": 306, "msg": "sqlite存储路径错误"})
# 系统初始化
SYSINIT_ERROR = trans_res({"ret": 101, "msg": "配置文件未初始化"})
SYSINIT_SUCCESS = trans_res({"ret": 200, "msg": "配置文件初始化完成"})
SYSINIT_FAILED = trans_res({"ret": 102, "msg": "配置文件初始化失败"})
SYSINIT_INITED = trans_res({"ret": 201, "msg": "配置文件已初始化"})
# 账号口令
TOKEN_EXPIRE = trans_res({"ret": 201,"msg": "登陆过期，请重新登陆"})
TOKEN_ERROR = trans_res({"ret":201,"msg":"错误的token"})
LOGIN_ERROR = trans_res({"ret":201,"msg":"用户名或密码错误"})
PERMISSION_ERROR = trans_res({"ret":203,"msg":"没有权限"})
# 用户
USERINFO_ERROR = trans_res({"ret": 306, "msg": "用户信息错误"})
USERADD_SUCCESS = trans_res({"ret": 200, "msg": "用户增加成功"})
USER_EXISTS = trans_res({"ret":201,"msg":"用户已存在"})
USER_UNEXISTS = trans_res({"ret":201,"msg":"用户不存在"})
USERADD_FAILED = trans_res({"ret": 201, "msg": "用户增加失败"})
USERDEL_SUCCESS = trans_res({"ret": 200, "msg": "用户删除成功"})
USERDEL_FAILED = trans_res({"ret": 201, "msg": "用户删除失败"})
USERMODIFY_FAILED = trans_res({"ret": 201, "msg": "用户修改失败"})
USERMODIFY_SUCCESS = trans_res({"ret": 200, "msg": "用户修改成功"})
USERQUERY_ERROR = trans_res({"ret":201,"msg":"用户查询错误"})