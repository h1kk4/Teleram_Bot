import zlib
import gzip
import base64
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
class Utils(object):

    def get_gzip_base64_encoded(file_path):
        handler = open(file_path, mode='rb').read()
        return base64.encodestring(zlib.compress(handler))

    def decode(self, string, id):

        str = base64.b64decode(string)

        decompressed_data = zlib.decompress(str, 16 + zlib.MAX_WBITS)

        # with gzip.open('/Users/alex/Documents/-||-/file.txt.gz',  , 'w') as f:
        #     f.write(decompressed_data)
        #     #decompressed_data.encode('utf-8').strip()
        #     return decompressed_data.decode()



