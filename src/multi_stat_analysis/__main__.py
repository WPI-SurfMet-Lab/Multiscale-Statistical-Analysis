import warnings
warnings.simplefilter("error", RuntimeWarning)

import wx
import wx.adv
import wx.grid
import openpyxl

from Workbook import Workbook
from scipy.optimize import OptimizeWarning
from Dialogs import RegressionDialog
from Dialogs import GraphSelectDialog
from Dialogs import R2byScaleDialog
from Dialogs import SclbyAreaDialog
from Dialogs import XRValuesDialog
from Dialogs import HHPlotDialog
from PlotData import PlotData
from CanvasPanel import RegressionPlot as RP
from CanvasPanel import R2byScalePlot as R2
from StatsTestsUI import FtestDialog
from StatsTestsUI import TtestDialog
from StatsTestsUI import ANOVAtestDialog

#import faulthandler
#faulthandler.enable()

name = 'Multiscale Statisitcal Analysis'
__version__ = '0.3.0'
__license__ = 'MIT'
__author__ = 'Matthew Spofford, Nathaniel Rutkowski'
__author_email__ = 'mespofford@wpi.edu'
__url__ = 'https://github.com/MatthewSpofford/Multiscale-Statistical-Analysis'

global wb_counter
wb_counter = 1
global wb_list
wb_list = []
global frame
frame = None
global app
app = None

