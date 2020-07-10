
import __main__
import os
import wx
import csv
import numpy as np
import pyautogui
import winreg
from re import sub
from wx import TextCtrl, TreeCtrl
from wx.grid import Grid
from Workbook import Workbook
import _Resources
from enum import Enum
import subprocess

# Class PlotData:
# the purpose of this class is to create an object which stores all of the data opened from files as well as user inputs
# contains two functions to read multi-scale data from either the .csv files from sfrax or the .txt files from MountainsMap
# which contains the scale, relative area / length, and complexity (as well as R^2 which I don't understand / use).
class PlotData:

    def __init__(self, error_text:TextCtrl, grid:Grid, wb:Workbook):

        # the error text object which allows for errors to be logged in the main window.
        self.error_text = error_text
        # saves a list of the scales from the data files. It is important that the data files that are opened at the same time
        # all have the same scales
        self.results_scale = []
        # list of relative areas read from the data files.
        self.relative_area = []
        # default text for the legend of the plot to distinguish the data by file name
        self.legend_text = []
        # set of relative area values used for regression analysis
        # this is sorted into lists which contains one value from each data file at a given scale.
        # thus there will be one list for each scale
        self.regress_sets = []
        # list to contain the x-values on the regression plots defined by the user for each data set opened
        # the default is text of the file name so when the user inputs x-values for regression they can distinguish them
        # based on data file name.
        self.x_regress = []
        # list to contain all complexity values from all files opened
        self.complexity = []

        self.strings = []
        self.grid = grid
        self.wb = wb

    # function to open .csv files from Sfrax
    # takes in a list of file paths for the files the user opens
    def open_file(self, file_paths):

        # logs opening in the window
        self.get_error_text().AppendText("Opening..." + '\n')
        # sets all lists of stored data to be empty
        self.set_results_scale([])
        self.set_relative_area([])
        self.set_legend_text([])
        self.set_regress_sets([])
        self.set_x_regress([])
        self.set_complexity([])

        # iterates over each file path in the list of file paths opened by the user
        for i in file_paths:
            file_path = i.split("\\")
            file_name = file_path[len(file_path)-1]
            # adds the file name to the legend text and x-regress list
            self.get_x_regress().append(file_name)
            self.get_legend_txt().append(file_name)
        # -- deprecated
        legendCount = 0
        # iterate over each file in the file path
        for file in file_paths:

            # create two temporary lists for each file, default empty
            tempList = []
            complexList = []

            # open the file as 'openfile'
            with open(file) as openfile:

                # create a reader for the .csv file
                reader = csv.reader(openfile, dialect='excel')
                # count the number of rows read in the .csv file this variable is deprecated
                rowCounter = 0
                # iterate over a list of rows in the .csv file
                for row in reader:
                    # to catch errors i.e. any text cannot be appended to a list since I convert it to a float first
                    # in the following lines.
                    try:
                        # the first value in the row is always either text, empty, of a value for the scale
                        # in this line the value is converted to a float() if it is text it will throw an error and skip
                        # to the next line. However a number can be converted to a float and will not throw an error
                        # checks if the value of the scale rounded to 4 decimal places is not yet in the list of scales
                        if not self.get_results_scale().__contains__(np.round_(float(row[0]), 4)):
                            # it then appends the value of the scale rounded to 4 decimal places to the list of scales if it is not already in the list
                            self.get_results_scale().append(np.round_(float(row[0]), 4))
                        # the second value in the row is always relative area (or length) which is rounded and appended to tempList
                        tempList.append(np.round_(float(row[1]), 4))
                        # the third value in the row is always complexity which is rounded and appended to complexList
                        complexList.append(np.round_(float(row[2]), 4))
                    # catch and log errors prints them to main window
                    except (ValueError, IndexError) as e:
                        self.get_error_text().AppendText("Open: " + str(e) + '\n')
                    # increase row counter -- deprecated
                    rowCounter += 1

                # reverse the tempList for area or length and complexList see below for scale explanation.
                tempList.reverse()
                complexList.reverse()
                # append these lists to relative area and complexity lists
                self.get_relative_area().append(tempList)
                self.get_complexity().append(complexList)
                # reverse the scales list. After the first file is opened this list should not change.
                # this is reversed so that the scales increase from left to right in the list
                self.get_results_scale().reverse()
                # increase legend counter -- deprecated
                legendCount += 1
            # close the file and open the next one in the list of file paths
            openfile.close()

        # iterate over all of the relative areas from each file at the same time
        # see example below
        for y_values in zip(*self.get_relative_area()):

            # y is the list of all relative areas at the same scale for the different data sets
            y = list(y_values)
            # these lists are then appended to regress sets such that
            # there is a list of relative areas for each scale.
            self.get_regress_sets().append(y)

        self.get_error_text().AppendText("Done." + '\n')

    # function to open .txt files from mountainsmap
    def open_file2(self, file_paths):

        self.get_error_text().AppendText("Opening..." + '\n')
        # set all lists to be empty
        self.set_results_scale([])
        self.set_relative_area([])
        self.set_legend_text([])
        self.set_regress_sets([])
        self.set_x_regress([])
        self.set_complexity([])
        self.set_strings([])

        s = []

        # iterates over each file path in the list of file paths opened by the user
        for i in file_paths:

            file_path = i.split("\\")
            file_name = file_path[len(file_path)-1]
            # adds the file name to the legend text and x-regress list
            self.get_x_regress().append(file_name)
            self.get_legend_txt().append(file_name)

        # iterate over each file to open each file and read the data
        for file in file_paths:

            # temp lists for each file to contain
            # relative area data
            tempList = []
            # complexity data
            complexList = []

            # Defines if the data values have been found, so float warnings can be ignored
            dataFound = False

            # open the file
            with open(file) as openfile:
                # Line number
                lineNum = 0
                # variable which contains a list of all of the lines in the text file
                lines = openfile.readlines()
                # iterate over each line in the text file
                for line in lines:
                    lineNum += 1 # Increase line counter
                    try:
                        # process text in file each line becomes a list of words and numbers
                        line = line.split("\t")
                        # the first value in the list is always either scale value or text
                        # if it is text a value error will be thrown here and is skipped
                        # otherwise check if the scale value is in the list of scales
                        scaleVal = np.sqrt(2*float(line[0]))
                        if not np.round_(scaleVal, 4) in self.get_results_scale():
                            # if not add the value to the list of scales
                            self.get_results_scale().append(np.round_(scaleVal, 4))
                            
                        # second value in the line is always relative area add to temp list
                        tempList.append(np.round_(float(line[1]), 4))
                        # third value in the line is always complexity add to temp list
                        complexList.append(np.round_(float(line[2]), 4))
                        # With the float conversions being successful, data has been found
                        dataFound = True
                    # throw and log errors
                    except ValueError as e:
                        s.append(line)
                        if dataFound :
                            self.get_error_text().AppendText("Open (" + openfile.name + ":" + str(lineNum) + "): " + str(e) + '\n')
                # append temp lists to complexity and relative area lists
                self.get_relative_area().append(tempList)
                self.get_complexity().append(complexList)
                self.set_strings(s)
            # close the file recursively open the next file
            openfile.close()

        # iterate over all of the relative areas from each file at the same time
        # see example below
        for y_values in zip(*self.get_relative_area()):

            # the list of all relative areas at the same scale for the different data sets
            # these lists are then appended to regress sets such that
            # there is a list of relative areas for each scale.
            self.get_regress_sets().append(list(y_values))

        # add data to workbook hopefully ----------------------------------------------------
        [print(x) for x in s]

        start = 5
        # scale of analysis
        add_data = {(start - 1, 0): s[3][0]}

        for num in range(start + 1, len(self.get_results_scale()) + 1 + start):

            add_data.__setitem__((num, 0), self.get_results_scale()[num - (1 + start)])

        for num in range(2, 2*len(self.get_legend_txt()) + 1, 2):

            add_data.__setitem__((start, int(num - 1)), self.get_legend_txt()[int(num / 2) - 1][:len(self.get_legend_txt()[int(num / 2) - 1]) - 4])
            # relative area
            add_data.__setitem__((start - 1, num - 1), s[3][1])
            add_data.__setitem__((start, int(num)), self.get_legend_txt()[int(num / 2) - 1][:len(self.get_legend_txt()[int(num / 2) - 1]) - 4])
            # Fractal complexity
            add_data.__setitem__((start - 1, num), s[3][2])

            for i in range(start + 1, len(self.get_relative_area()[int(num / 2) - 1]) + 1 + start):

                add_data.__setitem__((i, int(num - 1)), self.get_relative_area()[int(num / 2) - 1][i - (1 + start)])

            for i in range(start + 1, len(self.get_complexity()[int(num / 2) - 1]) + 1 + start):

                add_data.__setitem__((i, int(num)), self.get_complexity()[int(num / 2) - 1][i - (1 + start)])

        self.wb.set_data(add_data)
        self.get_grid().SetTable(self.wb)
        self.get_grid().AutoSizeColumns()
        self.get_grid().Refresh()

        self.get_error_text().AppendText("Done." + '\n')

    def open_sur(self, file_paths) -> None :
        """Takes an input of an array of strings for the file path of each surface being analyzed. These surfaces are
        input into MountainsMap using mouse and keyboard control. The user is then given a choice of selecting either
        length-scale, area-scale, or complexity analysis. These results are then record in various text files which are
        then opened seperatly."""
        # Initialize pyautogui
        orig_FAILSAFE = pyautogui.FAILSAFE
        orig_PAUSE = pyautogui.PAUSE
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 1 # second delay between each action

        result_file_paths, mnts_interact_funcs = get_surface_options(file_paths)
        if __debug__:
            print(result_file_paths, mnts_interact_funcs)

        # If the options were not selected, end file opening prematurely
        if not (result_file_paths and mnts_interact_funcs):
            return

        # Store directory locations for external cmds and mountains template
        cmd_path = os.path.join(os.sep, os.getcwd(), "temp-cmds.txt")
        tmplt_path = _Resources.resource_path("ssfa-template.mnt")

        # Store directory location for mountains executable
        mountains_path = _Resources.find_mountains_map()

        # Minimize all windows
        pyautogui.hotkey('win', 'd')

        mnts_instances = []
        # Generate result files for each selected surface
        for i, surf_file_path in enumerate(file_paths) :
            # Write external command file for MountainsMap
            with open(cmd_path, "w") as cmd_file :
                cmd_contents = [
                    "SHOW",
                    "LOAD_DOCUMENT \"" + tmplt_path + "\"",
                    "AUTOSAVE OFF",
                    "SUBSTITUTE_STUDIABLE \"" + surf_file_path + "\" 1 MULTILAYER_MODE=-1",
                ]
                cmd_file.write("\n".join(cmd_contents))
            # Launch Mountains for this current surface
            mnts_instances.append(subprocess.Popen(
                mountains_path, "/CMDFILE:\"" + cmd_path + "\"", "/NOSPLASHCREEN"))

            # Check to see if mountains has started, it hasn't wait
            while True:
                window_title = _Resources.get_foreground_window_title()
                if not window_title is None:
                    break
            # Start up and select mountains tab
            init_mountains()

        # Interact with Mountains and generate the result files
        for i in range(len(result_file_paths)) :
            mnts_interact_funcs[i]()
            mnts_instances[i].kill() # Terminate this instance of mountains, current job complete
            mnts_instances[i].wait() # Wait to see if this instance of mountains has terminated
            if not os.path.exists(result_file_paths[i]):
                raise FileNotFoundError("Could not find results file " + result_file_paths[i])

        # Revert pyautogui to old settings
        pyautogui.FAILSAFE = orig_FAILSAFE
        pyautogui.PAUSE = orig_PAUSE
        # Open generated result text files
        open_file2(result_file_paths)

    def get_relative_area(self): return self.relative_area
    def get_results_scale(self): return self.results_scale
    def get_legend_txt(self): return self.legend_text
    def get_regress_sets(self): return self.regress_sets
    def get_x_regress(self): return self.x_regress
    def set_x_regress(self, xrvals): self.x_regress = xrvals
    def set_results_scale(self, sclres): self.results_scale = sclres
    def set_relative_area(self, rarea): self.relative_area = rarea
    def set_regress_sets(self, rsets): self.regress_sets = rsets
    def set_legend_text(self, ltxt): self.legend_text = ltxt
    def get_error_text(self): return self.error_text
    def get_complexity(self): return self.complexity
    def set_complexity(self, comp): self.complexity = comp
    def get_grid(self): return self.grid
    def get_wb(self): return self.wb
    def set_wb(self, wb): self.wb = wb
    def get_strings(self): return self.strings
    def set_strings(self, string): self.strings = string

