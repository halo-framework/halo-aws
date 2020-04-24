from __future__ import print_function

from flask import current_app as app

class settingsx():
    def __getattribute__(self, name):
        global flx
        try:
            settings = app.config
            attr = settings.get(name)
            return attr
        except RuntimeError as e:
            print("settingsx=" + name + " error:" + str(e))
            return None