"""
Process Inspector - Analyze running processes including self-inspection
For debugging and educational purposes
"""
import psutil
import os
import sys
import threading
import time

class ProcessInspector:
    """Inspect and analyze process details"""
    
    def __init__(self):
        self.current_pid = os.getpid()
        self.current_process = psutil.Process(self.current_pid)
    
    def get_self_info(self):
        """Get information about current process (CipherV2)"""
        try:
            info = {
                'pid': self.current_pid,
                'name': self.current_process.name(),
                'exe': self.current_process.exe(),
                'cwd': self.current_process.cwd(),
                'status': self.current_process.status(),
                'create_time': time.strftime('%Y-%m-%d %H:%M:%S', 
                                             time.localtime(self.current_process.create_time())),
                'num_threads': self.current_process.num_threads(),
                'cpu_percent': self.current_process.cpu_percent(interval=0.1),
                'memory_info': self.current_process.memory_info(),
                'memory_percent': self.current_process.memory_percent(),
            }
            return info
        except Exception as e:
            return {'error': str(e)}
    
    def get_memory_maps(self):
        """Get memory maps of current process"""
        try:
            maps = []
            for mmap in self.current_process.memory_maps(grouped=True):
                maps.append({
                    'path': mmap.path,
                    'rss': mmap.rss,
                    'size': mmap.size,
                })
            return maps
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_open_files(self):
        """Get list of open files"""
        try:
            files = []
            for f in self.current_process.open_files():
                files.append({
                    'path': f.path,
                    'fd': f.fd,
                    'mode': getattr(f, 'mode', 'N/A')
                })
            return files
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_connections(self):
        """Get network connections"""
        try:
            connections = []
            for conn in self.current_process.connections():
                connections.append({
                    'fd': conn.fd,
                    'family': str(conn.family),
                    'type': str(conn.type),
                    'local': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                    'remote': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                    'status': conn.status,
                })
            return connections
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_threads(self):
        """Get thread information"""
        try:
            threads = []
            for thread in self.current_process.threads():
                threads.append({
                    'id': thread.id,
                    'user_time': thread.user_time,
                    'system_time': thread.system_time,
                })
            return threads
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_environment_vars(self):
        """Get environment variables"""
        try:
            return dict(self.current_process.environ())
        except Exception as e:
            return {'error': str(e)}
    
    def get_loaded_modules(self):
        """Get loaded Python modules"""
        try:
            modules = []
            for name, module in sorted(sys.modules.items()):
                if module and hasattr(module, '__file__') and module.__file__:
                    modules.append({
                        'name': name,
                        'file': module.__file__,
                        'size': os.path.getsize(module.__file__) if os.path.exists(module.__file__) else 0
                    })
            return modules
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_cpu_usage_realtime(self, duration=5, callback=None):
        """Monitor CPU usage in real-time"""
        try:
            for i in range(duration * 10):
                cpu = self.current_process.cpu_percent(interval=0.1)
                if callback:
                    callback(cpu, i / 10)
                time.sleep(0.1)
        except Exception as e:
            if callback:
                callback(0, -1)
    
    def get_memory_usage_realtime(self, duration=5, callback=None):
        """Monitor memory usage in real-time"""
        try:
            for i in range(duration * 10):
                mem = self.current_process.memory_info().rss / 1024 / 1024  # MB
                if callback:
                    callback(mem, i / 10)
                time.sleep(0.1)
        except Exception as e:
            if callback:
                callback(0, -1)
    
    def get_process_tree(self):
        """Get process tree (parent and children)"""
        try:
            tree = {
                'current': {
                    'pid': self.current_pid,
                    'name': self.current_process.name(),
                },
                'parent': None,
                'children': []
            }
            
            # Get parent
            try:
                parent = self.current_process.parent()
                if parent:
                    tree['parent'] = {
                        'pid': parent.pid,
                        'name': parent.name(),
                    }
            except:
                pass
            
            # Get children
            try:
                for child in self.current_process.children(recursive=True):
                    tree['children'].append({
                        'pid': child.pid,
                        'name': child.name(),
                    })
            except:
                pass
            
            return tree
        except Exception as e:
            return {'error': str(e)}
    
    def format_bytes(self, bytes_value):
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} TB"


# Example usage
if __name__ == "__main__":
    inspector = ProcessInspector()
    
    print("=== Self-Inspection Test ===")
    info = inspector.get_self_info()
    print(f"PID: {info['pid']}")
    print(f"Name: {info['name']}")
    print(f"Threads: {info['num_threads']}")
    print(f"Memory: {info['memory_percent']:.2f}%")
