"""
Этот модуль сождержит класс OpenSubtitles, реализующий работу с OpenSubtitles API
"""
from xmlrpc.client import ServerProxy
from settings import Settings
import logging

logging.basicConfig(format="""%(asctime)s - %(name)s -
                        %(levelname)s - %(message)s""",
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class OpenSubtitles(object):
    def __init__(self):
        self.xmlrpc = ServerProxy(Settings.OPENSUBTITLES_SERVER,
                                  allow_none=True)
        self.language = Settings.LANGUAGE
        self.token = None

    def _get_from_data_or_none(self, key):
        """
        Проверка на аутентификацию
        Args:
            key (str): строка с параметром который нужно вернуть
        Returns:
            (str) : возвращаемое значение
        """
        status = self.data.get('status').split()[0]
        return self.data.get(key) if '200' == status else None

    def login(self):
        """
        Авторизация
        Returns:
            (str) : токен
        """
        self.data = self.xmlrpc.LogIn(Settings.USER_NAME, Settings.USER_PASSWORD,
                                      self.language, Settings.USER_AGENT)
        token = self._get_from_data_or_none('token')

        if token:
            self.token = token
        return token

    def logout(self):
        """
        Логаут
        Returns:
            (str) : статус
        """
        data = self.xmlrpc.LogOut(self.token)
        return '200' in data.get('status')

    def search_subtitles(self, params):
        """
        Поиск субтитров
        Args:
            params(dict):
                + язык субтитров
                + id фильма на сайте *imdb.com*
        Returns:
            (dic) :
                + id субтитров
                + формат субтитров
                + id фильма
        """
        self.data = self.xmlrpc.SearchSubtitles(self.token, params)
        return self.data

    def search_movies_on_imdb(self, params):
        """
        Поиск фильмов
        Args:
            params(dict):
                + название фильма
        Returns:
            (dic) :
                + id фильма
                + название фильма
        """
        self.data = self.xmlrpc.SearchMoviesOnIMDB(self.token, params)
        return self.data

    def download_subtitles(self, params):
        """
        Загрузка субтитров
        Args:
            params(int): id субтитров
        Returns:
            (dic) :
                + id субтитров
                + строка с субтитрами
        """
        self.data = self.xmlrpc.DownloadSubtitles(self.token, params)
        return self.data
