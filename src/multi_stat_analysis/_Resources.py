import sys, os

def resource_path(relative_path):
    """Get absolute path to resource, works for normal file handling and for PyInstaller.
    Found from this stackoverflow page: 
    https://stackoverflow.com/questions/5227107/python-code-to-read-registry."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.getcwd()
    return os.path.join(base_path, relative_path)