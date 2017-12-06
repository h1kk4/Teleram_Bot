import re
import requests

MASHAPE_URBAN_KEY = 'y4ueGKZdPzmshLr6dheyPokoxvolp1vWfXQjsneXC1iVJBX4rQ'
MASHAPE_URBAN_URL = 'https://mashape-community-urban-dictionary.p.mashape.com/define'


def mk_sent(text):
    text = text.strip().strip('"\'`').strip()
    if text[-1] not in '.!?':
        text += '.'

    return text.capitalize()


def get_card(word, min_len=15, max_len=128):
    response = requests.get(
        MASHAPE_URBAN_URL,
        params={
            'term': word
        },
        headers={
            'X-Mashape-Key': MASHAPE_URBAN_KEY,
            'Accept': 'text/plain'
        }
    )

    res = response.json()
    card = {
        'word': word,
        'def': [],
        'src': "urbandict"
    }

    for result in res['list']:

        if 'definition' in result and len(result['definition']) < max_len:

            parts = re.split('[\r\n\.;]+', result['definition'])
            parts = [p for p in parts if not re.findall('See\s', p)]
            parts = [re.sub('\d\.\s?', '', p) for p in parts if p]
            parts = [mk_sent(p) for p in parts]

            card['def'].append([])
            for part in parts:
                card['def'][-1].append({'text': part, 'type': 'mean'})

            if 'example' in result and len(result['example']) > min_len:
                card['def'][-1].append({'text': mk_sent(result['example']), 'type': 'ex'})

    return card if card['def'] else None
