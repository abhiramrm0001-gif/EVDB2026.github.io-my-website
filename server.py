import http.server
import socketserver
import json
import shutil
import os

PORT = 8000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    # This ensures the browser always gets fresh data (disables caching)
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_POST(self):
        if self.path == '/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # Parse the incoming data from the browser
                data = json.loads(post_data.decode('utf-8'))
                
                # 1. Create a backup of the existing data.json if it exists
                if os.path.exists('data.json'):
                    shutil.copy('data.json', 'data_backup.json')
                
                # 2. Overwrite data.json with the new data
                with open('data.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
                
                # Send success response to the browser
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode())
                
                print(">> Success: Data saved and backup created!")
                
            except Exception as e:
                print(f">> Error during save: {e}")
                self.send_error(500, str(e))
        else:
            self.send_error(404)

# Set up the server
socketserver.TCPServer.allow_reuse_address = True
print(f"Server starting at http://localhost:{PORT}")
print("Point your browser to the editor HTML file via this URL.")

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")