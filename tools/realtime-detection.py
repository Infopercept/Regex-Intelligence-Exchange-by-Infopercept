#!/usr/bin/env python3
"""
Real-Time Detection for Regex Intelligence Exchange
"""

import json
import os
import sys
import re
import time
import threading
from datetime import datetime
from queue import Queue, Empty
import socket


class RealTimeDetector:
    """Real-time pattern detection engine."""
    
    def __init__(self, patterns_dir="patterns/by-vendor"):
        self.patterns = []
        self.running = False
        self.detection_queue = Queue()
        self.results_queue = Queue()
        self.load_patterns(patterns_dir)
    
    def load_patterns(self, patterns_dir):
        """Load all patterns into memory."""
        print("Loading patterns...")
        pattern_count = 0
        
        for root, dirs, files in os.walk(patterns_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            pattern_data = json.load(f)
                        
                        vendor = pattern_data.get('vendor', 'Unknown')
                        product = pattern_data.get('product', 'Unknown')
                        
                        # Compile all regex patterns for faster matching
                        if 'all_versions' in pattern_data:
                            for pattern in pattern_data['all_versions']:
                                if 'pattern' in pattern:
                                    try:
                                        compiled_regex = re.compile(pattern['pattern'])
                                        self.patterns.append({
                                            'vendor': vendor,
                                            'product': product,
                                            'name': pattern.get('name', 'Unknown'),
                                            'regex': compiled_regex,
                                            'version_group': pattern.get('version_group', 0),
                                            'confidence': pattern.get('confidence', 0.5)
                                        })
                                        pattern_count += 1
                                    except re.error as e:
                                        print(f"Error compiling pattern in {file_path}: {e}")
                        
                        if 'versions' in pattern_data:
                            for version_patterns in pattern_data['versions'].values():
                                for pattern in version_patterns:
                                    if 'pattern' in pattern:
                                        try:
                                            compiled_regex = re.compile(pattern['pattern'])
                                            self.patterns.append({
                                                'vendor': vendor,
                                                'product': product,
                                                'name': pattern.get('name', 'Unknown'),
                                                'regex': compiled_regex,
                                                'version_group': pattern.get('version_group', 0),
                                                'confidence': pattern.get('confidence', 0.5)
                                            })
                                            pattern_count += 1
                                        except re.error as e:
                                            print(f"Error compiling pattern in {file_path}: {e}")
                    
                    except Exception as e:
                        print(f"Error loading {file_path}: {e}")
        
        print(f"Loaded {pattern_count} patterns for real-time detection")
    
    def detect_patterns(self, text):
        """Detect patterns in text."""
        matches = []
        
        for pattern in self.patterns:
            match = pattern['regex'].search(text)
            if match:
                version = None
                if pattern['version_group'] > 0 and pattern['version_group'] <= len(match.groups()):
                    version = match.group(pattern['version_group'])
                
                matches.append({
                    'vendor': pattern['vendor'],
                    'product': pattern['product'],
                    'pattern_name': pattern['name'],
                    'matched_text': match.group(0),
                    'version': version,
                    'confidence': pattern['confidence'],
                    'timestamp': datetime.now().isoformat()
                })
        
        return matches
    
    def process_detection_queue(self):
        """Process items in the detection queue."""
        while self.running:
            try:
                # Get item from queue with timeout
                item = self.detection_queue.get(timeout=1)
                
                if item['type'] == 'text':
                    # Detect patterns in text
                    matches = self.detect_patterns(item['data'])
                    if matches:
                        self.results_queue.put({
                            'type': 'matches',
                            'data': matches,
                            'source': item.get('source', 'unknown')
                        })
                
                elif item['type'] == 'http_request':
                    # Simulate HTTP request processing
                    # In a real implementation, this would capture actual HTTP traffic
                    request_data = item['data']
                    # For demo, we'll just detect patterns in the request data
                    matches = self.detect_patterns(str(request_data))
                    if matches:
                        self.results_queue.put({
                            'type': 'http_matches',
                            'data': matches,
                            'source': item.get('source', 'http')
                        })
                
                # Mark task as done
                self.detection_queue.task_done()
                
            except Empty:
                # No items in queue, continue loop
                continue
            except Exception as e:
                print(f"Error processing detection queue: {e}")
    
    def start_detection(self):
        """Start the real-time detection engine."""
        if self.running:
            return
        
        self.running = True
        
        # Start detection thread
        self.detection_thread = threading.Thread(target=self.process_detection_queue)
        self.detection_thread.daemon = True
        self.detection_thread.start()
        
        print("Real-time detection engine started")
    
    def stop_detection(self):
        """Stop the real-time detection engine."""
        self.running = False
        if hasattr(self, 'detection_thread'):
            self.detection_thread.join(timeout=2)
        print("Real-time detection engine stopped")
    
    def submit_text_for_detection(self, text, source="manual"):
        """Submit text for real-time detection."""
        self.detection_queue.put({
            'type': 'text',
            'data': text,
            'source': source
        })
    
    def submit_http_request_for_detection(self, request_data, source="http"):
        """Submit HTTP request data for real-time detection."""
        self.detection_queue.put({
            'type': 'http_request',
            'data': request_data,
            'source': source
        })
    
    def get_detection_results(self, timeout=1):
        """Get detection results."""
        try:
            result = self.results_queue.get(timeout=timeout)
            self.results_queue.task_done()
            return result
        except Empty:
            return None


def simulate_http_traffic(detector, duration=30):
    """Simulate HTTP traffic for demonstration."""
    print(f"Simulating HTTP traffic for {duration} seconds...")
    
    # Sample HTTP responses to detect
    sample_responses = [
        "HTTP/1.1 200 OK\r\nServer: Apache/2.4.41 (Ubuntu)\r\nContent-Type: text/html\r\n\r\n<html>",
        "HTTP/1.1 200 OK\r\nServer: nginx/1.18.0\r\nContent-Type: text/html\r\n\r\n<html>",
        "HTTP/1.1 200 OK\r\nX-Powered-By: PHP/7.4.3\r\nContent-Type: text/html\r\n\r\n<html>",
        "HTTP/1.1 200 OK\r\nServer: Microsoft-IIS/10.0\r\nContent-Type: text/html\r\n\r\n<html>",
    ]
    
    start_time = time.time()
    while time.time() - start_time < duration:
        # Submit random sample response
        response = sample_responses[int(time.time()) % len(sample_responses)]
        detector.submit_http_request_for_detection(response, "simulated_http")
        
        # Wait a bit between requests
        time.sleep(2)
    
    print("HTTP traffic simulation completed")


def monitor_results(detector):
    """Monitor and display detection results."""
    print("Monitoring detection results (Press Ctrl+C to stop)...")
    
    try:
        while True:
            result = detector.get_detection_results(timeout=1)
            if result:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Detection Result:")
                print(f"  Type: {result['type']}")
                print(f"  Source: {result['source']}")
                
                for match in result['data']:
                    print(f"  - {match['vendor']} {match['product']}")
                    print(f"    Pattern: {match['pattern_name']}")
                    print(f"    Version: {match['version']}")
                    print(f"    Confidence: {match['confidence']}")
                    print(f"    Matched: {match['matched_text'][:50]}...")
                print()
            
            # Small delay to prevent busy waiting
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping result monitoring...")


def main():
    """Main function."""
    print("Real-Time Detection for Regex Intelligence Exchange")
    print("=" * 50)
    
    # Create detector
    detector = RealTimeDetector()
    
    # Start detection engine
    detector.start_detection()
    
    # Start result monitoring in separate thread
    monitor_thread = threading.Thread(target=monitor_results, args=(detector,))
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Simulate some detections
    print("\nSubmitting sample text for detection...")
    sample_texts = [
        "Server: Apache/2.4.41 (Ubuntu)",
        "X-Powered-By: PHP/7.4.3",
        "Server: nginx/1.18.0",
        "Microsoft-IIS/10.0"
    ]
    
    for text in sample_texts:
        detector.submit_text_for_detection(text, "sample")
        time.sleep(1)
    
    # Simulate HTTP traffic
    simulate_http_traffic(detector, duration=10)
    
    # Wait a bit for processing to complete
    time.sleep(3)
    
    # Stop detection engine
    detector.stop_detection()
    
    print("\nReal-time detection demo completed")


if __name__ == "__main__":
    main()