#!/usr/bin/env python3

import http.server
import socketserver
import argparse
import os
import configparser
import sys
import logging

SCANARIUM_DIR_ABS=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, SCANARIUM_DIR_ABS)
from common import SCANARIUM_CONFIG
from common import FRONTEND_DIR_ABS
from common import FRONTEND_DYNAMIC_DIR_ABS
from common import get_dynamic_directory
del sys.path[0]

logger = logging.getLogger(__name__)


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    """Simple HTTP handler that aliases user-generated-content"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        f = super().translate_path(path)
        if f.startswith(FRONTEND_DYNAMIC_DIR_ABS + os.sep):
            f = f[len(FRONTEND_DYNAMIC_DIR_ABS + os.sep):]
            f = os.path.join(get_dynamic_directory(), f)
            f = os.path.normpath(f)
        return f


def serve_forever(port):
    socketserver.TCPServer.allow_reuse_address = True

    # Python <=3.6 does not allow to configure the directory to serve from,
    # but unconditionally servers from the current directory. As Linux Mint
    # Tricia is still on Python 3.6 and we do not want to exclude such users,
    # we instead chdir to the expected directory.
    os.chdir(FRONTEND_DIR_ABS)

    with socketserver.TCPServer(('', port), RequestHandler) as httpd:
        print('-------------------------------------------------------------')
        print()
        print('Scanarium demo server listening on port', port)
        print()
        print('To use Scanarium, yoint your browser to the followung URL:')
        print()
        print('  http://localhost:%d/' % (port))
        print()
        print('Note that this demo server is not secure. Please consider')
        print('to instead run it on a proper webserver like Apache HTTPD.')
        print()
        print('-------------------------------------------------------------')
        print()
        sys.stdout.flush()

        httpd.serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scanarium demo server', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('port', metavar='PORT', type=int, help='The port to listen for connections on', default=SCANARIUM_CONFIG['demo_server']['port'], nargs='?')
    args = parser.parse_args()

    serve_forever(args.port)
