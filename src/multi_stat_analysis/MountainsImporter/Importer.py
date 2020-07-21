import __main__
import MountainsImporter.ImportUtils as ImportUtils
from MountainsImporter.ImportUtils import ResourceFiles
import wx, os, subprocess, time, traceback, shutil
import pyautogui
from multiprocessing import Process, Queue
from enum import Enum

_CMDS_FILE_NAME = "-temp-cmds.txt"
_TMPLT_FILE_NAME = "-ssfa-tmplt.mnt"

_DELAY = 1
_PYAUTOGUI_ACTION_DELAY = 0.05
_FILE_DIALOG_TAB_INTERVAL = 0.05

def import_surfaces(file_paths):
    """Takes an input of an array of strings for the file path of each surface being analyzed. These surfaces are
    input into MountainsMap using mouse and keyboard control. The user is then given a choice of selecting either
    length-scale, area-scale, or complexity analysis. These result file paths are then returned.
    @return result_file_paths - Set to None if import could not continue"""
    orig_FAILSAFE = pyautogui.FAILSAFE
    orig_PAUSE = pyautogui.PAUSE

    mnts_instance = None
    temp_dir = None
    output = None

    # Collect user selected configuration from import options dialog
    options_dialog = ImportOptionsDialog(file_paths)
    options_dialog.CenterOnScreen()
    options_dialog.ShowModal()

    # Get output from dialog
    result_file_paths = options_dialog.get_result_file_paths()
    mnts_processes = options_dialog.get_mnts_processes()
    if __debug__:
        print(mnts_processes)

    # If the options were not selected, end file opening prematurely
    if not (result_file_paths and mnts_processes):
        return None

    # Delete old result files if they exist
    for file in result_file_paths:
        if os.path.exists(file):
            os.remove(file)

    # Create temporary directory
    temp_dir = ImportUtils.append_to_path(".temp")
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    # Store directory locations for mountains template
    tmplt_path = ImportUtils.resource_abs_path(ResourceFiles.SSFA_TEMPLATE)

    # Store directory location for mountains executable
    mountains_path = ImportUtils.find_mountains_map()

    # Store directory locations for mountains external commands file
    # Uses time in the file name to prevent accidental usage of this file
    cmd_path = ImportUtils.append_to_path(str(time.time_ns()) + _CMDS_FILE_NAME, temp_dir)

    # Catch errors while assuming control of keyboard/mouse with pyautogui
    try:
        # Initialize pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = _PYAUTOGUI_ACTION_DELAY

        # Launch Mountains for surfaces
        mnts_instance = subprocess.Popen("\"" + mountains_path + "\"" + \
            " /CMDFILE:\"" + cmd_path + "\" /NOSPLASHCREEN", shell=True)

        # Generate result files for each selected surface
        for i, surf_file_path in enumerate(file_paths) :
            # Write external command file for MountainsMap
            with open(cmd_path, "w") as cmd_file :
                cmd_contents = []
                # If the command file has not been created yet, include extra initialization commands
                if i == 0:
                    cmd_contents = [
                        "STOP_ON_ERROR OFF",
                        "SHOW",
                        "MESSAGES OFF",
                        "LOAD_DOCUMENT \"" + tmplt_path + "\"",
                        "AUTOSAVE OFF"
                    ]
                # Add substitution command to file
                cmd_contents.append("SUBSTITUTE_STUDIABLE \"" + surf_file_path + "\" 1 MULTILAYER_MODE=7")
                # Create command file
                cmd_file.write("\n".join(cmd_contents))

            # Handle MountainsMap startup window
            if i <= 0:
                ImportUtils.click_resource(ResourceFiles.START_MNTS_BTN)

            # Use Mountains and generate given surface file
            mnts_process = mnts_processes[i]
            excep_queue = mnts_process.get_excep_queue()
            mnts_process.start()

            # Used to check that failsafe is not being triggered
            while True:
                # Kill thread if failsafe was triggered
                x, y = pyautogui.position()
                if x == 0 and y == 0:
                    mnts_process.kill()
                    raise Exception("Terminating import prematurly. Failsafe triggered.")

                # Terminate alive check if exception occured during runtime
                exception = None
                if not excep_queue.empty():
                    exception = excep_queue.get()
                if not exception is None:
                    e, tb = exception
                    # If end process exception was thrown, leave failsafe check loop
                    if isinstance(e, MountainsProcess.EndProcessException):
                        break
                    # Otherwise, a normal exception was thrown
                    else:
                        print(tb)
                        raise e

            # End MountainsMap interact process, no longer needed
            mnts_process.kill()

        # Set output to generated result file paths
        output = result_file_paths
    finally:
        # Terminate this instance of mountains, current job complete
        if mnts_instance is not None:
            pyautogui.press('esc')
            pyautogui.hotkey('alt', 'f4')
            pyautogui.press('enter')
            mnts_instance.kill()
            mnts_instance.wait()
        # Delete temporary directory
        #if temp_dir is not None:
        #    shutil.rmtree(temp_dir, ignore_errors=False)

        # Revert pyautogui to old settings
        pyautogui.FAILSAFE = orig_FAILSAFE
        pyautogui.PAUSE = orig_PAUSE

    # Output generated result files
    return output

