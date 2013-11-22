from json import dumps
import os
import subprocess

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, \
    HttpResponseServerError, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
import transmissionrpc


tc = transmissionrpc.Client(
    settings.TRANSMISSION['default']['HOST'],
    port=settings.TRANSMISSION['default']['PORT'],
    user=settings.TRANSMISSION['default']['USER'],
    password=settings.TRANSMISSION['default']['PASSWORD'])


@csrf_exempt
def create(request):
    if request.method == 'POST':
        if 'file' in request.FILES:
            file = request.FILES.get('file')
            filename = os.path.basename(file.name)

            fp = open('%s/%s' % (settings.VAULT_PATH, file.name), 'w')
            for chunk in file.chunks():
                fp.write(chunk)
            fp.close()
        elif 'url' in request.POST:
            url = request.POST['url']
            filename = os.path.basename(request.POST['url'])
            try:
                p = subprocess.Popen(
                    "/usr/bin/wget '%s' -O '%s/%s'" % (url, settings.VAULT_PATH, filename),
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
                )
                stdout, stderr = p.communicate()
                p.wait()
            except:

                os.unlink('%s/%s' % (settings.VAULT_PATH, filename))
                return HttpResponseServerError(
                    content=dumps({
                        'status': 'error',
                        'reason': 'wget failed to download an iso: %s' % ''.join((stdout, stderr))
                    }, indent=4, sort_keys=False),
                    content_type='application/json'
                )
        else:
            return HttpResponseBadRequest(
                content=dumps({
                    'status': 'error',
                    'reason': 'file named file required in POSTed data'
                }, indent=4, sort_keys=False),
                content_type='application/json'
            )

        p = subprocess.Popen(
            "/usr/bin/mktorrent --announce='%s' '%s/%s' --output='%s'" % (
                settings.TRACKER_URL,
                settings.VAULT_PATH,
                filename,
                '/tmp/' + filename + '.torrent'
            ),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )

        stdout, stderr = p.communicate()
        p.wait()

        t = tc.add_torrent(
            '/tmp/%s.torrent' % filename,
            download_dir=settings.VAULT_PATH
        )

        t = tc.get_torrent(t.id)

        return HttpResponse(
            content=dumps({
                'status': 'ok',
                'magnet': t.magnetLink
            }, indent=4, sort_keys=False),
            content_type='application/json'
        )
    else:
        return HttpResponseBadRequest(
            content=dumps({
                'status': 'error',
                'reason': 'request method should be POST'
            }, indent=4, sort_keys=False),
            content_type='application/json'
        )

def list(request):
    list = tc.get_torrents()
    out = {}
    for k in list:
        out[k.name] = k.magnetLink

    return HttpResponse(
        content=dumps(
            out,
            indent=4,
            sort_keys=False),
        content_type='application/json'
    )

def status(request, name):
    list = tc.get_torrents()

    data = {}

    for torrent in list:
        if torrent.name == name:
            data = {
                'id': torrent.id,
                'name': torrent.name,
                'status': torrent.status,
                'progress': torrent.progress,
                'magnet': torrent.magnetLink
            }

    if not data:
        return HttpResponseNotFound(
            content=dumps({
                'status': 'error',
                'reason': 'no such torrent found'
            }, indent=4, sort_keys=False),
            content_type='application/json'
        )

    return HttpResponse(
        content=dumps(
            data,
            indent=4, sort_keys=False
        ), content_type='application/json'
    )
