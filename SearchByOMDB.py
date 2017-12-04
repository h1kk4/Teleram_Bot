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
        self.Client = omdb.Client(apikey=Settings.apikey)
        omdb.set_default('apikey', Settings.apikey)

    def get_title(self, params):
        data = omdb.imdbid("tt%s" % params)
        return data.title

    def search_film(self, title):
        data = omdb.get(title = title)
        dic = {}
        if data:
            if data.type == 'movie':
                dic ['type'] = 0
            else:
                dic['type'] = 1
            dic ['imdb_id']= data.imdb_id[2:]
            return dic
        else:
            return None


    def search_series(self, params):
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
