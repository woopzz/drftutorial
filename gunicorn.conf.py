import os
import multiprocessing

bind = '0.0.0.0:8000'
wsgi_app = 'drftutorial.wsgi'

debug = os.getenv('APP_DEBUG', False)
if debug and debug == 'True':
    reload = True
    workers = 1
else:
    workers = 2
