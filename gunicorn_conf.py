import multiprocessing

#并行工作进程数
workers = multiprocessing.cpu_count() * 2 + 1
# workers = 4

#指定每个工作者的线程数，当使用gevent时,这个不起作用
threads = 4

# 控制是否在主进程中预加载应用程序。当设置为 True 时，Gunicorn 在主进程中加载应用程序，然后将其复制到每个工作进程中。当设置为 False 时，应用程序在每个工作进程中独立加载
preload_app = False

#端口 5000
bind = '127.0.0.1:8200'

#设置守护进程,将进程交给supervisor管理
daemon = 'true'

#工作模式协程,使用gevent模式（协程模式），默认的是sync模式,共有sync、eventlet、gevent、tornado
worker_class = 'gevent' 

# 最大的并发请求数为　　workers*2000
worker_connections = 2000

# 最大客户端并发数量，默认情况下这个值为1000。此设置将影响gevent和eventlet工作模式，当最大请求数量达到时进程会重启
max_requests = 1000  

#设置进程文件目录
pidfile = '/var/run/gunicorn.pid'

#进程名
proc_name = 'gunicorn_process'

#设置访问日志和错误信息日志路径
accesslog = "./Log/access.log"
errorlog = "./Log/error.log"
# 当想关闭日志时可以设置
# accesslog = '/dev/null'  # 禁用日志
# errorlog = '/dev/null'  # 禁用日志

# 日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置，
loglevel = "error"

  #- debug: 最详细的日志级别，通常用于调试目的。
  #- info（默认值）: 提供一般的信息日志，适用于大多数情况。
  #- warning: 输出警告级别的日志消息，表示可能存在潜在问题。
  #- error: 输出错误级别的日志消息，表示发生了一些错误，但 Gunicorn 可以继续运行。
  #- critical: 输出严重错误级别的日志消息，表示发生了严重问题，Gunicorn 无法继续运行。

# 设置gunicorn访问日志格式，错误日志无法设置
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'  

# INT：默认情况下，这个值为30，在超时(从接收到重启信号开始)之后仍然活着的工作将被强行杀死；一般使用默认
graceful_timeout = 60

# int：未决连接的最大数量，即等待服务的客户的数量。默认2048个，一般不修改；
backlog = 2048

# 超过这么多秒后工作将被杀掉，并重新启动。一般设定为30秒；
timeout = 300

# INT：在keep-alive连接上等待请求的秒数，默认情况下值为2。一般设定在1~5秒之间。
keepalive = 5 

# reload = True  # 默认为False。此设置用于开发，每当应用程序发生更改时，都会导致工作重新启动。

# 设置这个值为true 才会把打印信息记录到错误日志里,将stdout / stderr重定向到errorlog中的指定文件
capture_output = False 

# INT：HTTP请求头的行数的最大大小，此参数用于限制HTTP请求行的允许大小，默认情况下，这个值为4094。值是0~8190的数字
limit_request_line = 5120

# 限制HTTP请求中请求头字段的数量。此字段用于限制请求头字段的数量以防止DDOS攻击，与limit-request-field-size一起使用可以提高安全性。默认情况下，这个值为100，这个值不能超过32768
limit_request_fields = 101

# 限制HTTP请求中请求头的大小，默认情况下这个值为8190。值是一个整数或者0，当该值为0时，表示将对请求头大小不做限制
limit_request_field_size = 0

# 设置gunicorn使用的python虚拟环境
# pythonpath='/home/your_path/venv/bin/python3'
# 环境变量
# raw_env = 'APE_API_ENV=DEV'
