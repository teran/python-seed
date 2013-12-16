#!/usr/bin/env python

import json
import logging
from time import sleep
from optparse import OptionParser
import os
import sys
import subprocess
import transmissionrpc
import urllib2


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
            default=os.environ.get('MAGNET_LINK', None),
            help='download file with magnet link'
        )

        self.parser.add_option(
            '-o', '--output-dir', dest='output_dir',
            default=os.environ.get('SEEDCLIENT_OUTPUT_DIR', '/tmp'),
            help='Output directory for downloaded torrent'
        )

        self.parser.add_option(
            '-v', '--verbose', action='store_true', dest='verbose',
            default=os.environ.get('SEEDCLIENT_VERBOSE', False),
            help='print verbose information during work'
        )

        self.parser.add_option(
            '--seed-host', dest='seed_host',
            default=os.environ.get('SEED_HOST', None),
            help='Seed host'
        )
        self.parser.add_option(
            '--seed-port', dest='seed_port',
            default=os.environ.get('SEED_PORT', None),
            help='Seed port'
        )

        self.parser.add_option(
            '--transmission-host', dest='transmission_host',
            default=os.environ.get('TRANSMISSION_HOST', '127.0.0.1'),
            help='Transmission RPC host'
        )

        self.parser.add_option(
            '--transmission-port', dest='transmission_port',
            default=os.environ.get('TRANSMISSION_PORT', '9091'),
            help='Transmission RPC port'
        )

        self.parser.add_option(
            '--transmission-user', dest='transmission_user',
            default=os.environ.get('TRANSMISSION_USER', 'transmission'),
            help='Transmission RPC user'
        )

        self.parser.add_option(
            '--transmission-password', dest='transmission_password',
            default=os.environ.get('TRANSMISSION_PASSWORD', 'transmission'),
            help='Transmission RPC password'
        )

        self.parser.add_option(
            '--tracker-url', dest='tracker_url',
            default=os.environ.get('TRACKER_URL', None),
            help='Torrent tracker url'
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

        if self.options.upload or self.options.download:
            self.tc = transmissionrpc.Client(
                address='127.0.0.1',
                port='9091',
                user='transmission',
                password='transmission'
            )

    def download(self):
        self.logger.info('Starting downloading torrent %s' % self.options.magnet)
        try:
            torrent = self.tc.add_torrent(self.options.magnet)
        except transmissionrpc.error.TransmissionError as e:
            if str(e) == 'Query failed with result "duplicate torrent".':
                for torrent in self.tc.get_torrents():
                    if torrent.magnetLink == self.options.magnet:
                        if torrent.progress == 100:
                            self.logger.info('Torrent is already downloaded')
                            self.files(torrent)
                        else:
                            self.status(torrent)

            else:
                raise

        self.status(torrent)

    def files(self, torrent):
        files = torrent.files()

        for id in files:
            file = os.path.join(torrent.downloadDir, files[id]['name'])
            self.logger.debug('File: %s' % file)
            if self.options.output_dir is not torrent.downloadDir:
                destfile = os.path.join(
                    self.options.output_dir,
                    files[id]['name']
                )
                self.logger.info('Settings symlink for file %s to %s' % (
                    file, self.options.output_dir))
                os.symlink(
                    file,
                    destfile
                )
            print destfile
        exit(0)

    def upload(self):
        self.logger.info('Starting file seeding')

        cmd = "/usr/bin/mktorrent --announce='%s' '%s' --output='%s.torrent'" % (
            self.options.tracker_url,
            self.options.file,
            self.options.file
        )
        self.logger.info('Executing %s' % cmd)
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )

        stdout, stderr = p.communicate()
        p.wait()

        self.logger.debug('Command stdout: %s ; command stderr: %s' % (stdout, stderr))

        download_dir = os.path.dirname(self.options.file)
        self.logger.info('Adding %s.torrent downloaded to %s' % (
            self.options.file,
            download_dir
        ))
        torrent = self.tc.add_torrent(
            '%s.torrent' % self.options.file,
            download_dir=download_dir
        )
        self.tc.verify_torrent(torrent.id)
        self.tc.start_torrent(torrent.id)

        torrent = self.tc.get_torrent(torrent.id)

        self.logger.info('Magnet link: %s' % torrent.magnetLink)
        print torrent.magnetLink

    def status(self, torrent):
        while True:
            t = self.tc.get_torrent(torrent_id=torrent.id)
            self.logger.info('Torrent %s ; status %s ; progress %s' % (
                t.name, t.status, t.progress))
            if t.progress == 100:
                self.logger.info('Torrent %s download complete' % torrent.name)
                self.files(t)
            else:
                sleep(3)


if __name__ == "__main__":
    sc = SeedClient()

    if sc.options.download:
        sc.download()
    elif sc.options.upload:
        sc.upload()
    else:
        sc.parser.print_help()
        exit(1)