# function for show the curve fit dialog and get regression graphs
def OnRegression(event):

    selectedID = getPlotDataID()
    data = tree_menu.GetItemData(selectedID)

    warnings.simplefilter("error", OptimizeWarning)
    try:
        rsdlg = GraphSelectDialog(frame, data.get_results_scale(), data.get_x_regress(), data.get_regress_sets(),
                                  error_txt)
        rsdlg.CenterOnScreen()
        resid = rsdlg.ShowModal()

        if resid == wx.ID_OK:
            # Contains list of regression/R^2 dialog properties, checked value functions, and graph generators
            # Tuple Layout
            #   [0] - IsChecked property retrival function
            #   [1] - Dialog title
            #   [2] - Fit plot function to generate regression
            #   [3] - Tree menu item label
            #   [4] - Error dialog label
            #   [5] - Boolean is true if the dialog is for an R^2 dialog
            regressR2Dialogs = (
                (rsdlg.prop1check.IsChecked,"Proportional",RP.proportional_fit_plot,"Proportional Regression","Proportional: ", False),
                (rsdlg.lin1check.IsChecked,"Linear",RP.linear_fit_plot,"Linear Regression","Linear: ", False),
                (rsdlg.quad1check.IsChecked,"Quadratic",RP.quadratic_fit_plot,"Quadratic Regression","Quadratic: ", False),
                (rsdlg.cubic1check.IsChecked,"Cubic",RP.cubic_fit_plot,"Cubic Regression","Cubic: ", False),
                (rsdlg.quart1check.IsChecked,"Quartic",RP.quartic_fit_plot,"Quartic Regression","Quartic: ", False),
                (rsdlg.quint1check.IsChecked,"Quintic",RP.quintic_fit_plot,"Quintic Regression","Quintic: ", False),
                (rsdlg.pow1check.IsChecked,"Power",RP.power_fit_plot,"Power Regression","Power: ", False),
                (rsdlg.inverse1check.IsChecked,"Inverse",RP.inverse_fit_plot,"Inverse Regression","Inverse: ", False),
                (rsdlg.insq1check.IsChecked,"Inverse Square",RP.inverse_squared_fit_plot,"Inverse Square Regression","Inverse Square: ", False),
                (rsdlg.nexp1check.IsChecked,"Natural Exponent",RP.naturalexp_fit_plot,"Natural Exponent Regression","Natural Exponent: ", False),
                (rsdlg.Ln1check.IsChecked,"Natural Log",RP.loge_fit_plot,"Natural Log Regression","Natural Log: ", False),
                (rsdlg.b10log1check.IsChecked,"Base-10 Log",RP.log10_fit_plot,"Base-10 Log Regression","Log10: ", False),
                (rsdlg.invexp1check.IsChecked,"Inverse Exponent",RP.inverseexp_fit_plot,"Inverse Exponent Regression","Inverse Exponent: ", False),
                (rsdlg.sin1check.IsChecked,"Sine",RP.sin_fit_plot,"Sine Regression","Sine: ", False),
                (rsdlg.cos1check.IsChecked,"Cosine",RP.cos_fit_plot,"Cosine Regression","Cosine: ", False),
                (rsdlg.gauss1check.IsChecked,"Gaussian",RP.gaussian_fit_plot,"Gaussian Regression","Gaussian: ", False),
                (rsdlg.prop2check.IsChecked,"R^2 by Scale for Proportional Regression",R2.proportional_plot,"Proportional R^2 - Scale","Proportional R^2: ", True),
                (rsdlg.lin2check.IsChecked,"R^2 by Scale for Linear Regression",R2.linear_plot,"Linear R^2 - Scale","Linear R^2: ", True),
                (rsdlg.quad2check.IsChecked,"R^2 by Scale for Quadratic Regression",R2.quadratic_plot,"Quadratic R^2 - Scale","Quadratic R^2: ", True),
                (rsdlg.cubic2check.IsChecked,"R^2 by Scale for Cubic Regression",R2.cubic_plot,"Cubic R^2 - Scale","Cubic R^2: ", True),
                (rsdlg.quart2check.IsChecked,"R^2 by Scale for Quartic Regression",R2.quartic_plot,"Quartic R^2 - Scale","Quartic R^2: ", True),
                (rsdlg.quint2check.IsChecked,"R^2 by Scale for Quintic Regression",R2.quintic_plot,"Quintic R^2 - Scale","Quintic R^2: ", True),
                (rsdlg.pow2check.IsChecked,"R^2 by Scale for Power Regression",R2.power_plot,"Power R^2 - Scale","Power R^2: ", True),
                (rsdlg.inverse2check.IsChecked,"R^2 by Scale for Inverse Regression",R2.inverse_plot,"Inverse R^2 - Scale","Inverse R^2: ", True),
                (rsdlg.insq2check.IsChecked,"R^2 by Scale for Inverse Squared Regression",R2.inverse_squared_plot,"Inverse Square R^2 - Scale","Inverse Squared R^2: ", True),
                (rsdlg.nexp2check.IsChecked,"R^2 by Scale for Natural Exponent Regression",R2.natural_exp_plot,"Natural Exponent R^2 - Scale","Natural Exponent R^2: ", True),
                (rsdlg.Ln2check.IsChecked,"R^2 by Scale for Natural Log Regression",R2.loge_plot,"Natural Log R^2 - Scale","Natural Log R^2: ", True),
                (rsdlg.b10log2check.IsChecked,"R^2 by Scale for Log Regression",R2.log10_plot,"Base-10 R^2 - Scale","Log10 R^2: ", True),
                (rsdlg.invexp2check.IsChecked,"R^2 by Scale for Inverse Exponent Regression",R2.inverse_exp_plot,"Inverse Exponent R^2 - Scale","Inverse Exponent R^2: ", True),
                (rsdlg.sin2check.IsChecked,"R^2 by Scale for Sine Regression",R2.sin_plot,"Sine R^2 - Scale","Sine R^2: ", True),
                (rsdlg.cos2check.IsChecked,"R^2 by Scale for Cosine Regression",R2.cos_plot,"Cosine R^2 - Scale","Cosine R^2: ", True),
                (rsdlg.gauss2check.IsChecked,"R^2 by Scale for Gaussian Regression",R2.gaussian_plot,"Gaussian R^2 - Scale","Gaussian R^2: ", True))

            # Run through all given dialogs to find if the given option has been selected
            # If it has been selected, generate the corresponding graph dialog, and graph
            id = 0
            for dialog in regressR2Dialogs:
                checked_func, title, fit_func, menu_label, error_label, isR2 = dialog
                # Continue if this plot fit option been selected
                if checked_func():
                    try:
                        # Generate either R^2 or Regression dialog depending on selection
                        if isR2:
                            gdlg = R2byScaleDialog(frame, title, data, error_txt, tree_menu, selectedID, id)
                        else:
                            gdlg = RegressionDialog(frame, title, data.get_results_scale(), data.get_x_regress(),
                                                        data.get_regress_sets(), selectedID, tree_menu)
                        fit_func(gdlg.get_graph())
                        tree_menu.AppendItem(selectedID, menu_label, data=gdlg)
                        break
                    except (ZeroDivisionError, RuntimeError, Exception, Warning, TypeError, RuntimeWarning, OptimizeWarning) as e:
                        error_txt.AppendText(error_label + str(e) + '\n')
                # Don't increase ID if current dialog is not an R^2 dialog
                id += 1 if isR2 else 0

            # Refresh tree menu to show newly created graphs
            tree_menu.Refresh()
    except (ZeroDivisionError, RuntimeError, Exception, Warning, TypeError, RuntimeWarning, OptimizeWarning) as e:
        error_txt.AppendText("Graph: " + str(e) + '\n')

