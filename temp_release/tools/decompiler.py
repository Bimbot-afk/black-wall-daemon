import zlib

try:
    import brotli
except ImportError:
    try:
        import brotlicffi as brotli
    except ImportError:
        brotli = None

def decompress_gzip(data):
    if not data:
        return b""
    data = bytes(data)
    try:
        desc = zlib.decompressobj(16 + zlib.MAX_WBITS)
        return desc.decompress(data)
    except Exception:
        return data

def decompress_brotli(data):
    if not data or brotli is None:
        return data
    data = bytes(data)
    try:
        return brotli.decompress(data)
    except Exception:
        return data