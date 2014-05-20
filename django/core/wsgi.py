import django
from django.core.handlers.wsgi import WSGIHandler
from django.utils import six

try:
    import gunicorn
except ImportError:
    gunicorn = None


def get_wsgi_application():
    """
    The public interface to Django's WSGI support. Should return a WSGI
    callable.

    Allows us to avoid making django.core.handlers.WSGIHandler public API, in
    case the internal WSGI implementation changes or moves in the future.

    """
    django.setup()
    return WSGIHandler()


if gunicorn is not None:
    import gunicorn.app.base

    class DjangoApplication(gunicorn.app.base.Application):

        def __init__(self, options=None):
            self.options = options or {}
            super(DjangoApplication, self).__init__()

        def load_config(self):
            normalize_config = {key.lower(): value
                                for key, value in six.iteritems(self.options)}
            config = {key: value
                      for key, value in six.iteritems(normalize_config)
                      if key in self.cfg.settings and value is not None}
            for key, value in six.iteritems(config):
                self.cfg.set(key, value)

        def load(self):
            from django.core.servers.basehttp import get_internal_wsgi_application
            return get_internal_wsgi_application()
