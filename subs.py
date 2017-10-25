from xmlrpc.client import ServerProxy
from settings import Settings


class OpenSubtitles(object):

    def __init__(self, language=None):
        self.xmlrpc = ServerProxy(Settings.OPENSUBTITLES_SERVER,
                                  allow_none=True)
        self.language = language or Settings.LANGUAGE
        self.token = None

    def _get_from_data_or_none(self, key):
        status = self.data.get('status').split()[0]
        return self.data.get(key) if '200' == status else None

    def login(self,username,password):
        self.data = self.xmlrpc.LogIn(username, password,
                                 self.language, Settings.USER_AGENT)
        token = self._get_from_data_or_none('token')
        if token:
            self.token = token
        return token

    def logout(self):
        data = self.xmlrpc.LogOut(self.token)
        return '200' in data.get('status')

    def search_subtitles(self, params):
        '''Returns a list with the subtitles info.
        '''
        self.data = self.xmlrpc.SearchSubtitles(self.token, params)
        return self._get_from_data_or_none('data')


    def no_operation(self):

        data = self.xmlrpc.NoOperation(self.token)
        return '200' in data.get('status')

    def auto_update(self, program):

        data = self.xmlrpc.AutoUpdate(program)
        return data if '200' in data.get('status') else None

    def search_movies_on_imdb(self, params):
        self.data = self.xmlrpc.SearchMoviesOnIMDB(self.token, params)
        return self.data

    def download_subtitles(self, params):
        self.data = self.xmlrpc.DownloadSubtitles(self.token, params)
        return self.data


