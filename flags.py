import logging
logging.basicConfig(format="""%(asctime)s - %(name)s -
                        %(levelname)s - %(message)s""",
                    level=logging.INFO)

logger = logging.getLogger(__name__)
class Flags(object):

    def __init__(self):
        self.flag_series = False
        self.id_series = ''
        self.flag_search = False
        logger.info("init new flag")

    def set_flag_series(self, bool):
        logger.info("set flag_series %s"%bool)
        self.flag_series = bool

    def set_flag_search(self, bool):
        logger.info("set flag_search %s" % bool)
        self.flag_search = bool

    def set_id_series(self, id):
        logger.info("set title of series as %s" %id)
        self.id_series = id

    def get_flag_series(self):
        return self.flag_series

    def get_flag_search(self):
        return self.flag_search

    def get_id_series(self):
        return self.id_series

    def reset(self):
        # TODO add resetting flags at the end of searching
        self.flag_series = False
        self.id_series = ''
        self.flag_search = False
        logger.info("reset flag")