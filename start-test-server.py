#!/usr/bin/env python3
"""
Simple HTTP server to serve the test website and avoid CORS issues
"""
import http.server
import socketserver
import webbrowser
import os

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🚀 Test server running at http://localhost:{PORT}")
        print(f"📱 Open your browser and go to: http://localhost:{PORT}/test-website.html")
        print(f"🛑 Press Ctrl+C to stop the server")
        
        # Auto-open browser
        webbrowser.open(f"http://localhost:{PORT}/test-website.html")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
