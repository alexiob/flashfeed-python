import requests
import uuid
import pprint

class Resource(object):
    crawler = None
    logger = None
    news_entities = None
    news_outlet_name = None
    news_source_name = None
    country = None
    region = None

    def on_get(self, req, resp):
        resp.media = self.crawler.feed(
            self.logger,
            self.news_entities,
            self.news_outlet_name,
            self.news_source_name,
            self.country,
            self.region
        )


class Crawler(object):
    NAME = 'crawler'

    @staticmethod
    def fetch(logger, news_source, news_entities):
        raise NotImplementedError()

    @staticmethod
    def resource(logger, news_source, news_entities):
        class_name = f'{__class__.NAME}_{news_source["name"]}_{news_source["country"]}_{news_source["region"]}'
        resource = type(class_name, (Resource, ), dict(
            crawler=__class__,
            logger=logger,
            news_entities=news_entities,
            news_outlet_name=news_source['news_outlet']['name'],
            news_source_name=news_source['name'],
            country=news_source['country'],
            region=news_source['region']
        ))()

        return resource

    @staticmethod
    def feed(logger, news_entities, news_outlet_name, news_source_name, country, region):
        feed = []

        for news_entity in news_entities.values():
            if news_entity['news_source']['name'] != news_source_name or \
                news_entity['news_source']['news_outlet']['name'] != news_outlet_name:
                continue

            title_text = f'{news_entity["news_source"]["name"].upper()} {news_entity["title"]}'.replace(
                '_', ' ')
            main_text = ''
            update_date = news_entity['updated_at'].strftime(
                '%Y-%m-%dT%H:%M:%S') + 'Z'

            feed_entry = {
                'uid': news_entity['uuid'],
                'updateDate': update_date,
                'titleText': title_text,
                'mainText': main_text,
                'streamUrl': news_entity['url'],
                'redirectionUrl': news_entity['news_source']['url']
            }

            feed.append(feed_entry)

        return feed

    # PRIVATE

    @staticmethod
    def _request_get(url):
        return requests.get(url)

    @staticmethod
    def _get_media_type(data):
        media_type = 'unknown'
        data = data.lower()

        if 'video' in data:
            media_type = 'video'
        elif 'audio' in data:
            media_type = 'audio'

        return media_type

    @staticmethod
    def _to_https(url):
        if url.startswith('http://'):
            url = 'https://' + url.lstrip('http://')
        return url

    @staticmethod
    def _uuid():
        return f'urn:uuid:{str(uuid.uuid4())}'
