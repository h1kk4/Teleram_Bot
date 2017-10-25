import zlib
import base64


def get_gzip_base64_encoded(file_path):
    handler = open(file_path, mode='rb').read()
    return base64.encodestring(zlib.compress(handler))

