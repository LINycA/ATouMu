from flask import Response

from const import *


class Keepalive:
    def keepalive(self) -> Response:
        return KEEPALIVE