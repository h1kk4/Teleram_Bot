import zlib
import gzip
import base64
import io
from language_toolkit import *


def decode_base64(data):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += b'=' * (4 - missing_padding)
    return base64.decodestring(data)


def get_words_set(string):
    # print("string", string)
    str = base64.b64decode(string)
    # print("base decode ->", str)
    decompressed_data = zlib.decompress(str, 16 + zlib.MAX_WBITS)
    # decompressed_data.encode('utf-8').strip()
    # decompressed_data.decode('cp1252').encode('utf-8')
    # return decompressed_data.decode('cp1252')
    subtitles = decompressed_data.decode('cp1252')
    data = set()
    for x in ((subtitles.split('\r\n\r\n'))):
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
    for x in ((subtitles.split('\r\n\r\n'))):
        if x.split('\n')[2:]:
            sentence = ''.join(x.split('\n')[2:])
            labels = get_unknown_words(text=sentence)
            if word in labels:
                return sentence

