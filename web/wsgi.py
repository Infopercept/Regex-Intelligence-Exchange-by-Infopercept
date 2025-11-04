"""WSGI entrypoint for production servers (e.g. Gunicorn).

Exposes the WSGI application object as `app` so servers can import it:

    gunicorn -w 4 -b 0.0.0.0:5000 web.wsgi:app

"""
from __future__ import annotations

from .app import create_app

app = create_app()
