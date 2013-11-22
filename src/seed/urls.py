from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^api/create', 'api.views.create'),
    (r'^api/list$', 'api.views.list'),
)
