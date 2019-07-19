import uuid
import json
from urllib.parse import urlparse
from dateutil.parser import parse
import falcon
from apscheduler.schedulers.background import BackgroundScheduler
import os
import logging
import sys
import pprint

import datetime

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger

NEWS_OUTLETS = json.load(open('./config/news_outlets.json'))

# TODO:
# - cleanup old feeds, per NewsSource/NewsEntity.name
# - POST to seed new sources


class RAIFeed(object):
    DATA_FOLDER = 'data'
    DB_NAME = 'flashfeed.sqlite'

    def __init__(self):
        self.max_news_entries = 5

        self._db_setup(NEWS_OUTLETS)

    # def _to_https(self, url):
    #     if url.startswith('http://'):
    #         url = 'https://' + url.lstrip('http://')
    #     return url

    # def _resolve_url(self, url):
    #     url = requests.get(url, allow_redirects=False).headers['location']
    #     # url = urlparse(url)
    #     # url = url.scheme + '://' + url.netloc + url.path

    #     return url

    # def crawl(self):
    #     logger.info('raifeed.crawl')

    #     with orm.db_session:
    #         db_news_sources = NewsSource.select()

    #         for db_news_source in db_news_sources:
    #             logger.info(
    #                 f'raifeed.crawl.db_news_source: rocessing name={db_news_source.name} country={db_news_source.country} region={db_news_source.region} url={db_news_source.url}')
    #             html_doc = requests.get(db_news_source.url).content
    #             soup = BeautifulSoup(html_doc, 'html.parser')

    #             urls = {}

    #             dataFeeds = soup.select('[data-feed]')
    #             # print(dataFeeds)

    #             for dataFeed in dataFeeds:
    #                 # print(dir(dataFeed))

    #                 name = dataFeed.getText().lower().replace(' ', '_')
    #                 url = db_news_source.base_url + dataFeed['data-feed']
    #                 content = requests.get(url).json()
    #                 items = content.get('items', [])

    #                 if items:
    #                     item = items[0]
    #                     title = item['title']
    #                     date = parse(item['date'])
    #                     url = self._to_https(item['mediaUrl'])
    #                     media_type = self._get_media_type(item['type'])
    #                     db_news_entity = None

    #                     logger.info(
    #                         f'raifeed.crowl.db_news_entity.check: date={date} name={name} title={title} news_source={db_news_source.name} url={url}')

    #                     db_news_entity = NewsEntity.select(
    #                         lambda ne:
    #                             ne.name == name and
    #                             ne.news_source == db_news_source and
    #                             ne.url == url
    #                     ).first()

    #                     if db_news_entity:
    #                         logger.info(
    #                             f'raifeed.crawl.db_news_entity.exists: date={db_news_entity.date} updated_at={db_news_entity.updated_at} name={db_news_entity.name} title={db_news_entity.title} news_source={db_news_entity.news_source.name} url={db_news_entity.url}')
    #                         continue

    #                     now = datetime.datetime.now()

    #                     if not db_news_entity:
    #                         logger.info(
    #                             f'raifeed.crawl.db_news_entity.add: date={date} name={name} news_source={db_news_source.name} url={url}')
    #                         db_news_entity = NewsEntity(
    #                             uuid=f'urn:uuid:{str(uuid.uuid4())}',
    #                             name=name,
    #                             title=title,
    #                             date=date,
    #                             url=url,
    #                             media_type=media_type,
    #                             news_source=db_news_source,
    #                             created_at=now,
    #                             updated_at=now
    #                         )
    #                     else:
    #                         db_news_entity = list(db_news_entity)[0]
    #                         db_news_entity.title = title
    #                         db_news_entity.date = date
    #                         db_news_entity.url = url
    #                         db_news_entity.media_type = media_type
    #                         db_news_entity.updated_at = now

    def news_brief(self, outlet, source, country, region, name):
        logger.info('raifeed.news_brief')

        feed = []

        with orm.db_session:
            db_news_outlet = NewsOutlet.select(
                lambda no: no.name == outlet).first()
            db_news_source = NewsSource.select(
                lambda ns: ns.name == source and ns.country == country and ns.news_outlet == db_news_outlet).first()
            db_news_entities = NewsEntity.select(
                lambda ne: ne.news_source == db_news_source and ne.name == name).order_by(orm.desc(NewsEntity.updated_at))[:self.max_news_entries]

            for db_news_entity in db_news_entities:
                logger.info(
                    f'raifeed.news_brief.db_news_entity.exists: date={db_news_entity.date} updated_at={db_news_entity.updated_at} name={db_news_entity.name} title={db_news_entity.title} news_source={db_news_entity.news_source.name} url={db_news_entity.url}')

                titleText = f'{db_news_entity.news_source.name.upper()} {name.upper()} {db_news_entity.title}'
                mainText = ''
                updateDate = db_news_entity.updated_at.strftime(
                    '%Y-%m-%dT%H:%M:%S') + 'Z'
                feed_entry = {
                    'uid': db_news_entity.uuid,
                    'updateDate': updateDate,
                    'titleText': titleText,
                    'mainText': mainText,
                    'streamUrl': db_news_entity.url,
                    'redirectionUrl': db_news_entity.news_source.url
                }

                feed.append(feed_entry)

        return feed


class RaiNewsFVG(object):
    def on_get(self, req, resp):
        resp.media = rai_feed.news_brief(
            'rainews', 'rainews', 'it', 'fvg', 'gr')


app = falcon.API(media_type=falcon.MEDIA_JSON)

rai_feed = RAIFeed()

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    rai_feed.crawl,
    'interval',
    seconds=60*55
)


app.add_route('/v1/alexa/flashfeed/rainews/fvg/gr', RaiNewsFVG())

if __name__ == '__main__':
    rai_feed = RAIFeed()
    print('>>> CRAWL')
    rai_feed.crawl()
    print('>>> NEWS BRIEF', 'rainews', 'rainews', 'it', 'fvg', 'tgr')
    feed = rai_feed.news_brief('rainews', 'rainews', 'it', 'fvg', 'tgr')
    print(f'>>> FEED: {pprint.pformat(feed)}')
