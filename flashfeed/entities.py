__all__ = [
    'db',
    'NewsOutlet',
    'NewsSource',
    'NewsEntity',
]

from pony import orm
import datetime

db = orm.Database()


class NewsOutlet(db.Entity):
    name = orm.Required(str)
    title = orm.Required(str)
    country = orm.Required(str)
    url = orm.Required(str, unique=True)
    news_sources = orm.Set('NewsSource')
    created_at = orm.Required(datetime.datetime)
    updated_at = orm.Required(datetime.datetime)


class NewsSource(db.Entity):
    name = orm.Required(str)
    title = orm.Required(str)
    country = orm.Required(str)
    region = orm.Required(str)
    news_outlet = orm.Required(NewsOutlet)
    url = orm.Required(str, unique=True)
    base_url = orm.Required(str)
    news_entities = orm.Set('NewsEntity')
    created_at = orm.Required(datetime.datetime)
    updated_at = orm.Required(datetime.datetime)


class NewsEntity(db.Entity):
    uuid = orm.Required(str)
    name = orm.Required(str)
    title = orm.Required(str)
    url = orm.Required(str)
    media_type = orm.Required(str)
    news_source = orm.Required(NewsSource)
    date = orm.Required(datetime.datetime)
    created_at = orm.Required(datetime.datetime)
    updated_at = orm.Required(datetime.datetime)
