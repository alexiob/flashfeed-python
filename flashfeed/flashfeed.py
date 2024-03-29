import falcon
import json
import logging
import sys
import uuid

from apscheduler.schedulers.background import BackgroundScheduler

from .crawlers import CRAWLERS
from .routes import ROUTES


class FlashFeed(object):
    BASE_ROUTE = '/v1/api/alexa/flashfeed'

    def __init__(self, config_path):
        self._setup_logger()
        self._load_config(config_path)

        news_outlets_config_path = self._config.get('crawler').get('news_outlets_config_path')
        self._load_news_outlets_config(news_outlets_config_path)

    def _setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
        )
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        self._logger = logger

    def _load_config(self, config_path):
        with open(config_path) as config_file:
            self._config = json.load(config_file)

    def _load_news_outlets_config(self, news_outlets_config_path):
        with open(news_outlets_config_path) as news_outlets_config_file:
            news_outlets = json.load(news_outlets_config_file)

        for news_outlet in news_outlets:
            for news_source in news_outlet.get('news_sources', []):
                news_source['id'] = str(uuid.uuid4())
                news_source['news_outlet'] = news_outlet

        self._news_outlets = news_outlets
        self._news_entities = {}

    def start(self):
        self._start_scheduler()
        self._start_server()
        self.crawl()


    def _start_scheduler(self):
        scheduler = BackgroundScheduler()
        scheduler.start()
        scheduler.add_job(
            self.crawl,
            'interval',
            seconds=self._config.get('crawler', {}).get('every_seconds', 60*60)
        )

    def _start_server(self):
        self._server = falcon.API(media_type=falcon.MEDIA_JSON)

        for route_resource in ROUTES:
            route = route_resource.route
            resource = route_resource(self._logger)

            self._logger.info(
                f'adding route "{route}" with resource {resource}')
            self._server.add_route(route, resource)

        for news_outlet in self._news_outlets:
            for news_source in news_outlet.get('news_sources', []):
                if news_source.get('enabled', False):
                    crawler = CRAWLERS[news_source['crawler']]

                    for entity_name, entity_route in news_source.get('entities', {}).items():
                        route = self.BASE_ROUTE + '/' + entity_route.strip('/')

                        resource = crawler.resource(
                            self._logger,
                            news_source,
                            self._news_entities,
                            entity_name
                        )

                        self._logger.info(
                            f'adding route "{route}" with resource {resource}')
                        self._server.add_route(route, resource)

    def crawl(self):
        for news_outlet in self._news_outlets:
            for news_source in news_outlet.get('news_sources', []):
                if news_source.get('enabled', False):
                    crawler = CRAWLERS[news_source['crawler']]
                    crawler.fetch(self._logger, news_source,
                                  self._news_entities)

    @staticmethod
    def run():
        flashfeed = FlashFeed('./config/default.json')
        flashfeed.start()

        return flashfeed._server
