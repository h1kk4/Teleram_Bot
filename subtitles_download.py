import zlib
import base64
from language_toolkit import *


def get_words_set(string):
    str = base64.b64decode(string)
    decompressed_data = zlib.decompress(str, 16 + zlib.MAX_WBITS)
    subtitles = decompressed_data.decode('cp1252')
    data = set()
    if subtitles.find("\r\n\r\n") == -1:
        k = '\n\n'
    else:
        k = '\r\n\r\n'
    for x in ((subtitles.split(k))):
        if x.split('\n')[2:]:
            sentence = ''.join(x.split('\n')[2:])
            labels = get_unknown_words(text=sentence)
            for label in labels:
                data.add(label)
    return data


def search_sentence(string, word):
    str = base64.b64decode(string)
    decompressed_data = zlib.decompress(str, 16 + zlib.MAX_WBITS)
    subtitles = decompressed_data.decode('cp1252')
    if subtitles.find("\r\n\r\n") == -1:
        k = '\n\n'
    else:
        k = '\r\n\r\n'
    for x in ((subtitles.split(k))):
        if x.split('\n')[2:]:
            sentence = ''.join(x.split('\n')[2:])
            labels = get_unknown_words(text=sentence)
            if word in labels:
                print(sentence)
                return sentence
