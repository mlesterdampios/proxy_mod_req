import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import warnings
import random
import string

# Setup random User-Agent generator
software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value, SoftwareName.SAFARI.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MACOS.value]

user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

def generate_random_string():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=5))

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request('GET')
    
    def do_POST(self):
        self.handle_request('POST')
    
    def do_PUT(self):
        self.handle_request('PUT')
    
    def do_DELETE(self):
        self.handle_request('DELETE')
    
    def do_HEAD(self):
        self.handle_request('HEAD')
    
    def do_OPTIONS(self):
        self.handle_request('OPTIONS')
    
    def handle_request(self, method):
        # Parse the original request URL
        parsed_url = urllib.parse.urlparse(self.path)
        if not parsed_url.netloc:
            self.send_error(400, "Bad Request: Absolute URL required")
            return
        
        # Change scheme to HTTPS
        target_url = urllib.parse.urlunparse((
            'https', 
            parsed_url.netloc, 
            parsed_url.path, 
            parsed_url.params, 
            parsed_url.query, 
            parsed_url.fragment
        ))
        
        # Generate random User-Agent and set headers
        headers = {key: self.headers[key] for key in self.headers}
        headers['User-Agent'] = user_agent_rotator.get_random_user_agent() + " " + generate_random_string()
        headers['Accept-Encoding'] = 'identity'  # Prevent compressed responses
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None
        
        # Configure upstream proxy and SSL verification
        proxies = {
            'http': 'http://localhost:8081',
            'https': 'http://localhost:8081'
        }
        
        # Suppress SSL warnings
        requests.packages.urllib3.disable_warnings()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                response = requests.request(
                    method,
                    target_url,
                    headers=headers,
                    data=body,
                    proxies=proxies,
                    verify=False
                )
            except Exception as e:
                self.send_error(500, f"Internal Server Error: {str(e)}")
                return
        
        # Send response back to client
        self.send_response(response.status_code)
        
        # Filter out hop-by-hop headers
        hop_by_hop = {
            'connection', 'keep-alive', 'proxy-authenticate',
            'proxy-authorization', 'te', 'trailer', 'transfer-encoding', 'upgrade'
        }
        for key, value in response.headers.items():
            if key.lower() in hop_by_hop:
                continue
            self.send_header(key, value)
        
        # Set Content-Length header based on actual content length
        content_length = len(response.content)
        self.send_header('Content-Length', str(content_length))
        self.end_headers()
        self.wfile.write(response.content)

def run(server_class=HTTPServer, handler_class=ProxyHandler, port=9090):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting proxy server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()