# function to get the x-regression values
def OnData(event):
    data = tree_menu.GetItemData(getPlotDataID())

    datadialog = XRValuesDialog(frame, data.get_x_regress())
    datadialog.CenterOnScreen()
    result = datadialog.ShowModal()

    if result == wx.ID_OK:
        datadialog.SaveString()
        data.set_x_regress(datadialog.get_xvals())

class DiscrimTests:
    """Contains list of discrimination test dialog properties
    [0] - Function for creating the dialogs
    [1] - Error dialog label"""
    Ftest = (FtestDialog, "F-test:")
    Ttest = (TtestDialog, "T-test:")
    Anova = (ANOVAtestDialog, "Anova:")

def OnDiscrimTests(test_choice):
    selected_test_func, test_str = test_choice

    selectedID = getPlotDataID()
    data = tree_menu.GetItemData(selectedID)

    try:
        dlg = selected_test_func(frame, data, error_txt, tree_menu, selectedID)
    except (ZeroDivisionError, RuntimeError, Exception, Warning, TypeError, RuntimeWarning, OptimizeWarning) as e:
        error_txt.AppendText(test_str + " " + str(e) + '\n')

    dlg.CenterOnScreen()
    dlg.ShowModal()
    tree_menu.Refresh()

# function to show F-test dialog
def OnFtest(event):
    OnDiscrimTests(DiscrimTests.Ftest)

# current: paired two tails t-test, which one should I use or options...?
# function to show T-test dialog
def OnTtest(event):
    OnDiscrimTests(DiscrimTests.Ttest)

# function to show the ANOVA test dialog
def OnANOVA(event):
    OnDiscrimTests(DiscrimTests.Anova)

class ScalePlots:
    """Contains list of scale plot dialog properties
    [0] - Error dialog label string
    [1] - Dialog title string
    [2] - Function for creating the dialogs
    [3] - Tree menu label string
    [4] - Graph y-axis label"""
    Area = ("Area-Scale Graph:", "Scale by Relative Area", data.get_relative_area, "Relative Area - Scale", None),
    Complexity = ("Complexity-Scale Graph:", "Scale by Complexity", data.get_complexity, "Complexity - Scale", "Complexity")

def OnScalePlot(plot_choice):
    selectedID = getPlotDataID()
    data = tree_menu.GetItemData(selectedID)
    plot_str, title, scale_func, menu_text, y_label = plot_choice

    if data is None :
        error_txt.AppendText(plot_str + " No data given\n")

    gdlg = SclbyAreaDialog(frame, title, data.get_results_scale(),
                             scale_func(),
                             data.get_legend_txt(), data)
    if not y_label == None:
        gdlg.get_graph().get_axes().set_ylabel(y_label)
        print(y_label)

    try:
        gdlg.get_graph().draw_plot()
        tree_menu.AppendItem(parent=selectedID, text=menu_text, data=gdlg)
        tree_menu.Refresh()
    except (RuntimeError, ZeroDivisionError, Exception, Warning, TypeError, RuntimeWarning, OptimizeWarning) as e:
         error_txt.AppendText(plot_str + " " + str(e) + '\n')

# function to create the scale area plot
def OnAreaPlot(event):
    OnScalePlot(ScalePlots.Area)

# function to create the scale complexity plot
def OnComplexityPlot(event):
    OnScalePlot(ScalePlots.Complexity)

def OnHHPlot(event):
    gdlg19 = HHPlotDialog(frame, 'Height-Height Plot')
    gdlg19.CenterOnScreen()
    resid = gdlg19.Show()
    tree_menu.Refresh()

# function to get selected graph on left side of main screen
def OnSelection(event):
    selected = tree_menu.GetItemData(tree_menu.GetSelection())

    if isinstance(selected, PlotData):
        selectedWb = selected.get_wb()
        selected.get_error_text().AppendText("Wb: Switching to -- " + selectedWb.get_name() + "\n")
        grid.SetTable(selectedWb)
        grid.AutoSizeColumns()
        grid.Refresh()
    else:
        selected.CenterOnScreen()
        selected.Show()

