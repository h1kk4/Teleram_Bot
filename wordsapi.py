import requests
from settings import Settings


MASHAPE_WORDS_API_KEY= Settings.MASHAPE_KEY
MASHAPE_WORDS_API_URL = 'https://wordsapiv1.p.mashape.com/words/'


def get_cards(word):
    response = requests.get('%s%s' % (MASHAPE_WORDS_API_URL, word),
                            headers={
                                'X-Mashape-Key': MASHAPE_WORDS_API_KEY,
                                'Accept': 'application/json'
                            }
                            )

    res = response.json()
    if 'results' not in res:
        return []

    if 'pronunciation' in res:
        pron = res['pronunciation']
        if 'all' in pron:
            pron = pron['all']
    else:
        pron = None

    card = {

        'word': res['word'],
        'def': [],
        'src': 'wordsapi',

    }
    for result in res['results']:

        if pron:
            card['pron'] = pron

        if 'definition' in result:
            card['def'].append(result['definition'])

        else:
            continue

    return card
