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
        status = self.data.get('status').split()[0]
        return self.data.get(key) if '200' == status else None

    def login(self):
        self.data = self.xmlrpc.LogIn(Settings.USER_NAME, Settings.USER_PASSWORD,
                                      self.language, Settings.USER_AGENT)
        token = self._get_from_data_or_none('token')

        if token:
            self.token = token
        return token

    def logout(self):
        data = self.xmlrpc.LogOut(self.token)
        return '200' in data.get('status')

    def search_subtitles(self, params):
        self.data = self.xmlrpc.SearchSubtitles(self.token, params)
        return self.data

    def search_movies_on_imdb(self, params):
        self.data = self.xmlrpc.SearchMoviesOnIMDB(self.token, params)
        return self.data

    def download_subtitles(self, params):
        self.data = self.xmlrpc.DownloadSubtitles(self.token, params)
        return self.data
