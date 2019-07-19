__all__ = [
    'CRAWLERS'
]

from .rainnews import RaiNews

CRAWLERS = {
    RaiNews.NAME: RaiNews
}
