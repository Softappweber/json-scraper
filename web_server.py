#!/usr/bin/env python3
"""Web Interface Server"""
import http.server
import json
import threading
from scraper_cli import Scraper, save_contacts

HTML = '''<!DOCTYPE html>
<html>
<head>
<title>Contact Scraper Pro</title>
<style>
body{font-family:Arial;background:#667eea;padding:20px;margin:0}
.container{max-width:800px;margin:0 auto;background:white;padding:30px;border-radius:15px;box-shadow:0 10px 30px rgba(0,0,0,0.3)}
h1{color:#667eea;text-align:center}
textarea{width:100%;height:200px;padding:10px;border:2px solid #ddd;border-radius:8px;font-family:monospace;font-size:14px}
button{background:#667eea;color:white;padding:12px 30px;border:none;border-radius:8px;cursor:pointer;font-size:16px;margin:10px 5px}
button:hover{background:#5a67d8}
#result{margin-top:20px;white-space:pre-wrap;background:#f5f5f5;padding:15px;border-radius:8px;font-family:monospace;font-size:12px;max-height:400px;overflow-y:auto}
</style>
</head>
<body>
<div class="container">
<h1>🚀 Contact Scraper Pro</h1>
<p>Enter URLs (one per line):</p>
<textarea id="urls" placeholder="https://example.com/contact\nhttps://another-site.com/about"></textarea>
<br>
<button onclick="scrape()">🚀 Start Scraping</button>
<div id="result"></div>
</div>
<script>
async function scrape(){
    const urls=document.getElementById('urls').value.split('\\n').filter(u=>u.trim());
    document.getElementById('result').textContent='Scraping...';
    const res=await fetch('/scrape',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({urls:urls})});
    const data=await res.json();
    document.getElementById('result').textContent=JSON.stringify(data,null,2);
}
</script>
</body>
</html>'''

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/scrape':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            urls = data.get('urls', [])
            
            scraper = Scraper()
            contacts = scraper.scrape(urls, max_contacts=300, max_depth=3, delay=1)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'count': len(contacts), 'contacts': contacts}).encode())
    
    def log_message(self, format, *args):
        pass

def run_server(port=8000):
    print(f'\nStarting web server at http://localhost:{port}')
    print('Press Ctrl+C to stop')
    server = http.server.HTTPServer(('localhost', port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped')
