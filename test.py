import time
from loguru import logger
from traceback import format_exc

def retry_req(wait:float=1):
    def retry_req_wraps(func):
        def wraps(*wargs,**kwargs):
            while True:
                try:
                    res = func(*wargs,**kwargs)
                    return res
                except:
                    logger.error(format_exc())
                    time.sleep(wait)
                    continue
        return wraps
    return retry_req_wraps


# @retry_req(3)
def test(i):
    return i / 0 

res = retry_req(3)
res(test)(1)