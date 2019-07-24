from .route import Route
from ..__version__ import (__version__, __title__)


class Version(Route):
    route = '/v1/version'

    def on_get(self, req, resp):
        resp.media = f'{__title__}-{__version__}'
