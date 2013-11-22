#!/usr/bin/env python

import json
import logging
from time import sleep
from optparse import OptionParser

import requests
import transmissionrpc


class SeedClient:
    def __init__(self):
        self.parser = OptionParser()
        self.parser.add_option(
            '-u', '--upload', action='store_true', dest='upload',
            help='upload file, start seeding and detach')
        self.parser.add_option(
            '-f', '--file', dest='file',
            help='filename to operate with'
        )
        self.parser.add_option(
            '-d', '--download', action='store_true', dest='download',
            help='download file, proceed seeding and detach with printed '
                 'localpath')
        self.parser.add_option(
            '-m', '--magnet-link', dest='magnet',
            help='download file with magnet link'
        )

        self.parser.add_option(
            '-v', '--verbose', action='store_true', dest='verbose',
            help='print verbose information during work'
        )

        self.parser.add_option(
            '--seed-host', dest='seed_host',
            help='Seed host'
        )
        self.parser.add_option(
            '--seed-port', dest='seed_port',
            help='Seed port'
        )
        (self.options, self.args) = self.parser.parse_args()

        self.logger = logging.basicConfig(

        )

    def download(self):
        tc = transmissionrpc.Client(
            address='127.0.0.1',
            port='9091',
            user='transmission',
            password='transmission'
        )

        torrent = tc.add_torrent(self.options.magnet)

        while True:
            t = tc.get_torrent(
                torrent_id=torrent.id)

            if t.status not in ['seeding', 'complete']:
                sleep(3)
            else:
                for f in t.files():
                    print '%s/%s' % (t.downloadDir, f.name)
                exit(0)

    def upload(self):
        response = requests.post(
            'http://%s:%s/api/create' % (
                self.options.seed_host, self.options.seed_port),
            files={'file': open(self.options.file, 'rb')})

        print json.loads(response.content)['magnet']
        exit(0)


if __name__ == "__main__":
    sc = SeedClient()

    if sc.options.download:
        sc.download()
    elif sc.options.upload:
        sc.upload()
    else:
        sc.parser.print_help()
        exit(1)
