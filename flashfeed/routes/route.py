__all__ = ['Route']


class Route(object):
    route = '/v1/api/unknown'

    def __init__(self, logger):
        self.logger = logger
