"""
HTTP Request Tool - Simple API tester
"""
import urllib.request
import urllib.parse
import json

class HTTPClient:
    """Simple HTTP client for API testing"""
    
    @staticmethod
    def make_request(url, method='GET', headers=None, body=None, timeout=30):
        """Make HTTP request"""
        try:
            # Prepare request
            if headers is None:
                headers = {}
            
            # Add default headers
            if 'User-Agent' not in headers:
                headers['User-Agent'] = 'CipherV4-HTTPClient'
            
            # Prepare body
            data = None
            if body and method in ['POST', 'PUT', 'PATCH']:
                data = body.encode('utf-8')
                if 'Content-Type' not in headers:
                    headers['Content-Type'] = 'application/json'
            
            # Create request
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            
            # Make request
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status = response.status
                response_headers = dict(response.headers)
                response_body = response.read().decode('utf-8')
                
                # Try to parse JSON
                try:
                    response_body = json.loads(response_body)
                    response_body = json.dumps(response_body, indent=2)
                except:
                    pass
                
                return {
                    'success': True,
                    'status': status,
                    'headers': response_headers,
                    'body': response_body
                }
        
        except urllib.error.HTTPError as e:
            return {
                'success': False,
                'status': e.code,
                'error': f"HTTP {e.code}: {e.reason}",
                'body': e.read().decode('utf-8') if e.fp else None
            }
        except Exception as e:
            return {
                'success': False,
                'status': 0,
                'error': str(e),
                'body': None
            }
