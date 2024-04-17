# Naja Atra ASGI

This ia a ASGI proxy that proxies requests to Naja Atra.

# Usage

Take `uvicorn` as an example.

```python
import uvicorn
from naja_atra import route
from naja_atra_asgi import app

@route("/hello")
def hello(name: str):
    return {"messag": f"Hello, {name}!"}

if __name__ == '__main__':
    uvicon_conf = uvicorn.Config(
        app, host="0.0.0.0", port=9090, log_level="info")
    asgi_server = uvicorn.Server(uvicon_conf)
    asgi_server.run()
```

You can use `server.scan()` to import routes from other modules. And also you can use `naja_atra_asgi.config()` to function to sepecify the static resources routes.

```python
import os
import uvicorn
import naja_atra.server as server

from naja_atra import route
from naja_atra_asgi import config, app

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    server.scan(base_dir="tests/ctrls", regx=r'.*controllers.*',
                project_dir=PROJECT_ROOT)
    config(
        resources={"/public/*": f"{PROJECT_ROOT}/tests/static",
                   "/*": f"{PROJECT_ROOT}/tests/static"})
    uvicon_conf = uvicorn.Config(
        app, host="0.0.0.0", port=9090, log_level="info")
    asgi_server = uvicorn.Server(uvicon_conf)
    asgi_server.run()
```

## Legacy Applications

You can use the legacy ASGI (V2) application function `app_v2` if your server does not support ASGI V3.