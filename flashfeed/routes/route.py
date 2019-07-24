__all__ = ['Route']


class Route(object):
    route = '/unknown'

    def __init__(self, logger):
        self.logger = logger
