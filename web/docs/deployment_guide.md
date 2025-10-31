# Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Regex Intelligence Exchange web interface and RESTful API to various environments including development, staging, and production.

## Prerequisites

### System Requirements

- Python 3.7 or higher
- pip package manager
- Git (for cloning the repository)
- At least 2GB RAM (4GB recommended for production)
- 10GB free disk space (for pattern database and logs)

### Optional Components

- Redis server (for caching)
- Nginx or Apache (for reverse proxy in production)
- Docker and Docker Compose (for containerized deployment)
- Systemd (for service management on Linux)

## Environment Configuration

### Environment Variables

The application supports the following environment variables:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `FLASK_ENV` | Environment (development, staging, production) | development |
| `SECRET_KEY` | Flask secret key for sessions | Auto-generated |
| `HOST` | Host to bind to | 127.0.0.1 (dev) or 0.0.0.0 (prod) |
| `PORT` | Web application port | 5000 |
| `API_PORT` | API port | 5001 |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `REQUIRE_HTTPS` | Require HTTPS connections | False (dev) or True (prod) |
| `REDIS_HOST` | Redis server host | localhost |
| `REDIS_PORT` | Redis server port | 6379 |
| `REDIS_DB` | Redis database number | 0 (dev), 1 (staging), 2 (prod) |

## Deployment Methods

### 1. Manual Deployment

#### Step 1: Clone the Repository

```bash
git clone https://github.com/Infopercept/Regex-Intelligence-Exchange-by-Infopercept.git
cd Regex-Intelligence-Exchange-by-Infopercept/web
```

#### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

For development:
```bash
pip install -r requirements-dev.txt
```

#### Step 4: Configure Environment

Create a `.env` file in the web directory:

```bash
# Development environment
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
HOST=127.0.0.1
PORT=5000
API_PORT=5001
LOG_LEVEL=DEBUG
REQUIRE_HTTPS=False
```

#### Step 5: Run Applications

Start the web application:
```bash
python -m app.app
```

Start the API (in a separate terminal):
```bash
python -m api.app
```

### 2. Production Deployment with Systemd

#### Step 1: Create System User

```bash
sudo useradd -r -s /bin/false regex-exchange
```

#### Step 2: Install Application

```bash
sudo mkdir -p /opt/regex-exchange
sudo chown regex-exchange:regex-exchange /opt/regex-exchange
sudo -u regex-exchange git clone https://github.com/Infopercept/Regex-Intelligence-Exchange-by-Infopercept.git /opt/regex-exchange
```

#### Step 3: Set Up Virtual Environment

```bash
sudo -u regex-exchange python3 -m venv /opt/regex-exchange/venv
sudo -u regex-exchange /opt/regex-exchange/venv/bin/pip install -r /opt/regex-exchange/web/requirements.txt
```

#### Step 4: Create Environment Configuration

```bash
sudo -u regex-exchange tee /opt/regex-exchange/.env << EOF
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-here
HOST=0.0.0.0
PORT=80
API_PORT=81
LOG_LEVEL=WARNING
REQUIRE_HTTPS=True
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=2
EOF
```

#### Step 5: Create Systemd Service Files

Web application service (`/etc/systemd/system/regex-exchange-web.service`):
```ini
[Unit]
Description=Regex Intelligence Exchange Web Application
After=network.target

[Service]
Type=simple
User=regex-exchange
Group=regex-exchange
WorkingDirectory=/opt/regex-exchange/web
EnvironmentFile=/opt/regex-exchange/.env
ExecStart=/opt/regex-exchange/venv/bin/python -m app.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

API service (`/etc/systemd/system/regex-exchange-api.service`):
```ini
[Unit]
Description=Regex Intelligence Exchange RESTful API
After=network.target

[Service]
Type=simple
User=regex-exchange
Group=regex-exchange
WorkingDirectory=/opt/regex-exchange/web
EnvironmentFile=/opt/regex-exchange/.env
ExecStart=/opt/regex-exchange/venv/bin/python -m api.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Step 6: Enable and Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable regex-exchange-web
sudo systemctl enable regex-exchange-api
sudo systemctl start regex-exchange-web
sudo systemctl start regex-exchange-api
```

### 3. Docker Deployment

#### Step 1: Build Docker Images

```bash
# Build web application image
docker build -t regex-exchange-web -f Dockerfile.web .

