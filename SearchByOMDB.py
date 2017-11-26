import omdb
from xmlrpc.client import ServerProxy
from settings import Settings
class OMDB():

    def __init__(self):
        self.Client=omdb.Client(apikey=Settings.apikey)
        omdb.set_default('apikey', Settings.apikey )
        print(self.Client)

    def search_title(self, params):
        data = omdb.imdbid("tt%s"%params)
        return data.title

    def search_series(self, params):
        data = params.split()
        episode = data.pop()[1:]
        season = data.pop()[1:]
        title = ''

        for label in data:
            title += ''.join([label, ' '])
        data1 = omdb.get(title=title, season = season, episode = episode)
        return data1.imdb_id
