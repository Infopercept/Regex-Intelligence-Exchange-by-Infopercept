# How to run (quick start)

This file gives quick commands to run the application locally (development) and in production (Gunicorn / Docker).

Development (simple, using Flask built-in server)

1. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. Run the web app (development):

```powershell
# from repository root
python web/app.py --host 127.0.0.1 --port 5000 --debug
```

Production (Gunicorn)

1. Ensure `requirements.txt` is installed in your environment and optional `.env` is configured from `.env.example`.

2. Run with Gunicorn (WSGI entrypoint present at `web.wsgi:app`):

```powershell
gunicorn -w 4 -b 0.0.0.0:5000 web.wsgi:app
```

Docker (recommended for reproducible deploy)

1. Build the image:

```powershell
docker build -t regex-intel .
```

2. Run (mapping port 5000):

```powershell
docker run -p 5000:5000 --rm regex-intel
```

Or use docker-compose (recommended for optional Redis):

```powershell
docker-compose up --build
```

Healthcheck

Once running, the health endpoint is available at:

http://localhost:5000/api/health

Notes

- Patterns are expected in `patterns/by-vendor`.
- For production, place sensitive config in environment variables (see `.env.example`).