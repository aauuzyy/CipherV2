"""
Update Checker - Check GitHub for new versions
"""
import urllib.request
import json
import re
from packaging import version

class UpdateChecker:
    def __init__(self, repo_owner="aauuzyy", repo_name="CipherV2", current_version="4.0.0"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.latest_version = None
        self.release_notes = None
        self.download_url = None
        
    def check_for_updates(self):
        """Check GitHub for latest release"""
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'CipherV4-UpdateChecker')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                # Extract version from tag_name
                tag_name = data.get('tag_name', '')
                # Remove 'v' prefix if present
                self.latest_version = tag_name.lstrip('v')
                self.release_notes = data.get('body', 'No release notes available')
                
                # Get download URL for assets
                assets = data.get('assets', [])
                if assets:
                    self.download_url = assets[0].get('browser_download_url')
                else:
                    self.download_url = data.get('html_url')
                
                return self.is_update_available()
                
        except Exception as e:
            print(f"Update check failed: {e}")
            return None
    
    def is_update_available(self):
        """Compare versions to see if update is available"""
        if not self.latest_version:
            return False
        
        try:
            current = version.parse(self.current_version)
            latest = version.parse(self.latest_version)
            return latest > current
        except:
            # Fallback to string comparison
            return self.latest_version != self.current_version
    
    def get_update_info(self):
        """Get formatted update information"""
        return {
            'current': self.current_version,
            'latest': self.latest_version,
            'notes': self.release_notes,
            'url': self.download_url,
            'available': self.is_update_available()
        }