def init_mountains():
    """Use keyboard to startup MountainsMap.
    If the startup menu has not been disabled, then press enter to get rid of it"""
    # Open windows tab menu, and move to the back of the list where Mountains will be
    pyautogui.keyDown('alt')
    pyautogui.keyDown('shift')
    pyautogui.press('tab')
    # Get rid of startup/configuration menu if it is open
    pyautogui.press('enter')
    # Release keys
    pyautogui.keyUp('alt')
    pyautogui.keyUp('shift')

def interact_func(index, sensitivity_func, analysis_func, file_dir, file_name):
    """Defines how the mouse and keyboard will interact with MountainsMap"""
    from time import sleep
    # Open windows tab menu, move to the window corresponding to the surface
    # file being interacted with
    if index > 0:
        pyautogui.keyDown('alt')
        pyautogui.press('tab', presses=index)
        pyautogui.keyUp('alt')
    if __debug__:
        sleep(5)

    # Select ssfa graph
    pyautogui.press('tab')
    pyautogui.press('tab')
    if __debug__:
        sleep(5)

    # Select sensitivity and analysis options
    sensitivity_func()
    if __debug__:
        sleep(5)
    analysis_func()
    if __debug__:
        sleep(5)

    # Export result files --
    # Click on export button
    x, y = pyautogui.locateCenterOnScreen(_Resources.resource_path("export-curve.png"))
    pyautogui.click(x, y)
    # Enter file name
    pyautogui.typewrite(file_name)
    # Tab to file path
    pyautogui.press('tab', presses=6)
    # Right click on path menu
    pyautogui.hotkey('shit', 'f10')
    # Edit file path
    pyautogui.press('tab', presses=3)
    pyautogui.typewrite(file_dir)
    pyautogui.press('enter')
    # Highlight enter button
    pyautogui.keyDown('shift')
    pyautogui.press('tab', presses=4)
    if __debug__:
        sleep(5)
    # Exit file dialog
    pyautogui.press('enter')

