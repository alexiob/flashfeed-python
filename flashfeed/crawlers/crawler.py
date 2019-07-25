import requests
import uuid


class Resource(object):
    crawler = None
    logger = None
    news_source = None
    news_entities = None
    news_entity_name = None

    def on_get(self, req, resp):
        resp.media = self.crawler.feed(
            self.logger,
            self.news_source,
            self.news_entities,
            self.news_entity_name
        )


class Crawler(object):
    NAME = 'crawler'

    @staticmethod
    def fetch(logger, news_source, news_entities):
        raise NotImplementedError()

    @staticmethod
    def resource(logger, news_source, news_entities, news_entity_name):
        class_name = f'{__class__.NAME}_{__class__._news_entity_key(news_source, news_entity_name, "_")}'
        resource = type(class_name, (Resource, ), dict(
            crawler=__class__,
            logger=logger,
            news_source=news_source,
            news_entities=news_entities,
            news_entity_name=news_entity_name
        ))()

        return resource

    @staticmethod
    def feed(logger, news_source, news_entities, news_entity_name):
        feed = []

        news_entity_key = __class__._news_entity_key(news_source, news_entity_name)
        news_entity = news_entities.get(news_entity_key, None)

        if news_entity:
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

    @staticmethod
    def _news_entity_key(news_source, news_entity_name, join_key='-'):
        key = join_key.join([
            news_source['news_outlet']['name'],
            news_source['name'],
            news_source['country'],
            news_source['region'],
            news_entity_name
        ])
        return key

