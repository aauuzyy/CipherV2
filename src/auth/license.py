"""Authentication system for CipherV2"""
import os
import uuid
import json
import getpass
import platform
import uuid

class LicenseManager:
    def __init__(self):
        self.app_data_dir = os.path.join(os.getenv('APPDATA'), 'CipherV2')
        self.license_file = os.path.join(self.app_data_dir, 'license.json')
        os.makedirs(self.app_data_dir, exist_ok=True)

    def generate_hardware_id(self):
        """Generate unique hardware ID based on system info"""
        system_info = {
            'machine': platform.machine(),
            'processor': platform.processor(),
            'node': platform.node(),
            'username': getpass.getuser()
        }
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(system_info)))

    def validate_license(self, license_key):
        """Validate license key and bind to hardware"""
        try:
            if not self._is_valid_uuid(license_key):
                return False, "Invalid license format"

            hardware_id = self.generate_hardware_id()
            
            # Check if license exists
            if os.path.exists(self.license_file):
                with open(self.license_file, 'r') as f:
                    stored_data = json.load(f)
                    if stored_data['license'] == license_key:
                        if stored_data['hardware_id'] == hardware_id:
                            return True, "License validated"
                        return False, "License bound to different hardware"

            # Store new license
            license_data = {
                'license': license_key,
                'hardware_id': hardware_id
            }
            with open(self.license_file, 'w') as f:
                json.dump(license_data, f)

            return True, "License activated successfully"

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def check_existing_license(self):
        """Check if valid license exists"""
        try:
            if not os.path.exists(self.license_file):
                return False, "No license found"

            with open(self.license_file, 'r') as f:
                stored_data = json.load(f)
                if self.generate_hardware_id() != stored_data['hardware_id']:
                    return False, "Hardware ID mismatch"
                
                return True, "License valid"
        except:
            return False, "License validation failed"

    @staticmethod
    def _is_valid_uuid(val):
        """Check if string is valid UUID"""
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False