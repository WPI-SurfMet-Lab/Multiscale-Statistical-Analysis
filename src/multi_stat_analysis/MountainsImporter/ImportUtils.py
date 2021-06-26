import sys, os, winreg, time, errno
import pyautogui
import subprocess
from ctypes import wintypes, windll, create_unicode_buffer, pointer


class ResourceFiles:
    DIRECTORY = "resources"

    SSFA_TEMPLATE = "ssfa-template.mnt"

    START_MNTS_BTN = "start-mountains.png"

    SCALE_SENSITIVE_BTN = "scale-sensitive.png"
    COMPLEXITY_BTN = "complexity.png"

    ANALYSIS_OPTION_BTN = "analysis-method.png"

    EXPORT_BTN = "export-curve.png"
    SAVE_BTN = "save-curve.png"


def append_to_path(end_str, prefix=os.getcwd()):
    """Joins the given end string to the end of the file path prefix."""
    return os.path.join(os.sep, prefix, end_str)


_DEFAULT_TIMEOUT = 60.0
_resource_paths = {}
# Find base path for resources
try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    _resource_base_path = append_to_path(ResourceFiles.DIRECTORY, sys._MEIPASS)
except Exception:
    _resource_base_path = append_to_path(ResourceFiles.DIRECTORY)


def resource_abs_path(relative_path):
    """Get absolute path to resources, works for normal file handling and for PyInstaller.
    Based on answer from stackoverflow page: 
    https://stackoverflow.com/questions/5227107/python-code-to-read-registry."""

    # If path has already been found (resouces cannot move), return it
    global _resource_paths
    if relative_path in _resource_paths:
        return _resource_paths[relative_path]

    global _resource_base_path
    path = append_to_path(relative_path, _resource_base_path)
    if not os.path.exists(path):
        raise FileNotFoundError("Could not find resource " + path)
    _resource_paths[relative_path] = path

    return path


def find_resource(relative_path, timeout=_DEFAULT_TIMEOUT, wait=True, func=None):
    """Using a path to a resource image file, wait for that image to appear.
    A function can then be called while waiting.
    @return pos - center Point of object being clicked. Return None if position was not found"""

    end_time = time.time() + (0 if timeout is None else timeout)
    if __debug__:
        print("TIMEOUT:" + str(timeout))
        print("TIMEOUT:" + str(time.time()))
        print("TIMEOUT:" + str(end_time))

    def timedout():
        if timeout is None:
            return False
        else:
            return time.time() >= end_time

    while True:
        time.sleep(0.01)
        pos = pyautogui.locateCenterOnScreen(resource_abs_path(relative_path))
        # Resource image was found, return position
        if not pos is None:
            return pos
        # Run the given function if possible
        if not func is None:
            func()
        # Don't wait if wait is False
        if not wait:
            break
        # Throw exception if the timeout has occured
        if timedout():
            raise TimeoutError("Timeout has occured, could not find resource on screen.")

    # Loop exited, resource could not be found, return None
    return None


def click_resource(relative_path, timeout=_DEFAULT_TIMEOUT, wait=True):
    """Using a path to a resource image file, wait for that image to appear, and then click on the screen.
    @return pos - center Point of object being clicked. Return None if position was not found"""
    pos = find_resource(relative_path, timeout, wait)
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


class MountainsNotFound(str):
    def __init__(self):
        super().__init__()


_MOUNTAINS_PATH = None


def find_mountains_map() -> str:
    """Get the absolute path to the MountainsMap executable. If it cannot be found,
    an exception will be thrown."""

    # If path has already been found, output it
    global _MOUNTAINS_PATH
    if not _MOUNTAINS_PATH is None:
        return _MOUNTAINS_PATH

    excep = None
    try:
        # Open class ID key registery
        with winreg.ConnectRegistry(None, winreg.HKEY_CLASSES_ROOT) as reg:
            # Open MountainsMap's CLSID specific key
            with winreg.OpenKey(reg, "CLSID\\{B55C9B36-8A0F-463A-B367-9926963F08F7}\\InprocServer32") as key:
                sub_count, val_count, last_changed = winreg.QueryInfoKey(key)
                # Iterate through keys and find value containing MountainsMap path
                for i in range(val_count):
                    val_name, val_data, val_type = winreg.EnumValue(key, i)
                    # Path value for this key has no name
                    if not val_name:
                        mntsBinDir = val_data
                        break  # value has been found, break out of loop

        # Grab folder path for Mountains 'bin' directories
        mntsBinDir = os.path.dirname(mntsBinDir)
        _MOUNTAINS_PATH = append_to_path("Mountains.exe", mntsBinDir)
        # Check if MountainsMap path actually exists
        if not os.path.exists(_MOUNTAINS_PATH):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), _MOUNTAINS_PATH)
    except (FileNotFoundError, Exception) as e:
        if __debug__:
            import traceback
            traceback.print_exc()
        _MOUNTAINS_PATH = MountainsNotFound()
        excep = e
    finally:
        # Raise exception if it occurred
        if excep is not None:
            raise excep
        return _MOUNTAINS_PATH


class MountainsProcess(subprocess.Popen):
    """Starts a MountainsMap process that can then be interacted with to generate
    results files. These results can then later be used to import into the app.

    @param cmd_path - Given path to external commands script file."""

    def __init__(self, cmd_path):
        super().__init__("\"" + find_mountains_map() + "\"" + \
                         " /CMDFILE:\"" + cmd_path + "\" /NOSPLASHCREEN")


TEMP_PATH = append_to_path(".temp")
TMPLT_PATH = resource_abs_path(ResourceFiles.SSFA_TEMPLATE)


def write_mnts_surf_import_script(cmd_path, surf_file_path, initializer=True):
    # Write external command file for MountainsMap
    with open(cmd_path, "w") as cmd_file:
        cmd_contents = []
        # If the command file has not been created yet, include extra initialization commands
        if initializer:
            cmd_contents = [
                "STOP_ON_ERROR OFF",
                "SHOW",
                "MESSAGES OFF",
                "LOAD_DOCUMENT \"" + TMPLT_PATH + "\"",
                "AUTOSAVE OFF"
            ]
        # Add substitution command to file
        cmd_contents.append("SUBSTITUTE_STUDIABLE \"" + surf_file_path + "\" 1 MULTILAYER_MODE=7")
        # Create command file
        cmd_file.write("\n".join(cmd_contents))
