"""
Этот модуль сождержит класс Flags, реализующий кореектную работу бота при использовании его несколькими льдьми
"""
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
        """
        Установить значение флага "сериал"
        Args:
            bool (bool): значение флага
        """
        logger.info("set flag_series %s" % bool)
        self.flag_series = bool

    def set_flag_search(self, bool):
        """
        Установить значение флага "поиск"
        Args:
            bool (bool): значение флага
        """
        logger.info("set flag_search %s" % bool)
        self.flag_search = bool

    def set_id_series(self, id):
        """
        Установить значени ефлага "id сериала"
        Args:
            id (int): id сериала
        """
        logger.info("set title of series as %s" % id)
        self.id_series = id

    def set_library(self, dic):
        """
        Установить значение флага "library"
        Args:
             dic (dict): фильмы:
                + index
                + imdb_id
        """
        logger.info("set library %s" % dic)
        self.library = dic

    def set_words(self, dic):
        """
        Установить значение флага "words"
        Args:
            dic (dict): слова:
                + id слова из таблицы words
                + слово
        """
        logger.info("set words %s" % dic)
        self.words = dic

    def set_titles(self, dic):
        """
        Установить значение флага "titles"
        Args:
            dic (dict): фильмы:
                + index
                + imdb_id
        """
        logger.info("set titles %s" % dic)
        self.titles = dic

    def get_flag_series(self):
        """
        Получить значение флага "сериал"
        Returns:
            (bool): значение флага
        """
        return self.flag_series

    def get_flag_search(self):
        """
        Получить значение флага "поиск"
        Returns:
            (bool): значение флага
        """
        return self.flag_search

    def get_id_series(self):
        """
        Получить значение флага "id сериала"
        Returns:
            (bool): значение флага
        """
        return self.id_series

    def get_library(self):
        """
        Получить значение флага "library"
        Returns:
            (dict): фильмы:
                + index
                + imdb_id
        """
        return self.library

    def get_words(self):
        """
        Получить значение флага "words"
        Returns:
            (dict): слова:
                + index
                + word
        """
        return self.words

    def get_titles(self):
        """
        Получить значение флага "titles"
        Returns:
            (dict): фильмы:
                + index
                + imdb_id
        """
        return self.titles

    def reset_library(self):
        """
        Сбросить значение флага "library"
        """
        logger.info("library reset")
        self.library = {}

    def reset_words(self):
        """
        Сбросить значение флага "library"
        """
        logger.info("words reset")
        self.words = {}
