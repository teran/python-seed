#!/usr/bin/env python

import transmissionrpc

tc = transmissionrpc.Client(
    address='127.0.0.1',
    port='9091',
    user='transmission',
    password='transmission'
)

for torrent in tc.get_torrents():
    if torrent.status in ['paused', 'stopped']:
        tc.remove_torrent(
            torrent.id,
            delete_data=True
        )
