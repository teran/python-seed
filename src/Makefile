#!/usr/bin/make -f

clean:
	dh_clean

install:
	install -d													$(WEBAPP_DESTDIR)/usr/share/python-django-seed
	install -d													$(WEBAPP_DESTDIR)/etc/uwsgi/apps-available
	install -d													$(WEBAPP_DESTDIR)/etc/uwsgi/apps-enabled
	install	-d													$(WEBAPP_DESTDIR)/etc/nginx/sites-available
	install -d													$(WEBAPP_DESTDIR)/etc/nginx/sites-enabled
	install -m644	$(CURDIR)/uwsgi.yaml						$(WEBAPP_DESTDIR)/etc/uwsgi/apps-available/seed.yaml
	install -m644	$(CURDIR)/nginx.conf						$(WEBAPP_DESTDIR)/etc/nginx/sites-available/seed.conf
	cp -r 			$(CURDIR)/seed								$(WEBAPP_DESTDIR)/usr/share/python-django-seed/
	install -d													$(CLIENT_DESTDIR)/usr/bin
	install -m755	$(CURDIR)/client/seedclient.py				$(CLIENT_DESTDIR)/usr/bin/seedclient.py
	install -d													$(CLEANER_DRSTDIR)/usr/bin
	install -m755	$(CURDIR)/cleaner/seedcleaner.py			$(CLEANER_DRSTDIR)/usr/bin/seedcleaner.py

