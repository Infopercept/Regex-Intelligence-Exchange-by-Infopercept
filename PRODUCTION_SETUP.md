# Production Setup Guide

This guide provides instructions for deploying the Regex Intelligence Exchange in a production environment.

## Prerequisites

- Python 3.7 or higher
- Redis server (optional but recommended for caching)
- PostgreSQL database (optional, SQLite can be used for development)

## Installation Steps

### 1. Install Dependencies

```bash
cd web
pip install -r requirements.txt
```

If you encounter issues with PostgreSQL dependencies, you can install the binary version separately:

```bash
pip install psycopg2-binary
```

Or on Ubuntu/Debian:
```bash
sudo apt-get install libpq-dev python3-dev
pip install psycopg2
```

### 2. Install Redis (Recommended)

Redis provides caching capabilities that improve performance.

**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**On CentOS/RHEL:**
```bash
sudo yum install epel-release
sudo yum install redis
sudo systemctl start redis
sudo systemctl enable redis
```

**On macOS:**
```bash
brew install redis
brew services start redis
```

**On Windows:**
Download Redis from https://github.com/microsoftarchive/redis/releases

### 3. Configure Environment Variables

Create a `.env` file in the web directory with the following configuration:

```bash
# Environment
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Database (optional, for enhanced performance)
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/regex_exchange
# For SQLite:
# DATABASE_URL=sqlite:///patterns.db
# USE_DATABASE=false

# Redis (optional, for caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 4. Database Migration (Optional)

If you want to use database storage for better performance:

1. Configure your database connection in the environment variables
2. Set `USE_DATABASE=true`
3. Run the migration script:

```bash
cd web
python scripts/migrate_all_patterns.py
```

### 5. Start the Application

Run both the web interface and API:

```bash
cd web
python run.py --mode both --host 0.0.0.0 --port 5000 --api-port 5001
```

Or run them separately:

```bash
# Terminal 1 - Start API
cd web
python run.py --mode api --port 5001

# Terminal 2 - Start Web Interface
cd web
python run.py --mode web --port 5000
```

### 6. Access the Application

- Web Interface: http://localhost:5000
- API Documentation: http://localhost:5001/api/docs/
- API Base URL: http://localhost:5001/api/v1/

## Production Deployment

For production deployment, consider using:

1. **Gunicorn** or **uWSGI** as the WSGI server
2. **Nginx** or **Apache** as a reverse proxy
3. **Systemd** (Linux) or **Windows Services** for process management
4. **SSL/TLS** for secure connections

Example systemd service files:

**Web Interface Service** (`/etc/systemd/system/regex-exchange-web.service`):
```ini
[Unit]
Description=Regex Intelligence Exchange Web Interface
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/Regex-Intelligence-Exchange-by-Infopercept/web
Environment=FLASK_ENV=production
ExecStart=/path/to/venv/bin/python run.py --mode web --port 5000
Restart=always

[Install]
WantedBy=multi-user.target
```

**API Service** (`/etc/systemd/system/regex-exchange-api.service`):
```ini
[Unit]
Description=Regex Intelligence Exchange REST API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/Regex-Intelligence-Exchange-by-Infopercept/web
Environment=FLASK_ENV=production
ExecStart=/path/to/venv/bin/python run.py --mode api --port 5001
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable regex-exchange-web
sudo systemctl enable regex-exchange-api
sudo systemctl start regex-exchange-web
sudo systemctl start regex-exchange-api
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**: Ensure Redis is installed and running
2. **Database Connection Error**: Check database URL and credentials
3. **Port Conflicts**: Ensure ports 5000 and 5001 are available
4. **Permission Errors**: Ensure proper file permissions for the application directory

### Logs

Check application logs for debugging information:
```bash
tail -f web/logs/regex_exchange.log
```

## Performance Optimization

1. **Enable Redis**: Provides caching for better performance
2. **Use Database Storage**: For large pattern collections, database storage is more efficient
3. **Configure Proper Logging**: Use appropriate log levels for production
4. **Enable Gzip Compression**: Configure your reverse proxy for compression