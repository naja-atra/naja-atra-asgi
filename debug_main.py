# -*- coding: utf-8 -*-
#
# If you want to run this file, please install following package to run.
# python3 -m pip install werkzeug 'uvicorn[standard]'
#

from naja_atra import request_map
import naja_atra.server as server
import os
import signal
import asyncio

import uvicorn
from threading import Thread
from naja_atra.utils.logger import get_logger, set_level
from naja_atra_asgi import ASGIProxy
from naja_atra_asgi import config, app, app_v2

set_level("DEBUG")


_logger = get_logger("http_test")
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

asgi_server: uvicorn.Server = None

proxy: ASGIProxy = None
init_asgi_proxy_lock: asyncio.Lock = asyncio.Lock()


def start_server_uvicorn():
    server.scan(base_dir="tests/ctrls", regx=r'.*controllers.*',
                project_dir=PROJECT_ROOT)
    config(
        resources={"/public/*": f"{PROJECT_ROOT}/tests/static",
                   "/*": f"{PROJECT_ROOT}/tests/static"})
    uvicon_conf = uvicorn.Config(
        app, host="0.0.0.0", port=9090, log_level="info")
    global asgi_server
    asgi_server = uvicorn.Server(uvicon_conf)
    asgi_server.run()


@request_map("/stop")
async def stop():
    global asgi_server
    await asgi_server.shutdown()
    asgi_server = None
    return "<!DOCTYPE html><html><head><title>关闭</title></head><body>关闭成功！</body></html>"


def shutdown():
    global asgi_server
    if asgi_server:
        _logger.info("Shutdown the wsgi server...")
        asyncio.run(asgi_server.shutdown())
        asgi_server = None


def on_sig_term(signum, frame):
    if asgi_server:
        _logger.info(f"Receive signal [{signum}], shutdown the wsgi server...")
        Thread(target=shutdown).start()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, on_sig_term)
    signal.signal(signal.SIGINT, on_sig_term)
    start_server_uvicorn()
