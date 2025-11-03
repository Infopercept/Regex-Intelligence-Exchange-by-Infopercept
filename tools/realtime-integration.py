#!/usr/bin/env python3
"""
Real-time integration system for continuously fetching and integrating pattern data
from all available regex tools and databases
"""

import os
import re
import json
import time
import subprocess
import requests
from pathlib import Path
from datetime import datetime
import threading
import sys

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules with error handling
try:
    import schedule
except ImportError:
    print("schedule module not found. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "schedule"])
    import schedule

try:
    from enhanced_import_manager import EnhancedImportManager
except ImportError:
    print("enhanced_import_manager module not found")
    EnhancedImportManager = None

class RealTimeIntegrationSystem:
    """Real-time integration system for pattern data sources"""
    
    def __init__(self, config_file='config/integration_config.json'):
        self.config_file = config_file
        self.config = self._load_config()
        self.last_run_timestamp = {}
        self.integration_stats = {
            'whatweb': {'last_run': None, 'patterns_added': 0, 'errors': 0},
            'wappalyzer': {'last_run': None, 'patterns_added': 0, 'errors': 0},
            'webtech': {'last_run': None, 'patterns_added': 0, 'errors': 0}
        }
        # Initialize the enhanced import manager if available
        if EnhancedImportManager:
            self.import_manager = EnhancedImportManager(self.config.get('patterns_output_dir', 'patterns/by-vendor'))
        else:
            self.import_manager = None
    
    def _load_config(self):
        """Load integration configuration"""
        default_config = {
            "sources": {
                "whatweb": {
                    "enabled": True,
                    "repo_url": "https://github.com/urbanadventurer/WhatWeb.git",
                    "local_path": "external/whatweb-repo",
                    "update_interval_hours": 24,
                    "import_script": "tools/extract-whatweb-patterns.py"
                },
                "wappalyzer": {
                    "enabled": True,
                    "repo_url": "https://github.com/tomnomnom/wappalyzer.git",
                    "local_path": "external/wappalyzer-repo",
                    "update_interval_hours": 24,
                    "import_script": "tools/import-wappalyzer.py"
                },
                "webtech": {
                    "enabled": True,
                    "repo_url": "https://github.com/ShielderSec/webtech.git",
                    "local_path": "external/webtech-repo",
                    "update_interval_hours": 24,
                    "import_script": "tools/import-webtech.py"
                }
            },
            "patterns_output_dir": "patterns/by-vendor",
            "log_file": "logs/integration.log",
            "max_workers": 3
        }
        
        # Create config directory if it doesn't exist
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        # Create log directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        config_path = Path(self.config_file)
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Merge with default config
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
        else:
            # Save default config
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def _log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        # Also write to log file
        with open(self.config.get('log_file', 'logs/integration.log'), 'a') as f:
            f.write(log_message + '\n')
    
    def _clone_or_update_repo(self, source_name, repo_url, local_path):
        """Clone or update a git repository"""
        try:
            local_path_obj = Path(local_path)
            
            if local_path_obj.exists():
                # Update existing repository
                self._log(f"Updating {source_name} repository...")
                result = subprocess.run(
                    ['git', 'pull'], 
                    cwd=local_path, 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    self._log(f"Successfully updated {source_name} repository")
                else:
                    self._log(f"Failed to update {source_name} repository: {result.stderr}", "ERROR")
                    return False
            else:
                # Clone new repository
                self._log(f"Cloning {source_name} repository...")
                result = subprocess.run(
                    ['git', 'clone', repo_url, local_path], 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    self._log(f"Successfully cloned {source_name} repository")
                else:
                    self._log(f"Failed to clone {source_name} repository: {result.stderr}", "ERROR")
                    return False
            
            return True
        except Exception as e:
            self._log(f"Error with {source_name} repository: {str(e)}", "ERROR")
            return False
    
    def _count_patterns_before_after(self, patterns_dir):
        """Count patterns before and after import"""
        pattern_files = list(Path(patterns_dir).rglob('*.json'))
        return len(pattern_files)
    
    def _import_whatweb_patterns(self):
        """Import patterns from WhatWeb"""
        source_config = self.config['sources']['whatweb']
        if not source_config['enabled']:
            return True
        
        try:
            self._log("Starting WhatWeb pattern import...")
            
            # Count patterns before import
            patterns_before = self._count_patterns_before_after(self.config['patterns_output_dir'])
            
            # Run the import script - fix path resolution
            script_path = source_config['import_script']
            # Convert tools/script.py to ./script.py when running from tools directory
            if script_path.startswith('tools/'):
                script_path = './' + script_path[6:]  # Remove 'tools/' prefix
            result = subprocess.run(
                ['python', script_path], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                # Count patterns after import
                patterns_after = self._count_patterns_before_after(self.config['patterns_output_dir'])
                new_patterns = patterns_after - patterns_before
                
                self.integration_stats['whatweb']['last_run'] = datetime.now().isoformat()
                self.integration_stats['whatweb']['patterns_added'] += new_patterns
                self._log(f"Successfully imported WhatWeb patterns. Added {new_patterns} new patterns.")
                return True
            else:
                self.integration_stats['whatweb']['errors'] += 1
                self._log(f"Failed to import WhatWeb patterns: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.integration_stats['whatweb']['errors'] += 1
            self._log(f"Error importing WhatWeb patterns: {str(e)}", "ERROR")
            return False
    
    def _import_wappalyzer_patterns(self):
        """Import patterns from Wappalyzer"""
        source_config = self.config['sources']['wappalyzer']
        if not source_config['enabled']:
            return True
        
        try:
            self._log("Starting Wappalyzer pattern import...")
            
            # Count patterns before import
            patterns_before = self._count_patterns_before_after(self.config['patterns_output_dir'])
            
            # Run the import script - fix path resolution
            script_path = source_config['import_script']
            # Convert tools/script.py to ./script.py when running from tools directory
            if script_path.startswith('tools/'):
                script_path = './' + script_path[6:]  # Remove 'tools/' prefix
            result = subprocess.run(
                ['python', script_path], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                # Count patterns after import
                patterns_after = self._count_patterns_before_after(self.config['patterns_output_dir'])
                new_patterns = patterns_after - patterns_before
                
                self.integration_stats['wappalyzer']['last_run'] = datetime.now().isoformat()
                self.integration_stats['wappalyzer']['patterns_added'] += new_patterns
                self._log(f"Successfully imported Wappalyzer patterns. Added {new_patterns} new patterns.")
                return True
            else:
                self.integration_stats['wappalyzer']['errors'] += 1
                self._log(f"Failed to import Wappalyzer patterns: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.integration_stats['wappalyzer']['errors'] += 1
            self._log(f"Error importing Wappalyzer patterns: {str(e)}", "ERROR")
            return False
    
    def _import_webtech_patterns(self):
        """Import patterns from WebTech"""
        source_config = self.config['sources']['webtech']
        if not source_config['enabled']:
            return True
        
        try:
            self._log("Starting WebTech pattern import...")
            
            # Count patterns before import
            patterns_before = self._count_patterns_before_after(self.config['patterns_output_dir'])
            
            # Run the import script - fix path resolution
            script_path = source_config['import_script']
            # Convert tools/script.py to ./script.py when running from tools directory
            if script_path.startswith('tools/'):
                script_path = './' + script_path[6:]  # Remove 'tools/' prefix
            result = subprocess.run(
                ['python', script_path], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                # Count patterns after import
                patterns_after = self._count_patterns_before_after(self.config['patterns_output_dir'])
                new_patterns = patterns_after - patterns_before
                
                self.integration_stats['webtech']['last_run'] = datetime.now().isoformat()
                self.integration_stats['webtech']['patterns_added'] += new_patterns
                self._log(f"Successfully imported WebTech patterns. Added {new_patterns} new patterns.")
                return True
            else:
                self.integration_stats['webtech']['errors'] += 1
                self._log(f"Failed to import WebTech patterns: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.integration_stats['webtech']['errors'] += 1
            self._log(f"Error importing WebTech patterns: {str(e)}", "ERROR")
            return False
    
    def _standardize_patterns(self):
        """Run pattern standardization on all patterns"""
        try:
            self._log("Running pattern standardization...")
            script_path = 'tools/standardize-patterns.py'
            # Convert tools/script.py to ./script.py when running from tools directory
            if script_path.startswith('tools/'):
                script_path = './' + script_path[6:]  # Remove 'tools/' prefix
            result = subprocess.run(
                ['python', script_path], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                self._log("Pattern standardization completed successfully")
                return True
            else:
                self._log(f"Pattern standardization failed: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self._log(f"Error during pattern standardization: {str(e)}", "ERROR")
            return False
    
    def _validate_patterns(self):
        """Run pattern validation on all patterns"""
        try:
            self._log("Running pattern validation...")
            script_path = 'tools/validate-all-patterns.py'
            # Convert tools/script.py to ./script.py when running from tools directory
            if script_path.startswith('tools/'):
                script_path = './' + script_path[6:]  # Remove 'tools/' prefix
            result = subprocess.run(
                ['python', script_path], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                self._log("Pattern validation completed successfully")
                return True
            else:
                self._log(f"Pattern validation failed: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self._log(f"Error during pattern validation: {str(e)}", "ERROR")
            return False
    
    def integrate_all_sources(self):
        """Integrate patterns from all enabled sources"""
        self._log("Starting real-time integration of all pattern sources...")
        
        # Update repositories and import patterns
        success_count = 0
        total_sources = 0
        
        # WhatWeb integration
        source_config = self.config['sources']['whatweb']
        if source_config['enabled']:
            total_sources += 1
            if self._clone_or_update_repo(
                'WhatWeb', 
                source_config['repo_url'], 
                source_config['local_path']
            ):
                if self._import_whatweb_patterns():
                    success_count += 1
        
        # Wappalyzer integration
        source_config = self.config['sources']['wappalyzer']
        if source_config['enabled']:
            total_sources += 1
            if self._clone_or_update_repo(
                'Wappalyzer', 
                source_config['repo_url'], 
                source_config['local_path']
            ):
                if self._import_wappalyzer_patterns():
                    success_count += 1
        
        # WebTech integration
        source_config = self.config['sources']['webtech']
        if source_config['enabled']:
            total_sources += 1
            if self._clone_or_update_repo(
                'WebTech', 
                source_config['repo_url'], 
                source_config['local_path']
            ):
                if self._import_webtech_patterns():
                    success_count += 1
        
        # Run standardization and validation
        if success_count > 0:
            self._standardize_patterns()
            self._validate_patterns()
        
        self._log(f"Integration completed. {success_count}/{total_sources} sources processed successfully.")
        return success_count == total_sources
    
    def schedule_integration(self):
        """Schedule regular integration runs"""
        self._log("Setting up scheduled integration...")
        
        # Schedule integration to run every 24 hours
        schedule.every(24).hours.do(self.integrate_all_sources)
        
        # Also run immediately
        self.integrate_all_sources()
        
        self._log("Scheduled integration started. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self._log("Scheduled integration stopped by user.")
    
    def get_integration_stats(self):
        """Get integration statistics"""
        return self.integration_stats

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time integration system for pattern data sources')
    parser.add_argument('--schedule', action='store_true', help='Run in scheduled mode')
    parser.add_argument('--stats', action='store_true', help='Show integration statistics')
    parser.add_argument('--config', default='config/integration_config.json', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Create integration system
    integration_system = RealTimeIntegrationSystem(args.config)
    
    if args.stats:
        # Show statistics
        stats = integration_system.get_integration_stats()
        print(json.dumps(stats, indent=2))
    elif args.schedule:
        # Run in scheduled mode
        integration_system.schedule_integration()
    else:
        # Run once
        integration_system.integrate_all_sources()

if __name__ == '__main__':
    main()