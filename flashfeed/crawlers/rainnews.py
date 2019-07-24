from bs4 import BeautifulSoup

import datetime
from dateutil.parser import parse

from .crawler import Crawler


class RaiNews(Crawler):
    NAME = 'rainews'

    @staticmethod
    def fetch(logger, news_source, news_entities):
        logger.info(
            f'flashfeed.crawler.rainews: news_source={news_source["name"]} url={news_source["url"]}'
        )

        html_doc = RaiNews._request_get(news_source['url']).content
        soup = BeautifulSoup(html_doc, 'html.parser')

        urls = {}

        data_feeds = soup.select('[data-feed]')

        for data_feed in data_feeds:
            name = data_feed.getText().lower().replace(' ', '_')
            url = news_source['base_url'] + data_feed['data-feed']
            content = RaiNews._request_get(url).json()
            items = content.get('items', [])

            if items:
                item = items[0]
                title = item['title']
                date = parse(item['date'])
                url = RaiNews._to_https(item['mediaUrl'])
                media_type = RaiNews._get_media_type(item['type'])

                news_entity = news_entities.setdefault(news_source['id'], {})

                if news_entity and news_entity['name'] == name and news_entity['url'] == url:
                    logger.info(
                        f'flashfeed.crawler.rainews.present: date={date} name={name} title={title} news_source={news_source["name"]} url={url}'
                    )
                    return

                now = datetime.datetime.now()

                news_entity['uuid'] = RaiNews._uuid()
                news_entity['news_source'] = news_source
                news_entity['name'] = name
                news_entity['title'] = title
                news_entity['date'] = date
                news_entity['url'] = url
                news_entity['media_type'] = media_type
                news_entity['updated_at'] = now
                if 'created_at' not in news_entity:
                    news_entity['created_at'] = now

                logger.info(
                    f'flashfeed.crawler.rainews.fetched: date={date} name={name} title={title} news_source={news_source["name"]} url={url}'
                )
