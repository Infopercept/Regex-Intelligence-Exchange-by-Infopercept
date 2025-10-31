# Deployment Guide

## Overview

This guide provides instructions for deploying the Regex Intelligence Exchange web interface and RESTful API to production environments.

## Prerequisites

- Python 3.6 or higher
- pip package manager
- Virtual environment tool (recommended)
- Web server (Apache, Nginx, etc.)
- Process manager (Gunicorn, uWSGI, etc.)

## Production Deployment

### 1. Environment Setup

1. Create a dedicated user for the application:
   ```bash
   sudo useradd -r -s /bin/false regex-exchange
   ```

2. Create application directory:
   ```bash
   sudo mkdir -p /opt/regex-exchange
   sudo chown regex-exchange:regex-exchange /opt/regex-exchange
   ```

3. Clone or copy the application:
   ```bash
   sudo -u regex-exchange git clone https://github.com/Infopercept/Regex-Intelligence-Exchange-by-Infopercept.git /opt/regex-exchange
   ```

### 2. Python Environment

1. Create a virtual environment:
   ```bash
   sudo -u regex-exchange python3 -m venv /opt/regex-exchange/venv
   ```

2. Activate the virtual environment:
   ```bash
   sudo -u regex-exchange /opt/regex-exchange/venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   sudo -u regex-exchange pip install -r /opt/regex-exchange/web/requirements.txt
   ```

### 3. Configuration

1. Create production configuration:
   ```bash
   sudo -u regex-exchange cp /opt/regex-exchange/web/config/production.py.example /opt/regex-exchange/web/config/production.py
   ```

2. Update configuration values:
   ```python
   # /opt/regex-exchange/web/config/production.py
   class ProductionConfig:
       DEBUG = False
       SECRET_KEY = 'your-secret-key-here'
       # Add other production-specific settings
   ```

3. Set environment variables:
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY='your-secret-key-here'
   ```

### 4. Web Server Configuration

#### Using Gunicorn

1. Install Gunicorn:
   ```bash
   sudo -u regex-exchange pip install gunicorn
   ```

2. Create Gunicorn configuration for web application:
   ```bash
   # /opt/regex-exchange/gunicorn_web.conf.py
   bind = "127.0.0.1:5000"
   workers = 4
   worker_class = "sync"
   worker_connections = 1000
   timeout = 30
   keepalive = 2
   max_requests = 1000
   max_requests_jitter = 100
   preload_app = True
   ```

3. Create Gunicorn configuration for API:
   ```bash
   # /opt/regex-exchange/gunicorn_api.conf.py
   bind = "127.0.0.1:5001"
   workers = 4
   worker_class = "sync"
   worker_connections = 1000
   timeout = 30
   keepalive = 2
   max_requests = 1000
   max_requests_jitter = 100
   preload_app = True
   ```

#### Using Nginx as Reverse Proxy

1. Install Nginx:
   ```bash
   sudo apt-get install nginx
   ```

2. Create Nginx configuration for web application:
   ```nginx
   # /etc/nginx/sites-available/regex-exchange-web
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
   ```

3. Create Nginx configuration for API:
   ```nginx
   # /etc/nginx/sites-available/regex-exchange-api
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

4. Enable the sites:
   ```bash
   sudo ln -s /etc/nginx/sites-available/regex-exchange-web /etc/nginx/sites-enabled/
   sudo ln -s /etc/nginx/sites-available/regex-exchange-api /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

### 5. Process Management

#### Using systemd

1. Create systemd service for web application:
   ```ini
   # /etc/systemd/system/regex-exchange-web.service
   [Unit]
   Description=Regex Intelligence Exchange Web Application
   After=network.target
   
   [Service]
   Type=simple
   User=regex-exchange
   Group=regex-exchange
   WorkingDirectory=/opt/regex-exchange/web
   Environment=FLASK_ENV=production
   ExecStart=/opt/regex-exchange/venv/bin/gunicorn -c /opt/regex-exchange/gunicorn_web.conf.py app.app:create_app()
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

2. Create systemd service for API:
   ```ini
   # /etc/systemd/system/regex-exchange-api.service
   [Unit]
   Description=Regex Intelligence Exchange RESTful API
   After=network.target
   
   [Service]
   Type=simple
   User=regex-exchange
   Group=regex-exchange
   WorkingDirectory=/opt/regex-exchange/web
   Environment=FLASK_ENV=production
   ExecStart=/opt/regex-exchange/venv/bin/gunicorn -c /opt/regex-exchange/gunicorn_api.conf.py api.app:create_app()
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the services:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable regex-exchange-web
   sudo systemctl enable regex-exchange-api
   sudo systemctl start regex-exchange-web
   sudo systemctl start regex-exchange-api
   ```

### 6. SSL/TLS Configuration

#### Using Let's Encrypt

