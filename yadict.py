import requests

YADICT_KEY = 'dict.1.1.20171114T191912Z.e6cf7f858e4de103.cda2e4f4935c5f9adb77424a55be06f0cf533cd4'
YADICT_URL = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup'
YADICT_LANG = 'en-ru'

YATRANSLATE_KEY = 'trnsl.1.1.20171014T220357Z.578d1703f2928529.8305107e8a6022f127dfb2a4fa177aeb5ae098cf'
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
        'src':'yadict'

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