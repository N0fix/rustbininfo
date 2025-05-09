import ssl

import httpx
import truststore

ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
client = httpx.Client(verify=ctx)
