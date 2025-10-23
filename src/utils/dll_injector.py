"""
DLL Injector - Client-side injection tool
For educational purposes, game modding, and debugging your own applications
WARNING: Only use on processes you own or have permission to modify
"""
import ctypes
import sys
from ctypes import wintypes

# Windows API constants
PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_READWRITE = 0x04
VIRTUAL_MEM = MEM_COMMIT | MEM_RESERVE

# Load Windows DLLs
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
user32 = ctypes.WinDLL('user32', use_last_error=True)

class DLLInjector:
    """Client-side DLL injection utility"""
    
    def __init__(self):
        self.kernel32 = kernel32
        self.last_error = None
    
    def get_process_id(self, process_name):
        """Get process ID by name"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name.lower():
                    return proc.info['pid']
            return None
        except Exception as e:
            self.last_error = f"Error finding process: {e}"
            return None
    
    def inject_dll(self, process_id, dll_path):
        """
        Inject a DLL into a target process
        
        Args:
            process_id: Target process ID
            dll_path: Full path to DLL file
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Validate DLL path
            import os
            if not os.path.exists(dll_path):
                return False, f"DLL not found: {dll_path}"
            
            if not dll_path.lower().endswith('.dll'):
                return False, "File must be a .dll"
            
            # Open target process
            h_process = self.kernel32.OpenProcess(
                PROCESS_ALL_ACCESS,
                False,
                process_id
            )
            
            if not h_process:
                error = ctypes.get_last_error()
                return False, f"Failed to open process (Error {error}). Try running as Administrator."
            
            # Get LoadLibraryA address
            h_kernel32 = self.kernel32.GetModuleHandleW("kernel32.dll")
            if not h_kernel32:
                self.kernel32.CloseHandle(h_process)
                return False, "Failed to get kernel32.dll handle"
            
            load_library_addr = self.kernel32.GetProcAddress(h_kernel32, b"LoadLibraryA")
            if not load_library_addr:
                self.kernel32.CloseHandle(h_process)
                return False, "Failed to get LoadLibraryA address"
            
            # Allocate memory in target process
            dll_path_bytes = dll_path.encode('ascii') + b'\x00'
            dll_path_len = len(dll_path_bytes)
            
            arg_address = self.kernel32.VirtualAllocEx(
                h_process,
                None,
                dll_path_len,
                VIRTUAL_MEM,
                PAGE_READWRITE
            )
            
            if not arg_address:
                self.kernel32.CloseHandle(h_process)
                return False, "Failed to allocate memory in target process"
            
            # Write DLL path to target process
            written = ctypes.c_size_t(0)
            write_result = self.kernel32.WriteProcessMemory(
                h_process,
                arg_address,
                dll_path_bytes,
                dll_path_len,
                ctypes.byref(written)
            )
            
            if not write_result or written.value != dll_path_len:
                self.kernel32.VirtualFreeEx(h_process, arg_address, 0, 0x8000)
                self.kernel32.CloseHandle(h_process)
                return False, "Failed to write DLL path to target process"
            
            # Create remote thread to load DLL
            thread_id = wintypes.DWORD(0)
            h_thread = self.kernel32.CreateRemoteThread(
                h_process,
                None,
                0,
                load_library_addr,
                arg_address,
                0,
                ctypes.byref(thread_id)
            )
            
            if not h_thread:
                self.kernel32.VirtualFreeEx(h_process, arg_address, 0, 0x8000)
                self.kernel32.CloseHandle(h_process)
                error = ctypes.get_last_error()
                return False, f"Failed to create remote thread (Error {error})"
            
            # Wait for thread to complete
            self.kernel32.WaitForSingleObject(h_thread, 5000)  # 5 second timeout
            
            # Get thread exit code to verify injection
            exit_code = wintypes.DWORD()
            self.kernel32.GetExitCodeThread(h_thread, ctypes.byref(exit_code))
            
            # Cleanup
            self.kernel32.CloseHandle(h_thread)
            self.kernel32.VirtualFreeEx(h_process, arg_address, 0, 0x8000)
            self.kernel32.CloseHandle(h_process)
            
            if exit_code.value == 0:
                return False, "DLL injection failed - LoadLibrary returned NULL"
            
            return True, f"DLL injected successfully! Module handle: 0x{exit_code.value:X}"
            
        except Exception as e:
            self.last_error = str(e)
            return False, f"Injection error: {e}"
    
    def inject_by_name(self, process_name, dll_path):
        """
        Inject DLL by process name
        
        Args:
            process_name: Name of target process (e.g., "notepad.exe")
            dll_path: Full path to DLL file
            
        Returns:
            tuple: (success: bool, message: str)
        """
        pid = self.get_process_id(process_name)
        if not pid:
            return False, f"Process '{process_name}' not found"
        
        return self.inject_dll(pid, dll_path)
    
    def eject_dll(self, process_id, dll_name):
        """
        Eject/unload a DLL from a process
        
        Args:
            process_id: Target process ID
            dll_name: Name of DLL to eject (e.g., "mydll.dll")
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Open target process
            h_process = self.kernel32.OpenProcess(
                PROCESS_ALL_ACCESS,
                False,
                process_id
            )
            
            if not h_process:
                return False, "Failed to open process"
            
            # Get module handle
            h_module = self.kernel32.GetModuleHandleW(dll_name)
            if not h_module:
                self.kernel32.CloseHandle(h_process)
                return False, f"DLL '{dll_name}' not found in process"
            
            # Get FreeLibrary address
            h_kernel32 = self.kernel32.GetModuleHandleW("kernel32.dll")
            free_library_addr = self.kernel32.GetProcAddress(h_kernel32, b"FreeLibrary")
            
            if not free_library_addr:
                self.kernel32.CloseHandle(h_process)
                return False, "Failed to get FreeLibrary address"
            
            # Create remote thread to free library
            thread_id = wintypes.DWORD(0)
            h_thread = self.kernel32.CreateRemoteThread(
                h_process,
                None,
                0,
                free_library_addr,
                h_module,
                0,
                ctypes.byref(thread_id)
            )
            
            if not h_thread:
                self.kernel32.CloseHandle(h_process)
                return False, "Failed to create remote thread"
            
            # Wait for thread
            self.kernel32.WaitForSingleObject(h_thread, 5000)
            
            # Cleanup
            self.kernel32.CloseHandle(h_thread)
            self.kernel32.CloseHandle(h_process)
            
            return True, f"DLL '{dll_name}' ejected successfully"
            
        except Exception as e:
            return False, f"Ejection error: {e}"
    
    def list_loaded_modules(self, process_id):
        """
        List all loaded modules/DLLs in a process
        
        Args:
            process_id: Target process ID
            
        Returns:
            list: List of (module_name, base_address) tuples
        """
        try:
            import psutil
            process = psutil.Process(process_id)
            modules = []
            
            for module in process.memory_maps():
                if module.path and module.path.lower().endswith('.dll'):
                    import os
                    module_name = os.path.basename(module.path)
                    modules.append((module_name, module.path))
            
            return modules
        except Exception as e:
            self.last_error = str(e)
            return []


# Example usage and testing
if __name__ == "__main__":
    print("DLL Injector - Client-Side Injection Tool")
    print("=" * 50)
    print("WARNING: Only use on processes you own!")
    print("=" * 50)
    
    injector = DLLInjector()
    
    # Example: List processes
    try:
        import psutil
        print("\nAvailable processes:")
        for i, proc in enumerate(psutil.process_iter(['pid', 'name'])):
            if i < 10:  # Show first 10
                print(f"  {proc.info['pid']:>6} - {proc.info['name']}")
    except:
        pass
