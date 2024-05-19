from .settings import *

ELASTICSEARCH_INDEX_NAMES = {
    k: 'test_' + v
    for k, v in ELASTICSEARCH_INDEX_NAMES.items()
}
