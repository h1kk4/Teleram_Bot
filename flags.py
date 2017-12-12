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
        self.words = {}
        self.library = {}
        self.titles = {}
        logger.info("init new flag")

    def set_flag_series(self, bool):
        logger.info("set flag_series %s" % bool)
        self.flag_series = bool

    def set_flag_search(self, bool):
        logger.info("set flag_search %s" % bool)
        self.flag_search = bool

    def set_id_series(self, id):
        logger.info("set title of series as %s" % id)
        self.id_series = id

    def set_library(self, dic):
        logger.info("set library %s" % dic)
        self.library = dic

    def set_words(self, dic):
        logger.info("set words %s" % dic)
        self.words = dic

    def get_flag_series(self):
        return self.flag_series

    def get_flag_search(self):
        return self.flag_search

    def get_id_series(self):
        return self.id_series

    def get_library(self):
        return self.library

    def get_words(self):
        return self.words

    def set_titles(self, dic):
        logger.info("set titles %s" % dic)
        self.titles = dic

    def get_titles(self):
        return self.titles

    def reset_library(self):
        logger.info("library reset")
        self.library = {}

    def reset_words(self):
        logger.info("words reset")
        self.words = {}