def select_scale_sensitivity():
    """Select scale-sensitivity option"""
    x, y = pyautogui.locateCenterOnScreen(_Resources.resource_path("scale-sensitive.png"))
    pyautogui.click(x, y)

def select_complexity():
    """Select scale-sensitivity option"""
    x, y = pyautogui.locateCenterOnScreen(_Resources.resource_path("complexity.png"))
    pyautogui.click(x, y)

sensitivity_option_map = {}
class SensitivityOption(Enum):
    Scale = ("Scale-sensitive Analysis", select_scale_sensitivity)
    Complexity = ("Complexity Analysis", select_complexity)
    def __init__(self, label, func):
        self.label = label
        self.func = func
        # Assign label to function map
        global sensitivity_option_map
        sensitivity_option_map[label] = func

def select_analysis_option(pos):
    """Click on the analysis menu button to prepare for selecting the option"""
    x, y = pyautogui.locateCenterOnScreen(_Resources.resource_path("analysis-method.png"))
    pyautogui.click(x, y)

    # Select button at this pos
    pyautogui.press("down", presses=pos)
    pyautogui.press("enter")

analysis_option_map = {}
class AnalysisOption(Enum):
    LengthRows = ("Length Analysis (rows)", None)
    LengthColumns = ("Length Analysis (columns)", None)
    Area1Corner = ("Area Analysis (1 corner)", None)
    Area4Corners = ("Area Analysis (4 corners)", None)
    def __init__(self, label, func):
        self.label = label
        # Assign label to function map
        global analysis_option_map
        analysis_option_map[label] = func
        # Assign analysis option function
        self.func = lambda: select_analysis_option(len(analysis_option_map))