# function to rename selected graphs/workbooks
def OnRename(event):
    selectedID = tree_menu.GetSelection()
    selected = tree_menu.GetItemData(selectedID)
    newName = event.GetLabel()

    if isinstance(selected, PlotData):
        error_txt.AppendText("Wb: Renaming `" + selected.get_wb().get_name() + "` to `" + newName + "`\n")
        selected.get_wb().set_name(newName)
    else:
        pass

# function to display dialog about the software
def OnAbout(event):
    version = 'v' + __version__
    description = 'An Open-Source, Python-Based application to perform multi-scale \n' \
                  'regression and discrimination analysis using results from Surfract\n' \
                  'and MountainsMap. Developed in collaboration with Christopher A.\n' \
                  'Brown, Ph.D., PE, and the WPI Surface Metrology Lab. Contact\n' \
                  'mespofford@wpi.edu for details. You can support the development of this\n' \
                  'software by donating below.\n'

    # Reconfigure author strings to use newline seperate and not comma seperation
    developers = "\n".join(__author__.split(", "))

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

    aboutInfo.CenterOnScreen()
    aboutInfo.ShowModal()

# function to open the data files
def OnOpen(event):
    frame.EnableCloseButton(False)
    output = False
    try:
        # create the open file dialog
        openFileDialog = wx.FileDialog(frame, "Open",
                                       wildcard=
                                       "MountainsMap Surface Files (*.sur)|*.sur|"    
                                       "Comma Seperated Values - UTF-8 (*.csv)|*.csv|"
                                       "Text File (*.txt)|*.txt",
                                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)
        openFileDialog.CenterOnScreen()
        # shows the dialog on screen
        result = openFileDialog.ShowModal()
        # only opens the file if 'open' in dialog is pressed otherwise if 'cancel' in dialog is pressed closes dialog
        if result == wx.ID_OK:
            # gets the file path
            filepath = openFileDialog.GetPaths()
            data = tree_menu.GetItemData(getPlotDataID())

            # opens the file and reads it
            if filepath[0][len(filepath[0]) - 3:len(filepath[0])] == 'csv':
                data.open_file(filepath)
            if filepath[0][len(filepath[0]) - 3:len(filepath[0])] == 'txt':
                data.open_file2(filepath)
            if filepath[0][len(filepath[0]) - 3:len(filepath[0])] == 'sur':
                data.open_sur(filepath)
            output = True
        elif result == wx.ID_CANCEL:
            output = False
    except (Exception) as e:
        error_txt.AppendText("File Open: " + str(e) + '\n')
    finally:
        frame.EnableCloseButton(True)
        return output

def OnNewWB(event):

    global wb_counter
    global root

    grid.ClearGrid()
    d = {}
    table = Workbook(d, 'workbook{}'.format(wb_counter), grid.GetNumberRows(), grid.GetNumberCols())
    data = PlotData(error_txt, grid, table)
    grid.SetTable(table)

    item = tree_menu.AppendItem(root, table.name, data=data)
    tree_menu.SelectItem(item)

    error_txt.AppendText('Wb: New Workbook Created -- ' + table.name + '\n')
    wb_counter += 1

def getPlotDataID() :
    global tree_menu
    selectedID = tree_menu.GetSelection()
    selected = tree_menu.GetItemData(selectedID)

    # Check if currently selected node is not plot data
    # If plotdata is not found, go up the tree
    while not isinstance(selected, PlotData) :
        selectedID = tree_menu.GetItemParent(selectedID)
        selected = tree_menu.GetItemData(selectedID)

    return selectedID

def OnSave(event):
    frame.EnableCloseButton(False)
    output = False
    try:
        selectedID = getPlotDataID()
        selectedWorkbook = tree_menu.GetItemData(selectedID).get_wb()

        saveFileDialog = wx.FileDialog(frame, "Save", selectedWorkbook.name, "xlsx (*.xlsx)|*.xlsx", style=wx.FD_SAVE)
        saveFileDialog.CenterOnScreen()
        # shows the dialog on screen when pushes button
        result = saveFileDialog.ShowModal()
        # only saves the file if 'save' in dialog is pressed otherwise if 'cancel' in dialog is pressed closes dialog
        if result == wx.ID_OK:
            # gets the file path
            filepath = saveFileDialog.GetPath()

            cells = selectedWorkbook.get_data().keys()
            values = selectedWorkbook.get_data().values()

            file = openpyxl.Workbook()
            sheet = file.worksheets[0]

            for item in zip(cells, values):

                sheet.cell(row=item[0][0] + 1, column=item[0][1] + 1).value = str(item[1])

            file.save(filepath)
            output = True
        elif result == wx.ID_CANCEL:
            output = False
    except e:
        error_txt.AppendText("File Save: " + str(e) + '\n')
    finally:
        frame.EnableCloseButton(True)
        return output