1. Install Certbot:
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   ```

2. Obtain SSL certificates:
   ```bash
   sudo certbot --nginx -d your-domain.com -d api.your-domain.com
   ```

3. Test automatic renewal:
   ```bash
   sudo certbot renew --dry-run
   ```

### 7. Monitoring and Logging

#### Log Configuration

1. Create log directories:
   ```bash
   sudo mkdir -p /var/log/regex-exchange
   sudo chown regex-exchange:regex-exchange /var/log/regex-exchange
   ```

2. Configure application logging in `config/production.py`:
   ```python
   LOG_LEVEL = 'INFO'
   LOG_FILE = '/var/log/regex-exchange/app.log'
   ```

#### Monitoring

1. Install and configure monitoring tools:
   - **Prometheus** for metrics collection
   - **Grafana** for visualization
   - **Sentry** for error tracking

2. Set up health checks:
   ```bash
   # Web application health check
   curl -f http://localhost:5000/health || exit 1
   
   # API health check
   curl -f http://localhost:5001/api/v1/health || exit 1
   ```

### 8. Backup and Recovery

1. Regular database backups (if using a database):
   ```bash
   # Add to crontab for daily backups
   0 2 * * * /opt/regex-exchange/backup.sh
   ```

2. Backup script example:
   ```bash
   #!/bin/bash
   # /opt/regex-exchange/backup.sh
   BACKUP_DIR="/opt/backups/regex-exchange"
   DATE=$(date +%Y%m%d_%H%M%S)
   
   mkdir -p $BACKUP_DIR/$DATE
   cp -r /opt/regex-exchange/web $BACKUP_DIR/$DATE/
   cp -r /opt/regex-exchange/patterns $BACKUP_DIR/$DATE/
   
   # Keep only last 7 days of backups
   find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} \;
   ```

## Container Deployment

### Docker

1. Create Dockerfile for web application:
   ```dockerfile
   # /opt/regex-exchange/web/Dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 5000
   
   CMD ["gunicorn", "-b", "0.0.0.0:5000", "app.app:create_app()"]
   ```

2. Create Dockerfile for API:
   ```dockerfile
   # /opt/regex-exchange/api/Dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 5001
   
   CMD ["gunicorn", "-b", "0.0.0.0:5001", "api.app:create_app()"]
   ```

3. Create docker-compose.yml:
   ```yaml
   version: '3.8'
   
   services:
     web:
       build: ./web
       ports:
         - "5000:5000"
       environment:
         - FLASK_ENV=production
       volumes:
         - ./patterns:/app/patterns
   
     api:
       build: ./api
       ports:
         - "5001:5001"
       environment:
         - FLASK_ENV=production
       volumes:
         - ./patterns:/app/patterns
   
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
         - ./ssl:/etc/nginx/ssl
       depends_on:
         - web
         - api
   ```

## Security Considerations

1. **Secrets Management**
   - Never commit secrets to version control
   - Use environment variables or secret management tools
   - Rotate secrets regularly

2. **Input Validation**
   - Validate all user inputs
   - Sanitize data before processing
   - Use parameterized queries if using databases

3. **Rate Limiting**
   - Implement rate limiting to prevent abuse
   - Use tools like Nginx or application-level rate limiting

4. **CORS Configuration**
   - Configure CORS properly for API endpoints
   - Restrict origins to trusted domains only

5. **File Uploads**
   - Validate file types and sizes
   - Store uploads outside web root
   - Scan uploaded files for malware

## Performance Optimization

1. **Caching**
   - Implement Redis or Memcached for caching
   - Cache frequently accessed data
   - Use HTTP caching headers

2. **Database Optimization**
   - Use connection pooling
   - Optimize queries
   - Add appropriate indexes

3. **Static Assets**
   - Serve static assets through Nginx
   - Enable compression
   - Use CDN for global distribution

4. **Load Balancing**
   - Use load balancer for high availability
   - Distribute load across multiple instances
   - Implement health checks

## Troubleshooting

### Common Issues

1. **Application not starting**
   - Check logs in `/var/log/regex-exchange/`
   - Verify configuration files
   - Ensure all dependencies are installed

2. **Permission errors**
   - Verify file ownership and permissions
   - Check user and group settings
   - Ensure application user has necessary access

3. **Memory issues**
   - Monitor memory usage
   - Adjust Gunicorn worker settings
   - Consider adding swap space

### Log Analysis

1. Application logs:
   ```bash
   tail -f /var/log/regex-exchange/app.log
   ```

2. System logs:
   ```bash
   journalctl -u regex-exchange-web -f
   journalctl -u regex-exchange-api -f
   ```

3. Nginx logs:
   ```bash
   tail -f /var/log/nginx/access.log
   tail -f /var/log/nginx/error.log
   ```

## Maintenance

### Regular Tasks

1. **Updates**
   - Regularly update dependencies
   - Apply security patches
   - Test updates in staging environment first

2. **Monitoring**
   - Monitor application performance
   - Set up alerts for critical issues
   - Review logs regularly

3. **Backups**
   - Verify backup integrity
   - Test restore procedures
   - Update backup strategies as needed

### Scaling

1. **Horizontal Scaling**
   - Add more application instances
   - Use load balancer to distribute traffic
   - Implement shared session storage

2. **Vertical Scaling**
   - Increase server resources
   - Optimize application performance
   - Tune database settings

This deployment guide provides a comprehensive approach to deploying the Regex Intelligence Exchange web interface and API in production environments. Adjust the configurations based on your specific requirements and infrastructure.