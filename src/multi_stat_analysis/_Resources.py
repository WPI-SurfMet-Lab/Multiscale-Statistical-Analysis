import sys, os, winreg
from typing import Optional
from ctypes import wintypes, windll, create_unicode_buffer

__resource_paths = {}
def resource_path(relative_path):
    """Get absolute path to resource, works for normal file handling and for PyInstaller.
    Based on answer from stackoverflow page: 
    https://stackoverflow.com/questions/5227107/python-code-to-read-registry."""

    # If path has already been found (resouces cannot move), return it
    global __resource_paths
    if relative_path in __resource_paths:
        return __resource_paths[relative_path]

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.join(os.sep, os.getcwd(), "resources")

    path = os.path.join(os.sep, base_path, relative_path)
    if not os.path.exists(path):
        raise FileNotFoundError("Could not find resource " + path)

    return path

def get_foreground_window_title():
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)
    # 1-liner alternative: return buf.value if buf.value else None
    if buf.value:
        return buf.value
    else:
        return None

__mountains_path = None
def find_mountains_map() -> str:
    """Get the absolute path to the MountainsMap executable. If it cannot be found,
    an exception will be thrown."""
    global __mountains_path

    # If path has already been found, output it
    if __mountains_path:
        return __mountains_path
    try:
        with winreg.ConnectRegistry(None, winreg.HKEY_CLASSES_ROOT) as reg:
            with winreg.OpenKey(reg, "CLSID\{B55C9B36-8A0F-463A-B367-9926963F08F7}\InprocServer32") as key:
                sub_count, val_count, last_changed = winreg.QueryInfoKey(key)
                for i in range(val_count):
                    val_name, val_data, val_type = winreg.EnumValue(key, i)
                    # Path value for this key has no name
                    if not val_name:
                        mntsBinDir = val_data
                        break # value has been found, break out of loop

        # Grab folder path for Mountains 'bin' directories
        mntsBinDir = os.path.dirname(mntsBinDir)
        __mountains_path = os.path.join(os.sep, mntsBinDir, "Mountains.exe")
    except Exception as e:
        if __debug__:
            import traceback
            traceback.print_exc()
        raise Exception("Could not find MountainsMap installation.")
    finally:
        return __mountains_path