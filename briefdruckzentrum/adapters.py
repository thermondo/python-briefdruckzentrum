from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context


CIPHERS = 'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:DES-CBC3-SHA:ECDH+AES128:DH+AES:ECDH+HIGH' \
          ':DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:!eNULL:!MD5'


class SSLAdapter(HTTPAdapter):
    """Custom HTTPS Transport Adapter that uses cipher, supported by Briefdruckzentrum."""
    def init_poolmanager(self, connections, maxsize, block, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super(SSLAdapter, self).init_poolmanager(
            connections, maxsize, block, *args, **kwargs
        )
