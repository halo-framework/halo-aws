from __future__ import print_function

flx = None
try:
    from django.conf import settings
    flx = False
except:
    try:
        from flask import current_app as app

        flx = True
    except:
        pass


class settingsx(object):
    def __getattribute__(self, name):
        global flx
        if flx == False:
            from django.conf import settings
            return settings.__getattr__(name)
        try:
            settings = app.config
            attr = settings.get(name)
            return attr
        except RuntimeError as e:
            print("settingsx=" + name + " error:" + str(e))
            return None