def get_results_data(file_paths, results_dir, sensitive_func, analysis_func):
    """Given the list of surface files and a results directory,
    generate the corresponding list of new file names and paths.
    Also generates mountains interaction functions."""
    file_count = len(file_paths)
    result_paths = []
    result_names = []
    mountains_interact_funcs = []
    for index, surfName in enumerate(file_paths):
        surfName = os.path.normpath(surfName) # Remove stray/double slashes
        surfName = os.path.splitext(surfName)[0] # Remove file extension
        surfName = os.path.basename(surfName) # Grab file name
        # Add to file lists
        result_paths.append(os.path.join(os.sep, results_dir, surfName + ".txt"))
        result_names.append(surfName)
        # Add to function list
        mountains_interact_funcs.append(
            lambda: interact_func(index, sensitive_func, analysis_func, results_dir, surfName))

    return result_paths, mountains_interact_funcs

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

def get_surface_options(file_paths) :
    """Create surface import options selection. This includes specifying scale/complexity sensitivity,
    the type of surface analysis being done, as well as the directory for saving the analysis data.
    @param file_paths - List of surface file paths that will be analyzed into result files.
    @return result_file_paths, mnts_interact_funcs. Array indexes line up with given file_paths."""
    result_file_paths = None
    mnts_interact_funcs = None

    width = 600
    height = 250
    options_dialog = wx.Dialog(__main__.frame, wx.ID_ANY, "Surface Import Options", size=(width, height))
    options_panel = wx.Panel(options_dialog, wx.ID_ANY)
    options_sizer = wx.BoxSizer(wx.VERTICAL)

    def getTypeCombo(enum):
        choices  = [choice.label for choice in enum]
        return wx.ComboBox(options_panel, wx.ID_OK, choices[0],
                                            style=wx.CB_SIMPLE | wx.CB_READONLY,
                                            choices=choices)
    # Analysis Type Selection
    analysis_label = wx.StaticText(options_panel, wx.ID_ANY, label="Analysis Type:")
    analysis_combo = getTypeCombo(AnalysisOption)

    # Sensitivity Type Selection
    sensitivity_label = wx.StaticText(options_panel, wx.ID_ANY, label="Sensitivity Type:")
    sensitivity_combo = getTypeCombo(SensitivityOption)

    # Initialize sizer for both combo boxes
    combo_sizer = wx.BoxSizer(wx.HORIZONTAL)
    analysis_sizer = wx.BoxSizer(wx.VERTICAL)
    sensitivity_sizer = wx.BoxSizer(wx.VERTICAL)
    # Initialize Analyasis sizer
    analysis_sizer.AddStretchSpacer()
    analysis_sizer.Add(analysis_label, flag=wx.ALIGN_LEFT)
    analysis_sizer.Add(analysis_combo, flag=wx.ALIGN_LEFT)
    analysis_sizer.AddStretchSpacer()
    # Initialize Sensitivity sizer
    sensitivity_sizer.AddStretchSpacer()
    sensitivity_sizer.Add(sensitivity_label, flag=wx.ALIGN_LEFT)
    sensitivity_sizer.Add(sensitivity_combo, flag=wx.ALIGN_LEFT)
    sensitivity_sizer.AddStretchSpacer()
    # Layout combo sizers
    combo_sizer.AddStretchSpacer()
    combo_sizer.Add(analysis_sizer, flag=wx.CENTER)
    combo_sizer.AddStretchSpacer()
    combo_sizer.Add(sensitivity_sizer, flag=wx.CENTER)
    combo_sizer.AddStretchSpacer()

    # Results folder selection button handling
    results_label = wx.StaticText(options_panel, wx.ID_ANY, label="Select Results Folder:")
    results_dir_dialog = wx.DirPickerCtrl(options_panel, wx.ID_ANY, message="Select Results Folder",
                                            style=wx.DIRP_DEFAULT_STYLE)

    # Completion button initialization
    completion_sizer = wx.BoxSizer(wx.HORIZONTAL)
    cancelBtn = wx.Button(options_panel, wx.ID_CANCEL, label="Cancel")
    okBtn = wx.Button(options_panel, wx.ID_ANY, label="Ok")
    completion_sizer.Add(cancelBtn, flag=wx.ALIGN_LEFT)
    completion_sizer.Add(okBtn, flag=wx.ALIGN_LEFT)

    # Bind ok button to handler
    def okBtnHandler(event):
        """Handles generation of result file names and mountains interaction functions
        when the user pressed the "ok" button."""
        try:
            # Get Output from combo box and directory picker
            selected_results_dir = results_dir_dialog.GetPath()

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

            sensitive_func = sensitivity_option_map[sensitivity_combo.GetStringSelection()]
            analysis_func = analysis_option_map[analysis_combo.GetStringSelection()]
            # Build new file path based on given surface files and results dir
            new_file_paths, new_mountains_funcs = \
                get_results_data(file_paths, selected_results_dir, sensitive_func, analysis_func)

            # Possibly overwrite check was requested
            already_exists = []
            if overwriteSearch:
                # Go through possibly file names and confirm if these files already exist
                for i, path in enumerate(new_file_paths):
                    if os.path.exists(path):
                        already_exists.append(path)
                # Display overwrite dialog if needed
                if already_exists:
                    overwrite_dialog = OverwriteDialog(options_dialog, already_exists)
                    # If the user requests to not overwrite these files, end early
                    if not overwrite_dialog.ShowModal() == wx.ID_YES:
                        return

            nonlocal result_file_paths, mnts_interact_funcs
            result_file_paths = new_file_paths
            mnts_interact_funcs = new_mountains_funcs
            options_dialog.EndModal(wx.ID_OK)
        except Exception as e:
            if __debug__:
                import traceback
                traceback.print_exc()
            error_dialog = wx.MessageDialog(options_dialog, str(e), "Directory Path Error", style=wx.ICON_ERROR)
            error_dialog.CenterOnScreen()
            error_dialog.ShowModal()
    # Bind button handler to "Ok" button
    options_dialog.Bind(wx.EVT_BUTTON, okBtnHandler, okBtn)

    # Final initialization of dialog's sizer
    options_sizer.AddStretchSpacer()
    options_sizer.Add(combo_sizer, flag=wx.CENTER)
    options_sizer.AddStretchSpacer()
    options_sizer.Add(results_label, flag=wx.CENTER)
    options_sizer.Add(results_dir_dialog, flag=wx.CENTER)
    options_sizer.AddStretchSpacer()
    options_sizer.Add(completion_sizer, flag=wx.CENTER)
    options_sizer.AddStretchSpacer()

    options_panel.SetSizerAndFit(options_sizer)
    options_panel.Refresh()
    options_dialog.CenterOnScreen()
    result = options_dialog.ShowModal()

    return result_file_paths, mnts_interact_funcs