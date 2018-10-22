from __future__ import print_function

try:
    from django.conf import settings

    flx = False
    # from flask import current_app as app
    # settings = app.config
except:
    from flask import current_app as app

    settings = app.config
    flx = True


class settingsx(object):
    def __getattribute__(self, name):
        if not flx:
            return settings.__getattr__(name)
        attr = settings.get(name)
        return attr
