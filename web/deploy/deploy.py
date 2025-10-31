#!/usr/bin/env python3
"""
Deployment script for Regex Intelligence Exchange.
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path
from deploy.config import deploy_config

class Deployer:
    """Handles deployment of the web application."""
    
    def __init__(self, environment: str = 'development'):
        self.environment = environment
        self.config = deploy_config.get_config(environment)
        self.project_root = Path(__file__).parent.parent
        self.deploy_dir = self.project_root / 'deploy' / environment
    
    def setup_directories(self):
        """Create deployment directories."""
        print(f"Setting up directories for {self.environment} environment...")
        
        # Create deployment directory
        self.deploy_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logs directory
        (self.deploy_dir / 'logs').mkdir(exist_ok=True)
        
        # Create static files directory
        (self.deploy_dir / 'static').mkdir(exist_ok=True)
        
        print(f"Directories created at {self.deploy_dir}")
    
    def copy_files(self):
        """Copy application files to deployment directory."""
        print("Copying application files...")
        
        # Copy main application files
        files_to_copy = [
            'app/app.py',
            'api/app.py',
            'requirements.txt',
            'requirements-dev.txt'
        ]
        
        for file_path in files_to_copy:
            src = self.project_root / file_path
            dst = self.deploy_dir / file_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.exists():
                shutil.copy2(src, dst)
                print(f"Copied {file_path}")
        
        # Copy directories
        dirs_to_copy = [
            'app',
            'api',
            'config',
            'models',
            'services',
            'utils',
            'templates',
            'static'
        ]
        
        for dir_name in dirs_to_copy:
            src = self.project_root / dir_name
            dst = self.deploy_dir / dir_name
            if src.exists():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print(f"Copied directory {dir_name}")
    
    def install_dependencies(self):
        """Install Python dependencies."""
        print("Installing dependencies...")
        
        requirements_file = self.deploy_dir / 'requirements.txt'
        if requirements_file.exists():
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', '-r', 
                    str(requirements_file)
                ])
                print("Dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"Error installing dependencies: {e}")
                return False
        else:
            print("No requirements.txt found")
        
        return True
    
    def create_environment_file(self):
        """Create environment configuration file."""
        print("Creating environment configuration...")
        
        env_file = self.deploy_dir / '.env'
        with open(env_file, 'w') as f:
            f.write(f"FLASK_ENV={self.environment}\n")
            f.write(f"DEBUG={self.config['debug']}\n")
            f.write(f"HOST={self.config['host']}\n")
            f.write(f"PORT={self.config['port']}\n")
            f.write(f"API_PORT={self.config['api_port']}\n")
            f.write(f"LOG_LEVEL={self.config['log_level']}\n")
            f.write(f"REQUIRE_HTTPS={self.config['require_https']}\n")
            f.write(f"REDIS_HOST={self.config['redis_host']}\n")
            f.write(f"REDIS_PORT={self.config['redis_port']}\n")
            f.write(f"REDIS_DB={self.config['redis_db']}\n")
        
        print(f"Environment file created at {env_file}")
    
    def create_systemd_service(self):
        """Create systemd service files for production."""
        if self.environment != 'production':
            print("Systemd services only created for production environment")
            return
        
        print("Creating systemd service files...")
        
        # Web application service
        web_service_content = f"""[Unit]
