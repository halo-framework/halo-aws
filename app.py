# -*- coding: utf-8 -*-
"""Create an application instance."""
from flask_api import FlaskAPI


def create_app(config_object='halolib.settings'):
    """An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = FlaskAPI(__name__.split('.')[0])
    app.config.from_object(config_object)
    with app.app_context():
        from .halolib.flask.viewsx import TestLinkX, PerfLinkX
        app.add_url_rule("/", view_func=TestLinkX.as_view("member"))
        app.add_url_rule("/perf", view_func=PerfLinkX.as_view("perf"))
    return app


app = create_app()

# from halolib.halolib.viewsx import TestLinkX, PerfLinkX
# app.add_url_rule("/", view_func=TestLinkX.as_view("member"))
# app.add_url_rule("/perf", view_func=PerfLinkX.as_view("member"))
