#!/usr/bin/env python3
"""
Simple script to run real-time integration and add all data in your format
"""

import subprocess
import sys
import os
from pathlib import Path

def run_realtime_integration():
    """Run the real-time integration system to fetch and add all data"""
    print("Starting real-time integration to add all data in your format...")
    
    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        # Run the real-time integration script
        result = subprocess.run([
            'python', 'tools/realtime-integration.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Real-time integration completed successfully!")
            print(result.stdout)
            return True
        else:
            print("Error during real-time integration:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

def run_scheduled_integration():
    """Run integration in scheduled mode (runs continuously)"""
    print("Starting scheduled real-time integration...")
    print("This will run continuously, checking for updates every 24 hours.")
    print("Press Ctrl+C to stop.")
    
    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        # Run the real-time integration script in scheduled mode
        result = subprocess.run([
            'python', 'tools/realtime-integration.py', '--schedule'
        ])
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

def show_integration_stats():
    """Show integration statistics"""
    print("Fetching integration statistics...")
    
    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        # Run the real-time integration script to show stats
        result = subprocess.run([
            'python', 'tools/realtime-integration.py', '--stats'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Integration Statistics:")
            print(result.stdout)
            return True
        else:
            print("Error fetching statistics:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

def main():
    """Main function"""
    print("Regex Intelligence Exchange - Add All Real-Time Data")
    print("=" * 55)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--scheduled':
            run_scheduled_integration()
        elif sys.argv[1] == '--stats':
            show_integration_stats()
        else:
            print("Usage: python add-all-realtime-data.py [--scheduled|--stats]")
            print("  --scheduled: Run in scheduled mode (continuous integration)")
            print("  --stats: Show integration statistics")
            return
    else:
        # Run one-time integration
        success = run_realtime_integration()
        if success:
            print("\nAll data has been added in your format!")
            print("Patterns are stored in the patterns/by-vendor/ directory")
        else:
            print("\nIntegration failed. Check the logs for details.")

if __name__ == '__main__':
    main()