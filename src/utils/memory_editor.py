"""Memory Editor - Cheat Engine style memory scanning and editing"""
import pymem
import pymem.process
import psutil
import struct
import threading
import time
from typing import List, Tuple, Optional

class MemoryScanner:
    def __init__(self):
        self.process = None
        self.process_handle = None
        self.found_addresses = []
        self.scan_thread = None
        self.is_scanning = False
        self.scan_progress = 0
        
    def get_process_list(self) -> List[Tuple[int, str]]:
        """Get list of running processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                processes.append((proc.info['pid'], proc.info['name']))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return sorted(processes, key=lambda x: x[1].lower())
    
    def attach_process(self, process_name: str) -> bool:
        """Attach to a process by name"""
        try:
            self.process = pymem.Pymem(process_name)
            self.process_handle = self.process.process_handle
            return True
        except Exception as e:
            print(f"Failed to attach to process: {e}")
            return False
    
    def detach_process(self):
        """Detach from current process"""
        if self.process:
            try:
                self.process.close_process()
            except:
                pass
            self.process = None
            self.process_handle = None
    
    def read_int(self, address: int) -> Optional[int]:
        """Read 4-byte integer from memory"""
        try:
            return pymem.memory.read_int(self.process_handle, address)
        except:
            return None
    
    def read_float(self, address: int) -> Optional[float]:
        """Read 4-byte float from memory"""
        try:
            return pymem.memory.read_float(self.process_handle, address)
        except:
            return None
    
    def read_double(self, address: int) -> Optional[float]:
        """Read 8-byte double from memory"""
        try:
            return pymem.memory.read_double(self.process_handle, address)
        except:
            return None
    
    def read_bytes(self, address: int, size: int) -> Optional[bytes]:
        """Read bytes from memory"""
        try:
            return pymem.memory.read_bytes(self.process_handle, address, size)
        except:
            return None
    
    def write_int(self, address: int, value: int) -> bool:
        """Write 4-byte integer to memory"""
        try:
            pymem.memory.write_int(self.process_handle, address, value)
            return True
        except:
            return False
    
    def write_float(self, address: int, value: float) -> bool:
        """Write 4-byte float to memory"""
        try:
            pymem.memory.write_float(self.process_handle, address, value)
            return True
        except:
            return False
    
    def write_double(self, address: int, value: float) -> bool:
        """Write 8-byte double to memory"""
        try:
            pymem.memory.write_double(self.process_handle, address, value)
            return True
        except:
            return False
    
    def write_bytes(self, address: int, data: bytes) -> bool:
        """Write bytes to memory"""
        try:
            pymem.memory.write_bytes(self.process_handle, address, data, len(data))
            return True
        except:
            return False
    
    def first_scan(self, value, value_type: str, callback=None) -> List[int]:
        """Perform first scan for a value"""
        if not self.process:
            return []
        
        self.found_addresses = []
        self.is_scanning = True
        self.scan_progress = 0
        
        def scan_worker():
            try:
                # Simple memory scanning - scan common memory ranges
                regions = [
                    (0x00400000, 0x01000000),  # Common executable region
                    (0x10000000, 0x10000000),  # Heap region
                    (0x20000000, 0x10000000),  # Heap region
                    (0x30000000, 0x10000000),  # Heap region
                ]
                
                total_size = sum(size for _, size in regions)
                scanned_size = 0
                
                for base_addr, size in regions:
                    if not self.is_scanning:
                        break
                    
                    try:
                        # Read memory chunk
                        data = self.read_bytes(base_addr, size)
                        if not data:
                            continue
                        
                        # Scan for value based on type
                        if value_type == "4 Bytes":
                            pattern = struct.pack('<i', int(value))
                            step = 4
                        elif value_type == "Float":
                            pattern = struct.pack('<f', float(value))
                            step = 4
                        elif value_type == "Double":
                            pattern = struct.pack('<d', float(value))
                            step = 8
                        elif value_type == "2 Bytes":
                            pattern = struct.pack('<h', int(value))
                            step = 2
                        elif value_type == "Byte":
                            pattern = struct.pack('B', int(value))
                            step = 1
                        else:
                            step = 4
                            pattern = struct.pack('<i', int(value))
                        
                        # Search for pattern
                        for i in range(0, len(data) - len(pattern), step):
                            if data[i:i+len(pattern)] == pattern:
                                self.found_addresses.append(base_addr + i)
                        
                        scanned_size += size
                        self.scan_progress = int((scanned_size / total_size) * 100)
                        
                        if callback:
                            callback(self.scan_progress, len(self.found_addresses))
                    
                    except Exception as e:
                        continue
            
            except Exception as e:
                print(f"Scan error: {e}")
            finally:
                self.is_scanning = False
                if callback:
                    callback(100, len(self.found_addresses))
        
        self.scan_thread = threading.Thread(target=scan_worker, daemon=True)
        self.scan_thread.start()
        
        return self.found_addresses
    
    def next_scan(self, value, value_type: str, callback=None) -> List[int]:
        """Perform next scan on found addresses"""
        if not self.process or not self.found_addresses:
            return []
        
        self.is_scanning = True
        self.scan_progress = 0
        new_addresses = []
        
        def scan_worker():
            try:
                total = len(self.found_addresses)
                
                for idx, address in enumerate(self.found_addresses):
                    if not self.is_scanning:
                        break
                    
                    try:
                        # Read current value at address
                        if value_type == "4 Bytes":
                            current = self.read_int(address)
                            target = int(value)
                        elif value_type == "Float":
                            current = self.read_float(address)
                            target = float(value)
                        elif value_type == "Double":
                            current = self.read_double(address)
                            target = float(value)
                        else:
                            current = self.read_int(address)
                            target = int(value)
                        
                        if current is not None and current == target:
                            new_addresses.append(address)
                    
                    except:
                        pass
                    
                    if idx % 1000 == 0:
                        self.scan_progress = int((idx / total) * 100)
                        if callback:
                            callback(self.scan_progress, len(new_addresses))
                
                self.found_addresses = new_addresses
                self.is_scanning = False
                if callback:
                    callback(100, len(new_addresses))
            
            except Exception as e:
                print(f"Next scan error: {e}")
                self.is_scanning = False
        
        self.scan_thread = threading.Thread(target=scan_worker, daemon=True)
        self.scan_thread.start()
        
        return self.found_addresses
    
    def stop_scan(self):
        """Stop current scan"""
        self.is_scanning = False
    
    def get_address_value(self, address: int, value_type: str):
        """Get current value at address"""
        if value_type == "4 Bytes":
            return self.read_int(address)
        elif value_type == "Float":
            return self.read_float(address)
        elif value_type == "Double":
            return self.read_double(address)
        else:
            return self.read_int(address)
    
    def set_address_value(self, address: int, value, value_type: str) -> bool:
        """Set value at address"""
        if value_type == "4 Bytes":
            return self.write_int(address, int(value))
        elif value_type == "Float":
            return self.write_float(address, float(value))
        elif value_type == "Double":
            return self.write_double(address, float(value))
        else:
            return self.write_int(address, int(value))
