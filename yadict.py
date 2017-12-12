import requests
from settings import Settings

YADICT_KEY = Settings.YADICT_KEY
YADICT_URL = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup'
YADICT_LANG = 'en-ru'

YATRANSLATE_KEY = Settings.YATRANSLATE_KEY
YATRANSLATE_URL = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
YATRANSLATE_LANG = 'en-ru'


def get_card(word):
    response = requests.get(
        YADICT_URL,
        params={
            'key': YADICT_KEY,
            'lang': YADICT_LANG,
            'text': word
        }
    )
    res = response.json()
    if 'def' not in res:
        return None

    card = {
        'word': word,
        'syn': [],
        'src': 'yadict'

    }

    for definition in res['def']:

        if 'tr' not in definition:
            continue

        for translation in definition['tr']:

            if 'mean' not in translation:
                continue

            for mean in translation['mean']:
                card['syn'].append(mean['text'])

    return card if card['syn'] else None


def get_transcription(word):
    try:
        response = requests.get(
            YADICT_URL,
            params={
                'key': YADICT_KEY,
                'lang': YADICT_LANG,
                'text': word
            }
        )
        res = response.json()

        return res['def'][0]['ts']

    except Exception:
        return None


def get_translations(word):
    try:
        response = requests.get(
            YATRANSLATE_URL,
            params={
                'key': YATRANSLATE_KEY,
                'lang': YATRANSLATE_LANG,
                'text': word
            }
        )
        res = response.json()

        return res['text']

    except Exception:
        return None
