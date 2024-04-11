

from typing import Dict

from naja_atra import HttpSessionFactory, AppConf
from naja_atra import get_app_conf, set_session_factory
from naja_atra import ModelBindingConf
from naja_atra.http_servers.routing_server import RoutingServer
from naja_atra.request_handlers.http_session_local_impl import LocalSessionFactory
from .asgi_request_handler import ASGIRequestHandler

version = "1.0.1"


class ASGIProxy(RoutingServer):

    def __init__(self, res_conf, model_binding_conf: ModelBindingConf = ModelBindingConf()):
        super().__init__(res_conf=res_conf, model_binding_conf=model_binding_conf)

    async def app_proxy(self, scope, receive, send):
        request_handler = ASGIRequestHandler(self, scope, receive, send)
        await request_handler.handle_request()


def __fill_proxy(proxy: RoutingServer, session_factory: HttpSessionFactory, app_conf: AppConf):
    appconf = app_conf or get_app_conf()
    set_session_factory(
        session_factory or appconf.session_factory or LocalSessionFactory())
    filters = appconf._get_filters()
    # filter configuration
    for ft in filters:
        proxy.map_filter(ft)

    request_mappings = appconf._get_request_mappings()
    # request mapping
    for ctr in request_mappings:
        proxy.map_controller(ctr)

    ws_handlers = appconf._get_websocket_handlers()

    for hander in ws_handlers:
        proxy.map_websocket_handler(hander)

    err_pages = appconf._get_error_pages()
    for code, func in err_pages.items():
        proxy.map_error_page(code, func)


def new_asgi_proxy(resources: Dict[str, str] = {}, session_factory: HttpSessionFactory = None, app_conf: AppConf = None) -> ASGIProxy:
    appconf = app_conf or get_app_conf()
    proxy = ASGIProxy(res_conf=resources,
                      model_binding_conf=appconf.model_binding_conf)
    __fill_proxy(proxy, session_factory, appconf)
    return proxy


_proxy: ASGIProxy = None


def config(resources: Dict[str, str] = {}, session_factory: HttpSessionFactory = None, app_conf: AppConf = None):
    global _proxy
    _proxy = new_asgi_proxy(resources, session_factory, app_conf)


async def app(scope, receive, send):
    global _proxy
    if _proxy is None:
        _proxy = new_asgi_proxy()
    await _proxy.app_proxy(scope, receive, send)


def app_v2(scope):
    async def app_instance(receive, send):
        await app(scope, receive, send)
    return app_instance