# function to handle window maximization
def OnMaxmizeRestore(event):
    global resized
    global frame
    global width, height

    # Shrinks the window at initial resizing
    if frame.IsMaximized() :
        pass
    else:
        if not resized:
            screen = wx.DisplaySize()
            width = screen[0]
            height = screen[1]
            frame.SetSize(0, 0, int(width/1.5), int(height/1.5), sizeFlags=wx.SIZE_AUTO)
            frame.CenterOnScreen()
            resized = True
        else:
            pass

# function to exit the software
def OnExit(event):
    frame.EnableCloseButton(False)
    exitdialog = wx.MessageDialog(frame, "Are you sure you want to quit?", "Exit",
                                  style=wx.YES | wx.NO | wx.ICON_EXCLAMATION)
    exitdialog.SetSize(300, 200)
    exitdialog.CenterOnScreen()
    result = exitdialog.ShowModal()

    if result == wx.ID_YES:
        frame.Destroy()
        return True

    if result == wx.ID_NO:
        frame.EnableCloseButton(True)
        exitdialog.Destroy()
        return False


if __name__ == "__main__":
    app = wx.App(redirect=False)
    resized = False

    # sets the size of the window to be the size of the users computer screen can be set to integers instead
    screen = wx.DisplaySize()
    width = screen[0]
    height = screen[1]

    frame = wx.Frame(None, title='Multiscale Analysis')
    frame.SetSize(0, 0, width, height, sizeFlags=wx.SIZE_AUTO)
    frame.SetBackgroundColour('#ffffff')
    frame.EnableCloseButton(enable=True)
    frame.Bind(wx.EVT_CLOSE, OnExit)
    frame.Bind(wx.EVT_SIZE, OnMaxmizeRestore)

    # this is a bunch of GUI stuff
    # create the menu bar and populate it
    filemenu = wx.Menu()
    openitem = wx.MenuItem(parentMenu=filemenu, id=wx.ID_OPEN, text="Open")
    openfile = filemenu.Append(openitem)
    new_wb = filemenu.Append(wx.ID_ANY, 'New Workbook', 'New Workbook')
    frame.Bind(wx.EVT_MENU, OnNewWB, new_wb)
    save = wx.MenuItem(filemenu, wx.ID_SAVEAS, 'Save As')
    frame.Bind(wx.EVT_MENU, OnSave, save)
    filemenu.Append(save)
    # bind functions to menu objects
    about = wx.MenuItem(filemenu, wx.ID_ABOUT, 'About')
    filemenu.Append(about)
    exitprogram = wx.MenuItem(filemenu, wx.ID_CLOSE, 'Exit')
    filemenu.Append(exitprogram)


    # Regression menu initialization
    regres_menu = wx.Menu()
    xyvals = regres_menu.Append(wx.ID_ANY, 'Regression Values', 'Regression Values')
    regression = regres_menu.Append(wx.ID_ANY, 'Curve Fit', 'Curve Fit')
    # bind functions to menu objects
    frame.Bind(wx.EVT_MENU, OnData, xyvals)
    frame.Bind(wx.EVT_MENU, OnRegression, regression)

    # Discrimination menu initialization
    discrim_menu = wx.Menu()
    ftest = discrim_menu.Append(wx.ID_ANY, 'F-test', 'F-test')
    ttest = discrim_menu.Append(wx.ID_ANY, 'T-test', 'T-test')
    anova = discrim_menu.Append(wx.ID_ANY, 'ANOVA (one-way)', 'ANOVA (one-way)')
    # bind functions to menu objects
    frame.Bind(wx.EVT_MENU, OnFtest, ftest)
    frame.Bind(wx.EVT_MENU, OnTtest, ttest)
    frame.Bind(wx.EVT_MENU, OnANOVA, anova)

    graphmenu = wx.Menu()
    area_scale = graphmenu.Append(wx.ID_ANY, 'Area - Scale Plot', 'Area - Scale Plot')
    comp_scale = graphmenu.Append(wx.ID_ANY, 'Complexity - Scale Plot', 'Complexity - Scale Plot')
    HHplot = graphmenu.Append(wx.ID_ANY, 'Height-Height Plot', 'Height-Height Plot')
    frame.Bind(wx.EVT_MENU, OnAreaPlot, area_scale)
    frame.Bind(wx.EVT_MENU, OnComplexityPlot, comp_scale)
    frame.Bind(wx.EVT_MENU, OnHHPlot, HHplot)

    menuBar = wx.MenuBar()
    menuBar.Append(filemenu, 'File')
    menuBar.Append(regres_menu, 'Regression')
    menuBar.Append(discrim_menu, 'Discrimination')
    menuBar.Append(graphmenu, 'Graphs')
    frame.SetMenuBar(menuBar)
    frame.Bind(wx.EVT_MENU, OnOpen, openfile)
    frame.Bind(wx.EVT_MENU, OnExit, exitprogram)
    frame.Bind(wx.EVT_CLOSE, OnExit)
    frame.Bind(wx.EVT_MENU, OnAbout, about)

    # splits the main window into 3 sections, main empty space, side bar with graphs, error logging window
    vsplitter = wx.SplitterWindow(frame)
    vsplitter.SetBackgroundColour('#ffffff')
    hsplitter = wx.SplitterWindow(vsplitter)


    # -------------------------------------------------------------------------------------------------------
    v_sizer = wx.BoxSizer(wx.VERTICAL)
    h_sizer = wx.BoxSizer(wx.VERTICAL)


    # main panel with workbook view
    main_panel = wx.Panel(hsplitter, style=wx.SIMPLE_BORDER)
    main_panel.SetBackgroundColour('#ffffff')

    main_sizer = wx.BoxSizer(wx.VERTICAL)

    # --------------------------------------------------------------------------------------------------
    h_sizer.Add(main_panel, 1, wx.EXPAND)
    main_panel.Layout()
    main_panel.SetSizerAndFit(main_sizer)

    # error panel for error logging
    error_panel = wx.Panel(hsplitter, style=wx.BORDER_SUNKEN)

    # ------------------------------------------------------------------------------------------------------
    h_sizer.Add(error_panel, 1, wx.EXPAND)

    # left panel for holding workbook trees on left
    left_panel = wx.Panel(vsplitter, style=wx.SIMPLE_BORDER)

    # ---------------------------------------------------------------------------------------------------------
    v_sizer.Add(left_panel, 1, wx.EXPAND)

    # create the error text box which displays the text for errors
    error_sizer = wx.BoxSizer(wx.VERTICAL)
    error_txt = wx.TextCtrl(error_panel, style=wx.TE_READONLY | wx.TE_MULTILINE)
    error_txt.SetBackgroundColour('#000000')
    error_txt.SetForegroundColour('#ff8d00')
    error_sizer.Add(error_txt, 1, wx.EXPAND)
    error_panel.SetSizer(error_sizer)
    hsplitter.SplitHorizontally(main_panel, error_panel, sashPosition=580)
    vsplitter.SplitVertically(left_panel, hsplitter, sashPosition=200)
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(vsplitter, 1, wx.EXPAND)
    # tree which contains the graphs when created, names can be editted
    tree_sizer = wx.BoxSizer(wx.VERTICAL)
    tree_menu = wx.TreeCtrl(left_panel, style=wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT | wx.TR_SINGLE |
                                              wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_EDIT_LABELS)
    root = tree_menu.AddRoot("graphs-root")
    tree_sizer.Add(tree_menu, 1, wx.EXPAND)
    left_panel.SetSizer(tree_sizer)
    frame.Bind(wx.EVT_TREE_ITEM_ACTIVATED, OnSelection, tree_menu)
    frame.Bind(wx.EVT_TREE_END_LABEL_EDIT, OnRename, tree_menu)

    main_sizer.Clear()
    main_sizer.Layout()
    grid = wx.grid.Grid(main_panel, wx.ID_ANY, style=wx.HSCROLL | wx.VSCROLL | wx.ALWAYS_SHOW_SB)

    main_sizer.Add(grid, 1, wx.EXPAND)
    main_panel.SetSizer(main_sizer)
    grid.CreateGrid(1000, 100)

    OnNewWB(wx.EVT_ACTIVATE_APP)

    frame.Maximize(True)
    frame.CenterOnScreen()
    frame.Layout()
    frame.SetSizer(sizer)
    frame.Show()
    app.MainLoop()
else:
    pass