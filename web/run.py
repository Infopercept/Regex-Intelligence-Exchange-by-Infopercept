#!/usr/bin/env python3
"""
Main entry point for Regex Intelligence Exchange web application and API
"""

import os
import sys
import argparse
from api.app import create_app as create_api_app
from app.app import create_app as create_web_app

def main():
    parser = argparse.ArgumentParser(description='Regex Intelligence Exchange Web Application')
    parser.add_argument('--mode', choices=['api', 'web', 'both'], default='both',
                        help='Run mode: api (REST API only), web (web interface only), or both')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--api-port', type=int, default=5001, help='API port (when running both modes)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--env', choices=['development', 'production', 'testing'], 
                        default='development', help='Environment configuration')
    
    args = parser.parse_args()
    
    if args.mode == 'api':
        # Run only the REST API
        api_app = create_api_app(args.env)
        print(f"Starting REST API server on {args.host}:{args.port}")
        api_app.run(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    elif args.mode == 'web':
        # Run only the web interface
        web_app = create_web_app(args.env)
        print(f"Starting web interface on {args.host}:{args.port}")
        web_app.run(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    else:
        # Run both API and web interface
        import threading
        
        # Start API in a separate thread
        def run_api():
            api_app = create_api_app(args.env)
            print(f"Starting REST API server on {args.host}:{args.api_port}")
            api_app.run(
                host=args.host,
                port=args.api_port,
                debug=False  # Disable debug in thread
            )
        
        api_thread = threading.Thread(target=run_api)
        api_thread.daemon = True
        api_thread.start()
        
        # Start web interface in main thread
        web_app = create_web_app(args.env)
        print(f"Starting web interface on {args.host}:{args.port}")
        web_app.run(
            host=args.host,
            port=args.port,
            debug=args.debug
        )

if __name__ == '__main__':
    main()