# Build API image
docker build -t regex-exchange-api -f Dockerfile.api .
```

#### Step 2: Run with Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  web:
    image: regex-exchange-web
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./logs:/app/logs
    depends_on:
      - redis

  api:
    image: regex-exchange-api
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./logs:/app/logs
    depends_on:
      - redis

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

Run the services:
```bash
docker-compose up -d
```

### 4. Nginx Reverse Proxy (Production)

#### Step 1: Install Nginx

```bash
sudo apt-get update
sudo apt-get install nginx
```

#### Step 2: Create Nginx Configuration

Create `/etc/nginx/sites-available/regex-exchange`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /opt/regex-exchange/web/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

server {
    listen 80;
    server_name api.your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Step 3: Enable Site and Restart Nginx

```bash
sudo ln -s /etc/nginx/sites-available/regex-exchange /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. SSL/TLS Configuration with Let's Encrypt

#### Step 1: Install Certbot

```bash
sudo apt-get install certbot python3-certbot-nginx
```

#### Step 2: Obtain SSL Certificates

```bash
sudo certbot --nginx -d your-domain.com -d api.your-domain.com
```

#### Step 3: Test Automatic Renewal

```bash
sudo certbot renew --dry-run
```

## Performance Optimization

### Caching

Redis is used for caching to improve performance:

1. Install Redis:
   ```bash
   sudo apt-get install redis-server
   ```

2. Configure Redis in the application via environment variables:
   ```bash
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=2
   ```

### Static File Serving

In production, serve static files through Nginx instead of the Flask application:

```nginx
location /static/ {
    alias /path/to/static/files/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Gunicorn (Alternative WSGI Server)

For production deployments, consider using Gunicorn instead of the built-in Flask server:

1. Install Gunicorn:
   ```bash
   pip install gunicorn
   ```

2. Run with Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app.app:create_app()
   ```

## Monitoring and Logging

### Log Files

Log files are created in the `logs` directory:

- `app.log` - Main application logs
- `error.log` - Error logs
- `access.log` - Access logs (when using Nginx)

### Health Checks

Monitor application health using the built-in health endpoints:

- Web application: `http://localhost:5000/health`
- API: `http://localhost:5001/api/v1/health`

### System Monitoring

Monitor system resources:

```bash
# Check service status
sudo systemctl status regex-exchange-web
sudo systemctl status regex-exchange-api

# Check logs
sudo journalctl -u regex-exchange-web -f
sudo journalctl -u regex-exchange-api -f

# Monitor system resources
htop
iotop
```

## Backup and Recovery

### Pattern Database Backup

The pattern database is stored in the `patterns` directory. Regular backups should be performed:

```bash
# Create backup
tar -czf patterns-backup-$(date +%Y%m%d).tar.gz ../patterns

# Restore backup
tar -xzf patterns-backup-20250101.tar.gz -C ../
```

### Configuration Backup

Backup configuration files:

```bash
# Backup environment file
cp .env .env.backup

# Backup systemd service files
sudo cp /etc/systemd/system/regex-exchange-*.service /backup/
```

## Troubleshooting

### Common Issues

1. **Application not starting**
   - Check logs in `logs/` directory
   - Verify all dependencies are installed
   - Ensure environment variables are set correctly

2. **Permission errors**
   - Verify file ownership and permissions
   - Check user and group settings in systemd services

3. **Connection errors**
   - Verify Redis is running and accessible
   - Check firewall settings
   - Verify port configurations

### Log Analysis

```bash
# View recent application logs
tail -f logs/app.log

# View error logs
tail -f logs/error.log

# View systemd logs
sudo journalctl -u regex-exchange-web -f
sudo journalctl -u regex-exchange-api -f
```

## Security Considerations

### Secret Management

- Never commit secrets to version control
- Use environment variables for sensitive configuration
- Rotate secrets regularly

### HTTPS Enforcement

- Always use HTTPS in production environments
- Redirect HTTP to HTTPS
- Use strong SSL/TLS configurations

### Input Validation

- All user inputs are sanitized
- ID parameters are validated
- Search queries are sanitized

### Rate Limiting

Consider implementing rate limiting for public endpoints to prevent abuse.

## Scaling

### Horizontal Scaling

- Deploy multiple instances behind a load balancer
- Use shared Redis for caching
- Implement sticky sessions if needed

### Vertical Scaling

- Increase server resources (CPU, RAM)
- Optimize database queries
- Tune application performance settings

This deployment guide provides a comprehensive approach to deploying the Regex Intelligence Exchange in various environments. Adjust the configurations based on your specific requirements and infrastructure.