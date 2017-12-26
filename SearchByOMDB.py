"""
Этот модуль сождержит класс OMDB, реализующий работу с OMDb API(The Open Movie Database)
"""
import omdb
from xmlrpc.client import ServerProxy
from settings import Settings
import logging

logging.basicConfig(format="""%(asctime)s - %(name)s -
                        %(levelname)s - %(message)s""",
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class OMDB():
    def __init__(self):
        self.Client = omdb.Client(apikey=Settings.OMDBapikey)
        omdb.set_default('apikey', Settings.OMDBapikey)

    def get_title(self, imdb_id):
        """
        Получение названия фильма по его imdb_id
        Args:
            imdb_id (int): id фильма на сайте *imdb.com*
        Returns:
            (str): название фильма
        """
        data = omdb.imdbid("tt%s" % imdb_id)
        if "title" in data:
            return data.title
        else:
            return None

    def search_film(self, title):
        """
        Поиск фильма
        Args:
            title(str): название фильма
        Returns:
            (dict): фильм:
                + тип фильма
                + imdb_id
        """
        data = omdb.get(title=title)
        dic = {}
        if data:
            if data.type == 'movie':
                dic['type'] = 0
            else:
                dic['type'] = 1
            dic['imdb_id'] = data.imdb_id[2:]
            return dic
        else:
            return None

    def search_series(self, params):
        """
        Поиск сериала
        Args:
            params (str): строка с названием фильма, номером сезона и эпизода
        Returns:
            (int): id фильма на сайте *imdb.com*
        """
        data = params.split()
        episode = data.pop()[1:]
        season = data.pop()[1:]
        title = ''
        for label in data:
            title += ''.join([label, ' '])
        data1 = omdb.get(title=title, season=season, episode=episode)
        logger.info("search for title %s, season %s, episode %s" % (title, season, episode))
        logger.info("returned data %s" % (data1))

        return data1