Description=Regex Intelligence Exchange Web Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory={self.deploy_dir}
Environment=FLASK_ENV=production
ExecStart={sys.executable} -m app.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        web_service_file = self.deploy_dir / 'regex-exchange-web.service'
        with open(web_service_file, 'w') as f:
            f.write(web_service_content)
        
        # API service
        api_service_content = f"""[Unit]
Description=Regex Intelligence Exchange RESTful API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory={self.deploy_dir}
Environment=FLASK_ENV=production
ExecStart={sys.executable} -m api.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        api_service_file = self.deploy_dir / 'regex-exchange-api.service'
        with open(api_service_file, 'w') as f:
            f.write(api_service_content)
        
        print("Systemd service files created")
        print("To install services, copy them to /etc/systemd/system/ and run:")
        print("sudo systemctl daemon-reload")
        print("sudo systemctl enable regex-exchange-web")
        print("sudo systemctl enable regex-exchange-api")
        print("sudo systemctl start regex-exchange-web")
        print("sudo systemctl start regex-exchange-api")
    
    def create_nginx_config(self):
        """Create Nginx configuration."""
        if self.environment != 'production':
            print("Nginx config only created for production environment")
            return
        
        print("Creating Nginx configuration...")
        
        nginx_config = f"""server {{
    listen 80;
    server_name your-domain.com;
    
    location / {{
        proxy_pass http://127.0.0.1:{self.config['port']};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    location /static/ {{
        alias {self.deploy_dir}/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
}}

server {{
    listen 80;
    server_name api.your-domain.com;
    
    location / {{
        proxy_pass http://127.0.0.1:{self.config['api_port']};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
        
        nginx_file = self.deploy_dir / 'nginx.conf'
        with open(nginx_file, 'w') as f:
            f.write(nginx_config)
        
        print(f"Nginx configuration created at {nginx_file}")
        print("To use this configuration, copy it to /etc/nginx/sites-available/")
        print("and create a symlink to /etc/nginx/sites-enabled/")
    
    def create_docker_files(self):
        """Create Docker configuration files."""
        print("Creating Docker configuration files...")
        
        # Web application Dockerfile
        web_dockerfile = """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "-m", "app.app"]
"""
        
        web_docker_file = self.deploy_dir / 'Dockerfile.web'
        with open(web_docker_file, 'w') as f:
            f.write(web_dockerfile)
        
        # API Dockerfile
        api_dockerfile = """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "-m", "api.app"]
"""
        
        api_docker_file = self.deploy_dir / 'Dockerfile.api'
        with open(api_docker_file, 'w') as f:
            f.write(api_dockerfile)
        
        # Docker Compose file
        docker_compose = """version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.web
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./logs:/app/logs
    depends_on:
      - redis

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
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
"""
        
        docker_compose_file = self.deploy_dir / 'docker-compose.yml'
        with open(docker_compose_file, 'w') as f:
            f.write(docker_compose)
        
        print("Docker configuration files created")
        print("To run with Docker, use: docker-compose up -d")
    
    def validate_deployment(self):
        """Validate the deployment setup."""
        print("Validating deployment...")
        
        # Check if required files exist
        required_files = [
            'app/app.py',
            'api/app.py',
            'requirements.txt',
            'config/production.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.deploy_dir / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"Missing required files: {missing_files}")
            return False
        
        # Check if dependencies can be imported
        try:
            sys.path.insert(0, str(self.deploy_dir))
            import app.app
            import api.app
            print("Dependencies validated successfully")
            return True
        except ImportError as e:
            print(f"Import error: {e}")
            return False
    
    def deploy(self):
        """Execute full deployment process."""
        print(f"Starting deployment for {self.environment} environment...")
        
        try:
            self.setup_directories()
            self.copy_files()
            self.create_environment_file()
            self.install_dependencies()
            self.create_systemd_service()
            self.create_nginx_config()
            self.create_docker_files()
            
            if self.validate_deployment():
                print(f"Deployment completed successfully for {self.environment} environment!")
                print(f"Deployment files are located at: {self.deploy_dir}")
                return True
            else:
                print("Deployment validation failed!")
                return False
                
        except Exception as e:
            print(f"Deployment failed: {e}")
            return False

def main():
    """Main entry point for deployment script."""
    parser = argparse.ArgumentParser(description='Deploy Regex Intelligence Exchange')
    parser.add_argument(
        'environment',
        choices=['development', 'staging', 'production'],
        default='development',
        help='Deployment environment'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate existing deployment'
    )
    
    args = parser.parse_args()
    
    deployer = Deployer(args.environment)
    
    if args.validate_only:
        if deployer.validate_deployment():
            print("Deployment validation successful!")
        else:
            print("Deployment validation failed!")
            sys.exit(1)
    else:
        if not deployer.deploy():
            sys.exit(1)

if __name__ == '__main__':
    main()