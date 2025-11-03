#!/usr/bin/env python3
"""
Main entry point for Regex Intelligence Exchange
Cross-platform compatible with modern structure
"""

import sys
import os
import argparse
import logging

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main entry point with enhanced command line interface."""
    parser = argparse.ArgumentParser(
        description='Regex Intelligence Exchange - Technology Pattern Analysis Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Run web interface
  python main.py --mode api                # Run API only
  python main.py --mode both               # Run both web and API
  python main.py --host 0.0.0.0 --port 8080 # Run on specific host/port
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['web', 'api', 'both'], 
        default='web',
        help='Run mode: web interface, API only, or both (default: web)'
    )
    
    parser.add_argument(
        '--host', 
        default='127.0.0.1', 
        help='Host to bind to (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port', 
        type=int, 
        default=5000, 
        help='Port to bind to (default: 5000)'
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Enable debug mode'
    )
    
    parser.add_argument(
        '--api-port', 
        type=int, 
        default=5001, 
        help='API port (when running in "both" mode, default: 5001)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'web':
            # Import and run web application
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web'))
            from app import create_app
            app = create_app()
            print(f"🚀 Starting Regex Intelligence Exchange Web Interface")
            print(f"🌍 Access at: http://{args.host}:{args.port}")
            print(f"📚 API Docs: http://{args.host}:{args.port}/api/docs/")
            app.run(host=args.host, port=args.port, debug=args.debug)
            
        elif args.mode == 'api':
            # Import and run API application
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web'))
            from api.app import create_app
            app = create_app()
            print(f"🚀 Starting Regex Intelligence Exchange API")
            print(f"🌍 Access at: http://{args.host}:{args.port}/api/v1/")
            print(f"📚 API Docs: http://{args.host}:{args.port}/api/docs/")
            app.run(host=args.host, port=args.port, debug=args.debug)
            
        elif args.mode == 'both':
            # Run both web and API applications
            import threading
            
            # Start web application in a separate thread
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web'))
            from app import create_app as create_web_app
            web_app = create_web_app()
            
            def run_web():
                web_app.run(host=args.host, port=args.port, debug=False)
            
            web_thread = threading.Thread(target=run_web)
            web_thread.daemon = True
            web_thread.start()
            
            print(f"🚀 Starting Regex Intelligence Exchange (Web + API)")
            print(f"🌍 Web Interface: http://{args.host}:{args.port}")
            print(f"🌍 API Endpoint: http://{args.host}:{args.api_port}/api/v1/")
            print(f"📚 API Docs: http://{args.host}:{args.api_port}/api/docs/")
            
            # Run API application in main thread
            from api.app import create_app as create_api_app
            api_app = create_api_app()
            api_app.run(host=args.host, port=args.api_port, debug=args.debug)
            
    except ImportError as e:
        print(f"❌ Failed to import application modules: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()