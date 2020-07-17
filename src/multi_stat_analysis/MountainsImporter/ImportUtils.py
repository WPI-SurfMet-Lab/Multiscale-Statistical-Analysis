import sys, os, winreg, time
import pyautogui
from typing import Optional
from ctypes import wintypes, windll, create_unicode_buffer, pointer

class ResourceFiles:
    SSFA_TEMPLATE = "ssfa-template.mnt"
    MULTI_STAT_TEMPLATE_INIT = "multi-stat-template-init.png"

    START_MNTS_BTN = "start-mountains.png"

    SCALE_SENSITIVE_BTN = "scale-sensitive.png"
    COMPLEXITY_BTN = "complexity.png"

    ANALYSIS_OPTION_BTN = "analysis-method.png"

    EXPORT_BTN = "export-curve.png"
    SAVE_BTN = "save-curve.png"

def append_to_path(end_str, prefix=os.getcwd()):
    """Joins the given end string to the end of the file path prefix."""
    return os.path.join(os.sep, prefix, end_str)

__resource_paths = {}
def resource_abs_path(relative_path):
    """Get absolute path to resources, works for normal file handling and for PyInstaller.
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
        base_path = append_to_path("resources")

    path = append_to_path(relative_path, base_path)
    if not os.path.exists(path):
        raise FileNotFoundError("Could not find resource " + path)
    __resource_paths[relative_path] = path

    return path

def find_resource(relative_path, wait=True, func=None):
    """Using a path to a resource image file, wait for that image to appear.
    A function can then be called while waiting.
    @return pos - center Point of object being clicked. Return None if position was not found"""
    pos = None
    while True:
        time.sleep(0.01)
        pos = pyautogui.locateCenterOnScreen(resource_abs_path(relative_path))
        # Don't wait if wait is False
        if not wait:
            break
        # Resource image was found, return position
        if not pos is None:
            return pos
        # Run the given function if possible
        if not func is None:
            func()
    # If resource could not be found somehow, return None
    return pos

def click_resource(relative_path, wait=True):
    """Using a path to a resource image file, wait for that image to appear, and then click on the screen.
    @return pos - center Point of object being clicked. Return None if position was not found"""
    pos = find_resource(relative_path, wait)
    if not pos is None:
        pyautogui.click(*pos)
    return pos

def get_foreground_window_rect(window_title):
    """Using given window title, find window coordinates.
    @return (top_left_x, top_left_y, btm_right_x, btm_right_y)"""
    hWnd = windll.user32.FindWindowW(None, window_title)
    rect = wintypes.RECT()
    windll.user32.GetWindowRect(hWnd, pointer(rect))
    if rect is None:
        return None
    return (rect.left, rect.top, rect.right, rect.bottom)

def get_foreground_window_title():
    """Output the title of the current foreground window."""
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd) + 1
    buf = create_unicode_buffer(length)
    windll.user32.GetWindowTextW(hWnd, buf, length)
    # Output possible found window title
    return buf.value if buf.value else None

__mountains_path = None
def find_mountains_map() -> str:
    """Get the absolute path to the MountainsMap executable. If it cannot be found,
    an exception will be thrown."""

    # If path has already been found, output it
    global __mountains_path
    if __mountains_path:
        return __mountains_path

    try:
        # Open class ID key registery
        with winreg.ConnectRegistry(None, winreg.HKEY_CLASSES_ROOT) as reg:
            # Open MountainsMap's CLSID specific key
            with winreg.OpenKey(reg, "CLSID\{B55C9B36-8A0F-463A-B367-9926963F08F7}\InprocServer32") as key:
                sub_count, val_count, last_changed = winreg.QueryInfoKey(key)
                # Iterate through keys and find value containing MountainsMap path
                for i in range(val_count):
                    val_name, val_data, val_type = winreg.EnumValue(key, i)
                    # Path value for this key has no name
                    if not val_name:
                        mntsBinDir = val_data
                        break # value has been found, break out of loop

        # Grab folder path for Mountains 'bin' directories
        mntsBinDir = os.path.dirname(mntsBinDir)
        __mountains_path = append_to_path("Mountains.exe", mntsBinDir)
    except Exception as e:
        if __debug__:
            import traceback
            traceback.print_exc()
        raise Exception("Could not find MountainsMap installation.")
    finally:
        return __mountains_path