class MountainsProcess(Process):
    """Using the given result file destination and MountainsMap interaction function,
    launch the MountainsMap app and generate the results file.
    If an exception is thrown, it can be recieved using the excep_recv pipe.
    This pipe outputs a tuple with data:
      [0] - Exception to re-raise
      [1] - Traceback to print out"""
    def __init__(self, result_file_path, file_dir, file_name,
                 sensitivity_func, analysis_func_wrapper):
        Process.__init__(self, target=MountainsProcess.interact_func, args=(self,))
        self.result_file_path = result_file_path
        self.file_dir = file_dir
        self.file_name = file_name
        self.sensitivity_func = sensitivity_func
        self.analysis_func_wrapper = analysis_func_wrapper
        self.excep_queue = Queue()

    class EndProcessException(Exception):
        """Exception thrown when the process ends sucessfully."""
        def __init__(self):
            super().__init__()

    def interact_func(self):
        orig_FAILSAFE = pyautogui.FAILSAFE
        orig_PAUSE = pyautogui.PAUSE
        try:
            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = _PYAUTOGUI_ACTION_DELAY
            print(self)

            # Generate results file from scale-sensitive fractal analysis
            self.option_select_export_func()
            # Throw exception if the results file was not correctly generated
            if not os.path.exists(self.result_file_path):
                raise FileNotFoundError("Could not find results file " + self.result_file_path +
                                        ". Terminating early.")
            # Process has terminated
            raise MountainsProcess.EndProcessException()
        except Exception as e:
            self.excep_queue.put((e, traceback.format_exc()))
        finally:
            pyautogui.FAILSAFE = orig_FAILSAFE
            pyautogui.PAUSE = orig_PAUSE

    def option_select_export_func(self):
        """Defines how the mouse and keyboard will interact with MountainsMap"""
        window_title = ""
        top_left_x = top_left_y = btm_right_x = btm_right_y = 0
        window_center = (0,0)
        # Wait for template document to load
        while ImportUtils.find_resource(ResourceFiles.EXPORT_BTN, wait=False) is None:
            # Add delay to prevent excesive usage of this loop
            time.sleep(0.01)
            # Get current title of current MountainsMap window
            window_title = ImportUtils.get_foreground_window_title()
            # If a title could not be found, set it to be blank
            if window_title is None:
                continue

            # Check if template document has loaded with correct file name
            if not ResourceFiles.SSFA_TEMPLATE in window_title:
                continue

            # Check to make sure the current window position is not (0,0,0,0)
            # If it is (0,0,0,0), then window still needs to be initialized
            window_rect = ImportUtils.get_foreground_window_rect(window_title)
            if window_rect is None or window_rect == (0,0,0,0):
                continue

            # Set window dimension values and leave loop
            top_left_x, top_left_y, btm_right_x, btm_right_y = window_rect
            # Get point at center of screen
            window_center = ((btm_right_x - top_left_x)//2 + top_left_x,
                             (btm_right_y - top_left_y)//2 + top_left_y)
            # If point is at failsafe position, recalculate center
            if window_center == (0,0):
                continue

            # Window center has been found, break out of init loop
            break

        # Give time for finishing loading process
        time.sleep(1.0)
        # Select ssfa graph
        pyautogui.click(*window_center)
        time.sleep(_DELAY)
        if __debug__:
            print("Selected graph")

        # Select sensitivity and analysis options
        self.sensitivity_func()
        if __debug__:
            time.sleep(_DELAY)
            print("Ran sensitivity selection")
        self.analysis_func_wrapper.call()
        if __debug__:
            time.sleep(_DELAY)
            print("Ran selection")

        # Export result files --
        # Click on export button
        ImportUtils.click_resource(ResourceFiles.EXPORT_BTN)
        if __debug__:
            print("Clicked export button")
            time.sleep(_DELAY)
        # Enter file name
        pyautogui.typewrite(self.file_name)
        if __debug__:
            print("Enter file name")
            time.sleep(_DELAY)
        # Tab to file path
        pyautogui.press('tab', presses=6, interval=_FILE_DIALOG_TAB_INTERVAL)
        if __debug__:
            time.sleep(_DELAY)
        # Edit file path
        pyautogui.press('enter')
        pyautogui.typewrite(self.file_dir)
        if __debug__:
            time.sleep(_DELAY)
        pyautogui.press('enter')
        if __debug__:
            print("Entered file directory")
            time.sleep(_DELAY)
        # Press save button
        #pyautogui.press('enter')
        ImportUtils.click_resource(ResourceFiles.SAVE_BTN)
        if __debug__:
            print("Saved result file")
            time.sleep(_DELAY)
        # Exit file editor
        pyautogui.hotkey('alt', 'f4')
        if __debug__:
            print("Closed file editor")

    def get_excep_queue(self): return self.excep_queue
    def get_file_name(self): return self.file_name

def get_results_data(file_paths, results_dir, sensitive_func, analysis_func_wrapper):
    """Given the list of surface files and a results directory,
    generate the corresponding list of new file names and paths.
    Also generates mountains interaction process calls."""
    result_paths = []
    mountains_processes = []
    for i, surfName in enumerate(file_paths):
        surfName = os.path.normpath(surfName) # Remove stray/double slashes
        surfName = os.path.splitext(surfName)[0] # Remove file extension
        surfName = os.path.basename(surfName) # Grab file name
        # Add to file lists
        result_paths.append(ImportUtils.append_to_path(surfName + ".txt", results_dir))
        # Add to function list
        mountains_processes.append(
            MountainsProcess(result_paths[i], results_dir, surfName, sensitive_func, analysis_func_wrapper))
    # Output generated paths and functions
    return result_paths, mountains_processes

def select_scale_sensitivity():
    """Select scale-sensitivity option"""
    ImportUtils.click_resource(ResourceFiles.SCALE_SENSITIVE_BTN)

def select_complexity():
    """Select scale-sensitivity option"""
    ImportUtils.click_resource(ResourceFiles.COMPLEXITY_BTN)

_sensitivity_option_map = {}
class SensitivityOption(Enum):
    """Used by ImportOptionsDialog to specify options for sensitivity combo box."""
    Scale = ("Scale-sensitive Analysis", select_scale_sensitivity)
    Complexity = ("Complexity Analysis", select_complexity)

    def __init__(self, label, func):
        self.label = label
        self.func = func
        # Assign label to function map
        global _sensitivity_option_map
        _sensitivity_option_map[label] = func

def select_analysis_option(pos):
    """Click on the analysis menu button to prepare for selecting the option"""
    ImportUtils.click_resource(ResourceFiles.ANALYSIS_OPTION_BTN)
    # Select button at this pos
    pyautogui.press("down", presses=pos, interval=0.1)
    pyautogui.press("enter", interval=0.1)

class AnalysisOptionFuncWrapper:
    def __init__(self, index):
        self.index = index    
    def call(self):
        select_analysis_option(self.index)

_analysis_option_map = {}
class AnalysisOption(Enum):
    """Used by ImportOptionsDialog to specify options for anlaysis combo box."""
    LengthRows = ("Length Analysis (rows)", None)
    LengthColumns = ("Length Analysis (columns)", None)
    Area1Corner = ("Area Analysis (1 corner)", None)
    Area4Corners = ("Area Analysis (4 corners)", None)

    def __init__(self, label, blank):
        self.label = label
        # Assign label to function map
        global _analysis_option_map
        # Assign analysis option function
        _analysis_option_map[label] = AnalysisOptionFuncWrapper(len(_analysis_option_map) + 1)

class ImportOptionsDialog(wx.Dialog):
    """Create surface import options selection. This includes specifying scale/complexity sensitivity,
    the type of surface analysis being done, as well as the directory for saving the analysis data.
    It can then be used to return these selected options wrapped within interactive functions designed
    for Digital Surf's MountainsMap application."""

    def __init__(self, file_paths):
        """@param file_paths - List of surface file paths that will be analyzed into result files."""
        width = 600
        height = 250
        wx.Dialog.__init__(self, __main__.frame, wx.ID_ANY, "Surface Import Options", size=(width, height))
        self.options_panel = wx.Panel(self, wx.ID_ANY)
        options_sizer = wx.BoxSizer(wx.VERTICAL)

        # Surface file path inputs
        self.file_paths = file_paths
        # Output values from dialog
        self.result_file_paths = None
        self.mnts_processes = None

        # Analysis Type Selection
        analysis_label = wx.StaticText(self.options_panel, wx.ID_ANY, label="Analysis Type:")
        self.analysis_combo = self.getTypeCombo(AnalysisOption)

        # Sensitivity Type Selection
        sensitivity_label = wx.StaticText(self.options_panel, wx.ID_ANY, label="Sensitivity Type:")
        self.sensitivity_combo = self.getTypeCombo(SensitivityOption)

        # Initialize sizer for both combo boxes
        combo_sizer = wx.BoxSizer(wx.HORIZONTAL)
        analysis_sizer = wx.BoxSizer(wx.VERTICAL)
        sensitivity_sizer = wx.BoxSizer(wx.VERTICAL)
        # Initialize Analyasis sizer
        analysis_sizer.AddStretchSpacer()
        analysis_sizer.Add(analysis_label, flag=wx.ALIGN_LEFT)
        analysis_sizer.Add(self.analysis_combo, flag=wx.ALIGN_LEFT)
        analysis_sizer.AddStretchSpacer()
        # Initialize Sensitivity sizer
        sensitivity_sizer.AddStretchSpacer()
        sensitivity_sizer.Add(sensitivity_label, flag=wx.ALIGN_LEFT)
        sensitivity_sizer.Add(self.sensitivity_combo, flag=wx.ALIGN_LEFT)
        sensitivity_sizer.AddStretchSpacer()
        # Layout combo sizers
        combo_sizer.AddStretchSpacer()
        combo_sizer.Add(analysis_sizer, flag=wx.CENTER)
        combo_sizer.AddStretchSpacer()
        combo_sizer.Add(sensitivity_sizer, flag=wx.CENTER)
        combo_sizer.AddStretchSpacer()

        # Results folder selection button handling
        results_label = wx.StaticText(self.options_panel, wx.ID_ANY, label="Select Results Folder:")
        self.results_dir_dialog = wx.DirPickerCtrl(self.options_panel, wx.ID_ANY, message="Select Results Folder",
                                                   style=wx.DIRP_DEFAULT_STYLE)

        # Completion button initialization
        completion_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cancelBtn = wx.Button(self.options_panel, wx.ID_CANCEL, label="Cancel")
        okBtn = wx.Button(self.options_panel, wx.ID_ANY, label="Ok")
        completion_sizer.Add(cancelBtn, flag=wx.ALIGN_LEFT)
        completion_sizer.Add(okBtn, flag=wx.ALIGN_LEFT)

        # Bind button handler to "Ok" button
        self.Bind(wx.EVT_BUTTON, self.okBtnHandler, okBtn)

        # Final initialization of dialog's sizer
        options_sizer.AddStretchSpacer()
        options_sizer.Add(combo_sizer, flag=wx.CENTER)
        options_sizer.AddStretchSpacer()
        options_sizer.Add(results_label, flag=wx.CENTER)
        options_sizer.Add(self.results_dir_dialog, flag=wx.CENTER)
        options_sizer.AddStretchSpacer()
        options_sizer.Add(completion_sizer, flag=wx.CENTER)
        options_sizer.AddStretchSpacer()
        self.options_panel.SetSizerAndFit(options_sizer)

    def getTypeCombo(self, enum):
        """Generates the combo boxes for each drop down option using a set of enums."""
        choices  = [choice.label for choice in enum]
        return wx.ComboBox(self.options_panel, wx.ID_OK, choices[0],
                                        style=wx.CB_SIMPLE | wx.CB_READONLY,
                                        choices=choices)

    def okBtnHandler(self, event):
        """Handles generation of result file names and mountains interaction functions
        when the user pressed the "ok" button."""
        try:
            # Get Output from combo box and directory picker
            selected_results_dir = self.results_dir_dialog.GetPath()

            # If the given directory is relative, do not use it
            if not os.path.isabs(selected_results_dir):
                raise Exception("Invalid path given. Path needs to be absolute.")
                return

            # Files could possibly be overwritten if the directory already exists
            overwriteSearch = False
            if os.path.isdir(selected_results_dir):
                overwriteSearch = True
            else: # Create new directory to save files, directory accepted
                os.mkdir(selected_results_dir)

            sensitive_func = _sensitivity_option_map[self.sensitivity_combo.GetStringSelection()]
            analysis_func = _analysis_option_map[self.analysis_combo.GetStringSelection()]
            # Build new file path based on given surface files and results dir
            new_file_paths, new_mountains_processes = \
                get_results_data(self.file_paths, selected_results_dir, sensitive_func, analysis_func)

            # Possibly overwrite check was requested
            already_exists = []
            if overwriteSearch:
                # Go through possibly file names and confirm if these files already exist
                for i, path in enumerate(new_file_paths):
                    if os.path.exists(path):
                        already_exists.append(path)
                # Display overwrite dialog if needed
                if already_exists:
                    overwrite_dialog = OverwriteDialog(self, already_exists)
                    # If the user requests to not overwrite these files, end early
                    if not overwrite_dialog.ShowModal() == wx.ID_YES:
                        return

            self.mnts_processes = new_mountains_processes
            self.result_file_paths = new_file_paths
            self.EndModal(wx.ID_OK)
        except Exception as e:
            if __debug__:
                import traceback
                traceback.print_exc()
            error_dialog = wx.MessageDialog(self, str(e), "Directory Path Error", style=wx.ICON_ERROR)
            error_dialog.CenterOnScreen()
            error_dialog.ShowModal()

    def get_result_file_paths(self): return self.result_file_paths
    def get_mnts_processes(self): return self.mnts_processes

class OverwriteDialog(wx.MessageDialog):
    """Dialog box to be displayed to give the user the option
    to overwrite the given existing files"""
    def __init__(self, parent, existing_files):
        existsStr = ["\n\t" + file_name for file_name in existing_files]
        existsStr = "".join(existsStr)
        wx.MessageDialog.__init__(self, __main__.frame, 
            "Files already exist in this directory. Are you sure "
            "you want to overwrite these files?\n" + existsStr,
            style=wx.YES_NO|wx.ICON_WARNING)