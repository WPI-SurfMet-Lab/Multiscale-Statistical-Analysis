
import os
import wx
import csv
import numpy as np
import pyautogui
import winreg
from re import sub
import winreg
from wx import TextCtrl, TreeCtrl
from wx.grid import Grid
from Workbook import Workbook
from _Resources import resource_path
from enum import IntEnum


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

    class _SensitivityOption(IntEnum, start=0):
        pass
    class _AnalysisOption(IntEnum, start=0):
        pass

    def open_sur(self, file_paths) -> None :
        """Takes an input of an array of strings for the file path of each surface being analyzed. These surfaces are
        input into MountainsMap using mouse and keyboard control. The user is then given a choice of selecting either
        length-scale, area-scale, or complexity analysis. These results are then record in various text files which are
        then also opened."""

        results_dir = get_surface_options()

        aboutInfo.CenterOnScreen()
        aboutInfo.ShowModal()
        
        wd = os.getcwd() + "\\"
        cmd_path = wd + "temp-cmds.txt"
        tmplt_path = resource_path("ssfa-template.mnt")
        results_dir = wd # TODO: Change this to fit input from popup
        result_file_paths = []

        for surf_file_path in file_paths :
            # Generate name for results file to be used
            sub()
            # Write external command file for MountainsMap
            cmd_file = open(cmd_path, "w")
            cmd_contents = [
                "SHOW",
                "LOAD_DOCUMENT \"" + tmplt_path + "\"",
                "AUTOSAVE OFF",
                "SUBSTITUTE_STUDIABLE \"" + surf_file_path + "\" 1 MULTILAYER_MODE=-1",
                "EXPORT_RESULTS \"" + result_path + "\"",
                "QUIT"
            ]
            cmd_file.writelines(cmd_contents)
            cmd_file.close()

            # Launch Mountains
            # subprocess.call()

            # Remove temporary script files
            subprocess.call(["rm -f \"" + cmd_path + "\""])

        # Open generated result text files
        open_file2(result_file_paths)

    def get_surface_options() :
        """
        """
        # TODO: Create popup that takes in scale-sensitive/complexity option, form of scale analysis, as well as
        #       the directory for storing the results files.
        # width, height = wx.DisplaySize()
        aboutInfo = wx.Dialog(frame, wx.ID_ANY, 'About ' + __name__ + ' ' + version, size=(480, 400))

        title_text = wx.StaticText(aboutInfo, wx.ID_ANY, label=__name__ + ' ' + version, pos=(60, 20),
                                   style=wx.ALIGN_CENTER_HORIZONTAL)
        title_text.SetFont(wx.Font(wx.FontInfo(14)).Bold())
        description_text = wx.StaticText(aboutInfo, wx.ID_ANY, label=description, pos=(45, 50),
                                         style=wx.ALIGN_CENTER_HORIZONTAL)

        github = wx.adv.HyperlinkCtrl(aboutInfo, id=wx.ID_ANY, label='Open-Source Code',
                                      url='https://github.com/MatthewSpofford/Multiscale-Statistical-Analysis',
                                      pos=(180, 150), style=wx.adv.HL_DEFAULT_STYLE)
        donate = wx.adv.HyperlinkCtrl(aboutInfo, id=wx.ID_ANY, label='Support Development',
                                      url='https://paypal.me/nrutkowski1?locale.x=en_US',
                                      pos=(173, 170), style=wx.adv.HL_DEFAULT_STYLE)
        lab_site = wx.adv.HyperlinkCtrl(aboutInfo, id=wx.ID_ANY, label='WPI Surface Metrology Lab',
                                        url='https://www.surfacemetrology.org/',
                                        pos=(159, 190), style=wx.adv.HL_DEFAULT_STYLE)

        line = wx.StaticLine(aboutInfo, id=wx.ID_ANY, pos=(10, 220), size=(450, -1), style=wx.LI_HORIZONTAL)

        d_title = wx.StaticText(aboutInfo, wx.ID_ANY, label='Developers', pos=(190, 240))
        d_title.SetFont(wx.Font(wx.FontInfo(11)).Bold())
        devs = wx.StaticText(aboutInfo, wx.ID_ANY, label=developers, pos=(178, 260), style=wx.ALIGN_CENTER_HORIZONTAL)

        okbtn = wx.Button(aboutInfo, wx.ID_OK, pos=(365, 325))

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