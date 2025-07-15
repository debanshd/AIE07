#!/usr/bin/env python3
"""
Simple callback server to handle LinkedIn OAuth redirects
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL and query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        print(f"\n=== OAuth Callback Received ===")
        print(f"Full URL: {self.path}")
        print(f"Query parameters: {query_params}")
        
        # Check for authorization code
        if 'code' in query_params:
            auth_code = query_params['code'][0]
            print(f"✅ Authorization code received: {auth_code}")
            
            # Store the code for the main script
            self.server.auth_code = auth_code
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
            <html>
            <body>
            <h2>Authorization Successful!</h2>
            <p>You can close this window and return to the terminal.</p>
            <script>setTimeout(function(){ window.close(); }, 3000);</script>
            </body>
            </html>
            ''')
            
        # Check for errors
        elif 'error' in query_params:
            error = query_params['error'][0]
            error_description = query_params.get('error_description', ['No description'])[0]
            
            print(f"❌ OAuth Error: {error}")
            print(f"❌ Error Description: {error_description}")
            
            # Send error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f'''
            <html>
            <body>
            <h2>Authorization Failed</h2>
            <p><strong>Error:</strong> {error}</p>
            <p><strong>Description:</strong> {error_description}</p>
            <p>Please check the terminal for more details.</p>
            </body>
            </html>
            '''.encode())
            
        else:
            print("❓ Unknown callback received")
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
            <html>
            <body>
            <h2>Unknown Response</h2>
            <p>No authorization code or error found in the callback.</p>
            </body>
            </html>
            ''')
    
    def log_message(self, format, *args):
        # Suppress default HTTP server logs
        pass

def start_callback_server(port=8000):
    """Start the callback server and wait for OAuth response"""
    server = HTTPServer(('localhost', port), CallbackHandler)
    server.auth_code = None
    
    print(f"🚀 Starting callback server on http://localhost:{port}/auth/callback")
    print("Waiting for OAuth callback...")
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for callback (with timeout)
    timeout = 300  # 5 minutes
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if hasattr(server, 'auth_code') and server.auth_code:
            print(f"✅ Received authorization code: {server.auth_code}")
            server.shutdown()
            return server.auth_code
        time.sleep(1)
    
    print("⏰ Timeout waiting for OAuth callback")
    server.shutdown()
    return None

if __name__ == "__main__":
    auth_code = start_callback_server()
    if auth_code:
        print(f"Authorization code: {auth_code}")
    else:
        print("Failed to get authorization code") 