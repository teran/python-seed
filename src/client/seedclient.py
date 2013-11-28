#!/usr/bin/env python

import json
import logging
from time import sleep
from optparse import OptionParser
import sys
import requests
import transmissionrpc


class SeedClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
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
            '-o', '--output-dir', dest='output_dir',
            help='Output directory for downloaded torrent'
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

        handler = logging.StreamHandler(sys.stderr)
        if self.options.verbose:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def download(self):
        tc = transmissionrpc.Client(
            address='127.0.0.1',
            port='9091',
            user='transmission',
            password='transmission'
        )

        if tc:
            self.logger.debug('Connected to Transmission RPC')

        try:
            download_dir = self.options.output_dir or '/tmp/'
            torrent = tc.add_torrent(
                torrent=self.options.magnet,
                download_dir=download_dir)
            self.logger.debug('Torrent %s added, downloading to %s' % (torrent.id, download_dir))
        except:
            try:
                for t in tc.get_torrents():
                    if t.magnetLink == self.options.magnet:
                        torrent = tc.get_torrent(t.id)
            except:
                raise

        while True:
            t = tc.get_torrent(
                torrent_id=torrent.id)

            self.logger.info('Torrent status: %s; Progress: %s; Current speed: %s KBps' % (
                t.status, t.progress, t.rateDownload / 1024))

            if t.status not in ['seeding', 'complete']:
                sleep(3)
            else:
                files = t.files()
                for f in files:
                    self.logger.info('Downloaded file: %s/%s' % (t.downloadDir, files[f]['name']))
                    print '%s/%s' % (t.downloadDir, files[f]['name'])
                exit(0)

    def upload(self):
        url = 'http://%s:%s/api/create' % (
            self.options.seed_host, self.options.seed_port)
        self.logger.debug('Sending POST request to %s' % url)
        response = requests.post(
            url,
            files={'file': open(self.options.file, 'rb')})
        try:
            print json.loads(response.content)['magnet']
            exit(0)
        except:
            self.logger.error('Unexpected response: %s' % response.content)
            raise


if __name__ == "__main__":
    sc = SeedClient()

    if sc.options.download:
        sc.download()
    elif sc.options.upload:
        sc.upload()
    else:
        sc.parser.print_help()
        exit(1)
