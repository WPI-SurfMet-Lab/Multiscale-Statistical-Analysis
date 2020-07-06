
import warnings

import numpy as np
import wx
import multi_stat_analysis.CurveFit
from wx.lib.scrolledpanel import ScrolledPanel
from scipy.optimize import OptimizeWarning
from multi_stat_analysis.CanvasPanel import R2byScalePlot
from multi_stat_analysis.CanvasPanel import RegressionPlot
from multi_stat_analysis.CanvasPanel import SclbyAreaPlot
from multi_stat_analysis.CanvasPanel import HHPlot
from multi_stat_analysis.GraphDialogs import SymbolDialog
from multi_stat_analysis.GraphDialogs import LegendDialog
from multi_stat_analysis.GraphDialogs import LabelDialog

# Class for the dialog to select the curve fitting types and graphs
# From the main menu under Analysis > Curve Fit
# select Regression and R^2 by scale graphs, get best fitting curve
class GraphSelectDialog(wx.Dialog):
    # this is all a bunch of UI stuff
    def __init__(self, parent, scale_data, x_regress_vals, y_regress_vals, errtext):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Curve Fit", size=(840, 680))
        self.panel = wx.Panel(self, wx.ID_ANY)
        CurveFit.set_maxfev(1000)

        # -------------------------------------------REGRESSION TYPE SELECTION------------------------------------------------------------------REGRESSION TYPE SELECTION-----------------------
        self.regress_box = wx.StaticBox(self.panel, wx.ID_ANY, "Curve Type", size=(420, 150), pos=(10,10))
        # -- creating the list box --
        self.regress_selection = wx.ListCtrl(self.regress_box, id=wx.ID_ANY, size=(400, 125), style=wx.LC_REPORT |
                                                                                              wx.LC_NO_HEADER |
                                                                                              wx.NO_BORDER, pos=(10,20))
        self.regress_selection.SetBackgroundColour('#f0f0f0')
        self.regress_selection.InsertColumn(0, "0", width=150)
        self.regress_selection.InsertColumn(1, "1", width=220)
        # -- choices in list box --
        self.choices = [["Proportional", "A*x"],
                        ["Linear", "m*x + b"],
                        ["Quadratic", "A*x^2 + B*x + C"],
                        ["Cubic", "A+B*x+C*x^2+D*x^3"],
                        ["Quartic", "A+B*x+C*x^2+D*x^3+E*x^4"],
                        ["Quintic", "A+B*x+C*x^2+D*x^3+E*x^4+F*x^5"],
                        ["Power", "A*x^B"],
                        ["Inverse", "A/x"],
                        ["Inverse Square", "A/x^2"],
                        ["Natural Exponent", "A*exp(-C*x)+B"],
                        ["Natural Log", "A*ln(B*x)"],
                        ["Base-10 Log", "A*log(B*x)"],
                        ["Inverse Exponent", "A*(1-exp(-C*x))+B"],
                        ["Sine", "A*sin(B*x+C)+D"],
                        ["Cosine", "A*cos(B*x+C)+D"],
                        ["Gaussian", "A*exp(-(x-B)^2/C^2)+D"]]
        [self.regress_selection.Append(i) for i in self.choices]

        # --------------------------- handles item list selection --------------------------
        # -- selected items --
        self.selectedList = []
        # -- bind functions to get selected values in ListCtrl --
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect, self.regress_selection)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnDeselect, self.regress_selection)

        # --------------------------------------DISPLAY GRAPHS---------------------------------------------------------------------------------------------DISPLAY GRAPHS-------------------
        # -- box to contain all check boxes --
        self.display_box = wx.StaticBox(self.panel, wx.ID_ANY, "Graph Display", size=(490, 400), pos=(10,170))

        # general graphs that can be generated without selecting regression type ---------
        # self.gen_plot_box = wx.StaticBox(self.display_box, wx.ID_ANY, "General", size=(110, 65))
        # self.gen_plot_box.SetPosition((10, 25))
        # self.sclxarea_check = self.checkBox(self.gen_plot_box, "Scale by Area")
        # self.sclxarea_check.SetPosition((10,20))
        # self.sclxcomplex_check = self.checkBox(self.gen_plot_box, "Scale by Complexity")
        # self.sclxcomplex_check.SetPosition((10, 40))

        # ---------------------------- selecting graphs to displaye for regression types -----------------
        self.prop_plot_box, self.prop1check, self.prop2check = self.displayBox("Proportional")
        self.lin_plot_box, self.lin1check, self.lin2check = self.displayBox("Linear")
        self.quad_plot_box, self.quad1check, self.quad2check = self.displayBox("Quadratic")
        self.cubic_plot_box, self.cubic1check, self.cubic2check = self.displayBox("Cubic")
        self.quart_plot_box, self.quart1check, self.quart2check = self.displayBox("Quartic")
        self.quint_plot_box, self.quint1check, self.quint2check = self.displayBox("Quintic")
        self.pow_plot_box, self.pow1check, self.pow2check = self.displayBox("Power")
        self.inverse_plot_box, self.inverse1check, self.inverse2check = self.displayBox("Inverse")
        self.insq_plot_box, self.insq1check, self.insq2check = self.displayBox("Inverse Square")
        self.nexp_plot_box, self.nexp1check, self.nexp2check = self.displayBox("Natural Exponent")
        self.Ln_plot_box, self.Ln1check, self.Ln2check = self.displayBox("Natural Log")
        self.b10log_plot_box, self.b10log1check, self.b10log2check = self.displayBox("Base-10 Log")
        self.invexp_plot_box,self.invexp1check, self.invexp2check = self.displayBox("Inverse Exponent")
        self.sin_plot_box, self.sin1check, self.sin2check = self.displayBox("Sine")
        self.cos_plot_box, self.cos1check, self.cos2check = self.displayBox("Cosine")
        self.gauss_plot_box, self.gauss1check, self.gauss2check = self.displayBox("Gaussian")
        # -- list of all sizers with type tag --
        self.sizerList = [["Proportional", self.prop_plot_box, self.prop1check, self.prop2check],
                          ["Linear", self.lin_plot_box, self.lin1check, self.lin2check],
                          ["Quadratic", self.quad_plot_box, self.quad1check, self.quad2check],
                          ["Cubic", self.cubic_plot_box, self.cubic1check, self.cubic2check],
                          ["Quartic", self.quart_plot_box, self.quart1check, self.quart2check],
                          ["Quintic", self.quint_plot_box, self.quint1check, self.quint2check],
                          ["Power", self.pow_plot_box, self.pow1check, self.pow2check],
                          ["Inverse", self.inverse_plot_box, self.inverse1check, self.inverse2check],
                          ["Inverse Square", self.insq_plot_box, self.insq1check, self.insq2check],
                          ["Natural Exponent", self.nexp_plot_box, self.nexp1check, self.nexp2check],
                          ["Natural Log", self.Ln_plot_box, self.Ln1check, self.Ln2check],
                          ["Base-10 Log", self.b10log_plot_box, self.b10log1check, self.b10log2check],
                          ["Inverse Exponent", self.invexp_plot_box, self.invexp1check, self.invexp2check],
                          ["Sine", self.sin_plot_box, self.sin1check, self.sin2check],
                          ["Cosine", self.cos_plot_box, self.cos1check, self.cos2check],
                          ["Gaussian", self.gauss_plot_box, self.gauss1check, self.gauss2check]]
        self.points = [(10,25),  (10,100),  (10,175),  (10,250),  (10,325),
                       (130,25), (130,100), (130,175), (130,250), (130,325),
                       (250,25), (250,100), (250,175), (250,250), (250,325),
                       (370,25), (370,100), (370,175), (370,250), (370,325)]

        self.hideAll()

        # --------------------------------BEST REGRESSION RELATIONSHIP BASED ON R^2---------------------------------------------

        self.find_best_box = wx.StaticBox(self.panel, wx.ID_ANY, "Best Fit", size=(290,400), pos=(520,170))
        self.best_fit_txt = wx.StaticText(self.find_best_box, -1, "Curve Fit: ", pos=(20,25))
        self.best_R2_txt = wx.StaticText(self.find_best_box, -1, "R^2: ", pos=(20,50))
        self.best_scale_txt = wx.StaticText(self.find_best_box, -1, "Scale: ", pos=(20,75))

        self.try_best = wx.Button(self.find_best_box, wx.ID_ANY, "Best Fit", pos=(20,360))
        self.try_best.Bind(wx.EVT_BUTTON, self.OnBest)

        self.scale_data = scale_data
        self.x_regress_vals = np.array(x_regress_vals).astype(np.float)
        self.y_regress_vals = y_regress_vals

        self.error_text = errtext

        # ------------------------------------ MAXFEV ------------------------------

        self.recursion_box = wx.StaticBox(self.panel, wx.ID_ANY, "Recursion", size=(350,150), pos=(450,10))
        self.recursion_txt = wx.StaticText(self.recursion_box, label="Recursion Limit: ", pos=(20,40))
        self.recursion_amount = wx.TextCtrl(self.recursion_box, value="1000", pos=(120,40), size=(200,20))

        self.Bind(wx.EVT_TEXT, self.get_recurse_value)

        # -------------------------------------DIALOG OK AND CANCEL BUTTONS--------------------------------------------------------
        # self.line = wx.StaticLine(self.panel, wx.LI_HORIZONTAL, pos=(0,580), size=(840,-1))
        self.helpbutton = wx.Button(self.panel, wx.ID_HELP, pos=(20, 600))
        self.okbutton = wx.Button(self.panel, wx.ID_OK, "OK", pos=(630, 600))
        self.cancelbutton = wx.Button(self.panel, wx.ID_CANCEL, pos=(720, 600))
        self.panel.Fit()
        self.Layout()
        self.added = []
    # function for clicking the 'Best Fit' button
    def OnBest(self, event):
        warnings.simplefilter("error", OptimizeWarning)
        r2best = -1
        scalebest = -1
        curvebest = -1
        # iterate over all y-values and calculate the R^2 value for all curve types at all scales
        # find the scale and curve type with highest R^2 value
        for y_values in self.get_y_rvals():
            # ------------------------------------------------------------------------------ linear
            try:
                popt0, pcov0 = CurveFit.linear_data(np.array(self.get_x_rvals()), np.array(y_values))
                r2_0 = CurveFit.r_squared(np.array(y_values), CurveFit.linear_fit(self.get_x_rvals(), *popt0))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_text().AppendText("Linear: " + str(e) + '\n')
                r2_0 = 0
            # -------------------------------------------------------------------------------- proportional
            try:
                popt1, pcov1 = CurveFit.prop_data(np.array(self.get_x_rvals()), np.array(y_values))
                r2_1 = CurveFit.r_squared(np.array(y_values), CurveFit.prop_fit(self.get_x_rvals(), *popt1))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_text().AppendText("Proportional: " + str(e) + '\n')
                # logging.error(traceback.format_exc())
                r2_1 = 0
            # -------------------------------------------------------------------------------- quadratic
            try:
                popt2, pcov2 = CurveFit.quad_data(np.array(self.get_x_rvals()), np.array(y_values))
                r2_2 = CurveFit.r_squared(np.array(y_values), CurveFit.quad_fit(self.get_x_rvals(), *popt2))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_text().AppendText("Quadratic: " + str(e) + '\n')
                # logging.error(traceback.format_exc())
                r2_2 = 0
            # ---------------------------------------------------------------------------------- cubic
            try:
                popt3, pcov3 = CurveFit.cubic_data(np.array(self.get_x_rvals()), np.array(y_values))
                r2_3 = CurveFit.r_squared(np.array(y_values), CurveFit.cubic_fit(self.get_x_rvals(), *popt3))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_text().AppendText("Cubic: " + str(e) + '\n')
                # logging.error(traceback.format_exc())
                r2_3 = 0
            # ---------------------------------------------------------------------------------- quartic
            try:
                popt4, pcov4 = CurveFit.quartic_data(np.array(self.get_x_rvals()), np.array(y_values))
                r2_4 = CurveFit.r_squared(np.array(y_values), CurveFit.quartic_fit(self.get_x_rvals(), *popt4))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_text().AppendText("Quartic: " + str(e) + '\n')
                # logging.error(traceback.format_exc())
                r2_4 = 0
            # ---------------------------------------------------------------------------------- quintic
            try:
                popt5, pcov5 = CurveFit.quintic_data(np.array(self.get_x_rvals()), np.array(y_values))
                r2_5 = CurveFit.r_squared(np.array(y_values), CurveFit.quintic_fit(self.get_x_rvals(), *popt5))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_text().AppendText("Quintic: " + str(e) + '\n')
                # logging.error(traceback.format_exc())
                r2_5 = 0
            # ---------------------------------------------------------------------------------- power
            try:
                popt6, pcov6 = CurveFit.power_data(np.array(self.get_x_rvals()), np.array(y_values))
                r2_6 = CurveFit.r_squared(np.array(y_values), CurveFit.power_fit(self.get_x_rvals(), *popt6))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_text().AppendText("Power: " + str(e) + '\n')
                # logging.error(traceback.format_exc())
                r2_6 = 0
            # ---------------------------------------------------------------------------------- inverse
            try:
                popt7, pcov7 = CurveFit.inverse_data(np.array(self.get_x_rvals()), np.array(y_values))
                r2_7 = CurveFit.r_squared(np.array(y_values), CurveFit.inverse_fit(self.get_x_rvals(), *popt7))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_text().AppendText("Inverse: " + str(e) + '\n')
                # logging.error(traceback.format_exc())
                r2_7 = 0
            # ---------------------------------------------------------------------------------- inverse squared
            try:
                popt8, pcov8 = CurveFit.insq_data(np.array(self.get_x_rvals()), np.array(y_values))
                r2_8 = CurveFit.r_squared(np.array(y_values), CurveFit.insq_fit(self.get_x_rvals(), *popt8))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_text().AppendText("Inverse Squared: " + str(e) + '\n')
                # logging.error(traceback.format_exc())
                r2_8 = 0
            # ---------------------------------------------------------------------------------- natural exponent
            try:
                popt9, pcov9 = CurveFit.nexp_data(np.array(self.get_x_rvals()), np.array(y_values))
                r2_9 = CurveFit.r_squared(np.array(y_values), CurveFit.nexp_fit(self.get_x_rvals(), *popt9))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_text().AppendText("Natural Exponent: " + str(e) + '\n')
                # logging.error(traceback.format_exc())
                r2_9 = 0
            # ---------------------------------------------------------------------------------- log e
            try:
                popt10, pcov10 = CurveFit.ln_data(np.array(self.get_x_rvals()), np.array(y_values))
                r2_10 = CurveFit.r_squared(np.array(y_values), CurveFit.ln_fit(self.get_x_rvals(), *popt10))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_text().AppendText("Natural Log: " + str(e) + '\n')
                # logging.error(traceback.format_exc())
                r2_10 = 0
            # ---------------------------------------------------------------------------------- log 10
            try:
                popt11, pcov11 = CurveFit.b10log_data(np.array(self.get_x_rvals()), np.array(y_values))
                r2_11 = CurveFit.r_squared(np.array(y_values), CurveFit.b10log_fit(self.get_x_rvals(), *popt11))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_text().AppendText("Log10: " + str(e) + '\n')
                # logging.error(traceback.format_exc())
                r2_11 = 0
            # ---------------------------------------------------------------------------------- inverse exponent
            try:
                popt12, pcov12 = CurveFit.invexp_data(np.array(self.get_x_rvals()), np.array(y_values))
                r2_12 = CurveFit.r_squared(np.array(y_values), CurveFit.invexp_fit(self.get_x_rvals(), *popt12))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_text().AppendText("Inverse Exponent: " + str(e) + '\n')
                # logging.error(traceback.format_exc())
                r2_12 = 0
            # ---------------------------------------------------------------------------------- sin
            try:
                popt13, pcov13 = CurveFit.sine_data(np.array(self.get_x_rvals()), np.array(y_values))
                r2_13 = CurveFit.r_squared(np.array(y_values), CurveFit.sine_fit(self.get_x_rvals(), *popt13))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_text().AppendText("Sine: " + str(e) + '\n')
                # logging.error(traceback.format_exc())
                r2_13 = 0
            # ---------------------------------------------------------------------------------- cos
            try:
                popt14, pcov14 = CurveFit.cosine_data(np.array(self.get_x_rvals()), np.array(y_values))
                r2_14 = CurveFit.r_squared(np.array(y_values), CurveFit.cosine_fit(self.get_x_rvals(), *popt14))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_text().AppendText("Cosine: " + str(e) + '\n')
                # logging.error(traceback.format_exc())
                r2_14 = 0
            # ---------------------------------------------------------------------------------- gaussian
            try:
                popt15, pcov15 = CurveFit.gauss_data(np.array(self.get_x_rvals()), np.array(y_values))
                r2_15 = CurveFit.r_squared(np.array(y_values), CurveFit.gauss_fit(self.get_x_rvals(), *popt15))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_text().AppendText("Gaussian: " + str(e) + '\n')
                # logging.error(traceback.format_exc())
                r2_15 = 0

            r2list = [[r2_0, "Linear"], [r2_1, "Proportional"], [r2_2, "Quadratic"], [r2_3, "Cubic"], [r2_4, "Quartic"],
                      [r2_5, "Quintic"], [r2_6, "Power"], [r2_7, "Inverse"], [r2_8, "Inverse Squared"],
                      [r2_9, "Natural Exponent"], [r2_10, "Natural Logarithm"], [r2_11, "Base-10 Log"],
                      [r2_12, "Inverse Exponent"], [r2_13, "Sine"], [r2_14, "Cosine"], [r2_15, "Gaussian"]]
            r2list.sort(key=self.keyfunc, reverse=True)
            if r2list[0][0] > r2best:
                r2best = r2list[0][0]
                scalebest = self.get_scale_vals()[self.get_y_rvals().index(y_values)]
                curvebest = r2list[0][1]
        # show the best curve type, R^2 and scale
        best_curve = wx.StaticText(self.find_best_box, -1, curvebest, pos=(80, 25))
        best_R2 = wx.StaticText(self.find_best_box, -1, str(r2best), pos=(80, 50))
        best_scale = wx.StaticText(self.find_best_box, -1, str(scalebest), pos=(80, 75))
    # function to select the curve types in the list
    def OnSelect(self, event):

        info = event.GetText()

        self.selectedList.append(info)

        def do_select():
            map(lambda x: self.regress_selection.Select(x, 1), set(self.selectedList))

        wx.CallLater(100, do_select)
        # display the check boxes for the selected curve types
        for i in self.sizerList:

            if self.selectedList.__contains__(i[0]) and not self.added.__contains__(i[0]):
                i[2].Enable()
                i[3].Enable()
                i[1].SetPosition(self.points[self.selectedList.index(i[0])])
                i[1].Show()
                self.added.append(i[0])

            self.panel.Layout()
            self.display_box.Fit()
            self.display_box.Refresh()
            self.panel.Fit()
            self.panel.Refresh()
    # function to deselect the curve types in the list
    def OnDeselect(self, event):

        info = event.GetText()

        self.selectedList.remove(info)

        def do_select():
            map(lambda x: self.regress_selection.Select(x, 1), set(self.selectedList))

        wx.CallLater(100, do_select)

        for i in self.sizerList:
            i[1].Hide()
        # remove the check boxes for the selected and then deselected curve types
        for i in self.added:

            if not self.selectedList.__contains__(i):

                self.added.remove(i)

                for j in self.sizerList:
                    if j[0] == i:
                        j[2].SetValue(False)
                        j[3].SetValue(False)

        for i in self.sizerList:

            if self.added.__contains__(i[0]):
                i[2].Enable()
                i[3].Enable()
                i[1].SetPosition(self.points[self.selectedList.index(i[0])])
                i[1].Show()

        self.panel.Layout()
        self.display_box.Fit()
        self.panel.Fit()
        self.panel.Refresh()
    # function to make check boxes
    def checkBox(self, box, label_txt): return wx.CheckBox(box, wx.ID_ANY, label=label_txt)
    # function with the check boxes for the possible graphs for the given curve type
    # this is whats displayed when selecting the curve type from the list
    def displayBox(self, title):

        plot_box = wx.StaticBox(self.display_box, wx.ID_ANY, title, size=(110, 65))
        regress_check = self.checkBox(plot_box, "Regression")
        regress_check.SetPosition((10,20))
        scalexR2_check = self.checkBox(plot_box, "Scale by R$^2$")
        scalexR2_check.SetPosition((10,40))
        return plot_box, regress_check, scalexR2_check
    # hides all of the displayed curve boxes
    def hideAll(self):

        self.prop_plot_box.Hide()
        self.lin_plot_box.Hide()
        self.quad_plot_box.Hide()
        self.cubic_plot_box.Hide()
        self.quart_plot_box.Hide()
        self.quint_plot_box.Hide()
        self.pow_plot_box.Hide()
        self.inverse_plot_box.Hide()
        self.insq_plot_box.Hide()
        self.nexp_plot_box.Hide()
        self.Ln_plot_box.Hide()
        # self.b10ex_plot_box.Hide()
        self.b10log_plot_box.Hide()
        self.invexp_plot_box.Hide()
        self.sin_plot_box.Hide()
        self.cos_plot_box.Hide()
        self.gauss_plot_box.Hide()
    # get the recursion value from user input and set it
    def get_recurse_value(self, event):

        try:
            CurveFit.set_maxfev(int(self.get_recursion_amount().GetValue()))
        except (ValueError) as e:
            self.get_error_text().AppendText("Recursion: " + str(e) + '\n')

    def get_x_rvals(self): return self.x_regress_vals
    def get_y_rvals(self): return self.y_regress_vals
    def get_scale_vals(self): return self.scale_data
    def get_error_text(self): return self.error_text
    def get_selected(self): return self.selectedList
    def keyfunc(self, x): return x[0]
    def get_recursion_amount(self): return self.recursion_amount
# Class for the dialog which contains the regression plots
# this is essentially identical to the code in the RegressionSelectDialog class
# see class RegressionSelectDialog in CanvasPanel.py
class RegressionDialog(wx.Frame):

    def __init__(self, parent, title, x, xr, y, swb, tree):
        # wx.Dialog.__init__(self, parent, wx.ID_ANY, "Graph", size=(640, 480))
        wx.Frame.__init__(self, parent, title=title, size=(640, 530), style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)

        # ------------------ Workbook ------------------------------
        self.workbook = swb
        self.tree_menu = tree

        self.graph = RegressionPlot(self, x, xr, y, swb, tree)
        # ------------------- Regression stuff -----------------------
        self.popt, self.pcov = None, None

        # ----------------------------------- MENU STUFF -----------------------------------------------------
        # 'file' sub menu on menu bar
        self.filemenu = wx.Menu()
        self.save = self.filemenu.Append(wx.ID_SAVE, 'Save', 'Save')
        self.close = self.filemenu.Append(wx.ID_EXIT, 'Close', 'Close')
        self.Bind(wx.EVT_MENU, self.OnSave, self.save)
        self.Bind(wx.EVT_MENU, self.OnClose, self.close)
        self.Bind(wx.EVT_MENU_CLOSE, self.OnClose, self)
        self.Bind(wx.EVT_CLOSE, self.OnClose, self)

        # 'graph' sub menu on menu bar
        self.graphmenu = wx.Menu()
        self.label = self.graphmenu.Append(wx.ID_ANY, 'Label', 'Label')
        self.legend = self.graphmenu.Append(wx.ID_ANY, 'Legend', 'Legend')
        self.symbol = self.graphmenu.Append(wx.ID_ANY, 'Symbols...', 'Symbols...')
        self.annotate = self.graphmenu.Append(wx.ID_ANY, 'Annotate', 'Annotate')
        self.grid = self.graphmenu.Append(wx.ID_ANY, 'Grid', 'Grid')
        self.gColor = self.graphmenu.Append(wx.ID_ANY, 'Graph Color...', 'Graph Color...')
        self.Bind(wx.EVT_MENU, self.OnLabel, self.label)
        self.Bind(wx.EVT_MENU, self.OnLegend, self.legend)
        self.Bind(wx.EVT_MENU, self.OnSymbol, self.symbol)
        self.Bind(wx.EVT_MENU, self.OnAnnotate, self.annotate)
        self.Bind(wx.EVT_MENU, self.OnGrid, self.grid)
        self.Bind(wx.EVT_MENU, self.OnGraphColor, self.gColor)

        # creates the menu bar and adds the tab to the top of the page
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(self.filemenu, 'File')
        self.menuBar.Append(self.graphmenu, 'Graph')
        self.SetMenuBar(self.menuBar)

        self.annotated = False
        self.isGrid = False

        # ------------------------------ GRAPH ANNOTATION -----------------------------------------------
        self.ann = []
        self.legend_text = ['line', 'data']

    def OnSave(self, event):

        saveFileDialog = wx.FileDialog(self, "Save", "", "untitled-plot", "PNG (*.PNG)|*.png|"
                                                                          "PDF (*.PDF)|*.pdf|"
                                                                          "RAW (*.RAW)|*.raw", wx.FD_SAVE | wx.FD_SAVE)
        saveFileDialog.CenterOnScreen()
        # shows the dialog on screen when pushes button
        result = saveFileDialog.ShowModal()
        # only saves the file if 'save' in dialog is pressed otherwise if 'cancel' in dialog is pressed closes dialog
        if result == wx.ID_OK:
            # gets the file path
            filepath = saveFileDialog.GetPath()
            # saves the regression plot figure
            self.graph.get_fig().savefig(filepath)
            self.graph.set_saved(True)
            return True
        elif result == wx.ID_CANCEL:
            return False

    def OnClose(self, event):

        self.Hide()

    def OnLabel(self, event):

        t = self.graph.get_axes().get_title()
        x = self.graph.get_axes().get_xlabel()
        y = self.graph.get_axes().get_ylabel()

        labelDialog = LabelDialog(self, t, x, y)
        labelDialog.CenterOnScreen()
        labelDialog.ShowModal()

        self.get_graph().set_titlelabel(labelDialog.get_title())
        self.get_graph().set_xlabel(labelDialog.get_xaxis())
        self.get_graph().set_ylabel(labelDialog.get_yaxis())

        # sets the title, xlabel, ylabel of the regression plot to the user inputs
        self.get_graph().label(labelDialog.get_title(), labelDialog.get_xaxis(), labelDialog.get_yaxis())

    def OnLegend(self, event):

        legendDialog = LegendDialog(self, self.get_saved_legend_text())
        legendDialog.CenterOnScreen()
        res = legendDialog.ShowModal()

        if res == wx.ID_OK:

            legendDialog.SaveString()
            text_list = legendDialog.get_legend_text()
            self.set_saved_legend_text(text_list)

            if legendDialog.get_topL().IsChecked():
                self.add_legend(2, text_list)
            if legendDialog.get_topR().IsChecked():
                self.add_legend(1, text_list)
            if legendDialog.get_botL().IsChecked():
                self.add_legend(3, text_list)
            if legendDialog.get_botR().IsChecked():
                self.add_legend(4, text_list)
            if legendDialog.get_off().IsChecked():
                self.get_graph().get_axes().legend(labels=text_list).remove()
                self.get_graph().set_isLegend(False)
                self.get_graph().set_legendLoc('')
            self.get_graph().get_canvas().draw()

    def OnSymbol(self, event):

        symbolDialog = SymbolDialog(self)
        results = symbolDialog.ShowModal()

        if results == wx.ID_OK:
            # x = []
            self.get_graph().set_dataSymbol(symbolDialog.get_selectedSymbol())
            self.get_graph().set_dataSymbolSize(int(symbolDialog.get_sizeChoices()[symbolDialog.get_sizeSelect().GetSelection()]))
            self.get_graph().get_axes().cla()
            self.get_graph().set_annot_line(self.get_graph().get_axes().annotate("", xy=(0,0),
                                                   xytext=(0.5,0.5), textcoords="figure fraction",
                                                   bbox=dict(boxstyle="round", fc="w"),
                                                   arrowprops=dict(arrowstyle="->")))
            self.get_graph().set_annot(self.get_graph().get_axes().annotate("", xy=(0, 0), xytext=(8, 8), textcoords="figure pixels",
                                              bbox=dict(boxstyle="round", fc="w"),
                                              arrowprops=dict(arrowstyle="->")))
            self.get_graph().get_annot().set_visible(False)
            self.get_graph().get_annot_line().set_visible(False)
            self.get_graph().get_annot_line().draggable()
            self.get_graph().get_axes().scatter(self.get_graph().get_xr(),
                                                self.get_graph().get_yr(),
                                                marker=self.get_graph().get_dataSymbol(),
                                                s=self.get_graph().get_dataSymbolSize(),
                                                color=self.get_graph().get_dataColor())
            self.get_graph().get_axes().plot(self.get_graph().get_x_plot(), self.get_graph().get_curve(), '-',
                                             color=self.get_graph().get_lineColor())
            if self.get_graph().get_isLegend():
                self.get_graph().get_axes().legend(labels=self.get_graph().get_legendText(), loc=self.get_graph().get_legendLoc())

            if self.get_isGrid():
                self.get_graph().get_axes().grid(True)
                self.set_isGrid(True)

            self.get_graph().label(self.get_graph().get_titlelabel(),
                                   self.get_graph().get_xlabel(),
                                   self.get_graph().get_ylabel())
            self.get_graph().get_canvas().draw()

    def OnAnnotate(self, event):

        # print(self.get_graph().get_line_annot_pos()) # whyyyyyyyy....

        # self.get_graph().get_annot_line().xy = self.get_graph().get_line_annot_pos() # <<<<<------ Problem

        mn = self.get_graph().get_mn()
        mx = self.get_graph().get_mx()
        y = self.get_graph().get_curve()[int(len(self.get_graph().get_curve())/2)]
        self.get_graph().get_annot_line().xy = [((mx-mn)/2.0) + mn, y]
        # print(y)
        # print(((mx-mn)/2.0) + mn)
        text = 'R$^2$: ' + str(np.round_(self.get_graph().get_best_r_squared(), 3)) + '\n' + \
               'Scale: ' + str(self.get_graph().get_best_scale()) + '\n' + self.get_graph().get_popt()

        self.get_graph().get_annot_line().set_text(text)
        self.get_graph().get_annot_line().set_fontsize(10)
        self.get_graph().get_annot_line().get_bbox_patch().set_alpha(0.4)

        if self.get_graph().get_annot_line().get_visible():
            self.get_graph().get_annot_line().set_visible(False)
            self.get_graph().get_fig().canvas.draw_idle()
        else:
            self.get_graph().get_annot_line().set_visible(True)
            self.get_graph().get_fig().canvas.draw_idle()

    def OnGrid(self, event):

        global customColor
        customColor = ''

        gridDialog = wx.Dialog(self, wx.ID_ANY, "Grid", size=(175, 200))
        gridPanel = wx.Panel(gridDialog, wx.ID_ANY)

        gridOn = wx.CheckBox(gridPanel, wx.ID_ANY, label="Grid On", pos=(10, 10))
        gridOff = wx.CheckBox(gridPanel, wx.ID_ANY, label="Grid Off", pos=(80, 10))

        gridTypeTxt = wx.StaticText(gridPanel, -1, 'Style', pos=(10,45))
        gridColorTxt = wx.StaticText(gridPanel, -1, 'Color', pos=(10, 80))

        gridType = wx.Choice(gridPanel, wx.ID_ANY, pos=(50, 45), choices=['solid', 'dashed', 'dotted', 'dashdot'])
        gridColor = wx.Choice(gridPanel, wx.ID_ANY, pos=(50, 80), choices=['black', 'dark grey', 'grey', 'light grey', 'custom...'])

        okbutton = wx.Button(gridPanel, wx.ID_OK, pos=(65, 130))

        def OnType(event): return str(gridType.GetString(gridType.GetSelection()))
        def OnColor(event):

            if gridColor.GetString(gridColor.GetCurrentSelection()) == 'custom...':
                data = wx.ColourData()
                col = wx.ColourDialog(self, data)
                col.CenterOnScreen()
                res = col.ShowModal()
                if res == wx.ID_OK:
                    global customColor
                    customColor = str(col.GetColourData().GetColour().GetAsString(wx.C2S_HTML_SYNTAX))

            else:
                return str(gridColor.GetString(gridColor.GetSelection()))

        gridType.Bind(wx.EVT_CHOICE, OnType)
        gridColor.Bind(wx.EVT_CHOICE, OnColor)

        gridDialog.CenterOnScreen()
        result = gridDialog.ShowModal()

        if result == wx.ID_OK:

            if gridOn.IsChecked():

                if str(gridColor.GetString(gridColor.GetSelection())) == 'custom...':
                    self.get_graph().get_axes().grid(True, linestyle=str(gridType.GetString(gridType.GetSelection())),
                                                     color=customColor)
                    self.set_isGrid(True)

                else:
                    self.get_graph().get_axes().grid(True, linestyle=str(gridType.GetString(gridType.GetSelection())),
                                                     color='xkcd:'+str(gridColor.GetString(gridColor.GetSelection())))
                    self.set_isGrid(True)

            if gridOff.IsChecked():
                self.get_graph().get_axes().grid(False)
                self.set_isGrid(False)

            self.get_graph().get_canvas().draw()

    def OnGraphColor(self, event):

        global customLineColor
        customLineColor = ''
        global customDataColor
        customDataColor = ''

        graphColorDialog = wx.Dialog(self, wx.ID_ANY, "Graph Color", size=(175, 200))
        graphColorPanel = wx.Panel(graphColorDialog, wx.ID_ANY)

        lineColorTxt = wx.StaticText(graphColorPanel, -1, 'Line', pos=(10, 45))
        dataColorTxt = wx.StaticText(graphColorPanel, -1, 'Data', pos=(10, 80))

        lineColor = wx.Choice(graphColorPanel, wx.ID_ANY, pos=(50, 45),
                              choices=['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'custom...'])
        dataColor = wx.Choice(graphColorPanel, wx.ID_ANY, pos=(50, 80),
                              choices=['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'custom...'])

        okbutton = wx.Button(graphColorPanel, wx.ID_OK, pos=(65, 130))

        def OnLineColor(event):

            global customLineColor
            if lineColor.GetString(lineColor.GetCurrentSelection()) == 'custom...':
                data = wx.ColourData()
                col = wx.ColourDialog(self, data)
                col.CenterOnScreen()
                res = col.ShowModal()
                if res == wx.ID_OK:
                    customLineColor = str(col.GetColourData().GetColour().GetAsString(wx.C2S_HTML_SYNTAX))

            else:
                customLineColor = 'xkcd:' + str(lineColor.GetString(lineColor.GetSelection()))

            self.get_graph().set_lineColor(customLineColor)

        def OnDataColor(event):

            global customDataColor
            if dataColor.GetString(dataColor.GetCurrentSelection()) == 'custom...':
                data = wx.ColourData()
                col = wx.ColourDialog(self, data)
                col.CenterOnScreen()
                res = col.ShowModal()
                if res == wx.ID_OK:
                    customDataColor = str(col.GetColourData().GetColour().GetAsString(wx.C2S_HTML_SYNTAX))

            else:
                customDataColor = 'xkcd:' + str(dataColor.GetString(dataColor.GetSelection()))

            self.get_graph().set_dataColor(customDataColor)

        lineColor.Bind(wx.EVT_CHOICE, OnLineColor)
        dataColor.Bind(wx.EVT_CHOICE, OnDataColor)

        graphColorDialog.CenterOnScreen()
        result = graphColorDialog.ShowModal()

        if result == wx.ID_OK:

            self.get_graph().get_axes().cla()
            self.get_graph().set_annot_line(self.get_graph().get_axes().annotate("", xy=(0, 0),
                                                                                 xytext=(0.5, 0.5),
                                                                                 textcoords="figure fraction",
                                                                                 bbox=dict(boxstyle="round", fc="w"),
                                                                                 arrowprops=dict(arrowstyle="->")))
            self.get_graph().set_annot(
                self.get_graph().get_axes().annotate("", xy=(0, 0), xytext=(8, 8), textcoords="figure pixels",
                                                     bbox=dict(boxstyle="round", fc="w"),
                                                     arrowprops=dict(arrowstyle="->")))
            self.get_graph().get_annot().set_visible(False)
            self.get_graph().get_annot_line().set_visible(False)
            self.get_graph().get_annot_line().draggable()
            self.get_graph().get_axes().scatter(self.get_graph().get_xr(),
                                                self.get_graph().get_yr(),
                                                marker=self.get_graph().get_dataSymbol(),
                                                s=self.get_graph().get_dataSymbolSize(),
                                                color=self.get_graph().get_dataColor())
            self.get_graph().get_axes().plot(self.get_graph().get_x_plot(), self.get_graph().get_curve(), '-',
                                             color=self.get_graph().get_lineColor())
            if self.get_graph().get_isLegend():
                self.get_graph().get_axes().legend(labels=self.get_graph().get_legendText(), loc=self.get_graph().get_legendLoc())

            if self.get_isGrid():
                self.get_graph().get_axes().grid(True)
                self.set_isGrid(True)

            self.get_graph().label(self.get_graph().get_titlelabel(),
                                   self.get_graph().get_xlabel(),
                                   self.get_graph().get_ylabel())

            self.get_graph().get_canvas().draw()

    def add_legend(self, loc, txt):
        self.get_graph().get_axes().legend(labels=txt, loc=loc)
        self.get_graph().set_isLegend(True)
        self.get_graph().set_legendLoc(loc)

    def get_graph(self): return self.graph
    def get_curve(self): return self.curve
    def set_curve(self, curve): self.curve = curve
    def get_annotated(self): return self.annotated
    def set_annotated(self, ann): self.annotated = ann
    def get_ann(self): return self.ann
    def set_ann(self, a): self.ann = a
    def get_isGrid(self): return self.isGrid
    def set_isGrid(self, g): self.isGrid = g
    def get_saved_legend_text(self): return self.legend_text
    def set_saved_legend_text(self, txt): self.legend_text = txt
# class for the dialog which contains the area / complexity by scale graphs
# the functions OnSave, OnLabel, etc... are the same as described in class RegressionSelectDialog
# This repetitive code is a possible place to generalize and simplify / reduce code
class SclbyAreaDialog(wx.Frame):

    def __init__(self, parent, title, x, y, legend_txt, data):
        # wx.Dialog.__init__(self, parent, wx.ID_ANY, "Graph", size=(640, 480))
        wx.Frame.__init__(self, parent, title=title, size=(640, 530), style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.graph = SclbyAreaPlot(self, x, y, data)
        self.legend_txt = legend_txt
        self.parent = parent
        self.title = title

        # ----------------------------------- MENU STUFF -----------------------------------------------------
        # 'file' sub menu on menu bar
        self.filemenu = wx.Menu()
        self.save = self.filemenu.Append(wx.ID_SAVE, 'Save', 'Save')
        self.close = self.filemenu.Append(wx.ID_EXIT, 'Close', 'Close')
        self.Bind(wx.EVT_MENU, self.OnSave, self.save)
        self.Bind(wx.EVT_MENU, self.OnClose, self.close)
        self.Bind(wx.EVT_CLOSE, self.OnClose, self)
        self.Bind(wx.EVT_MENU_CLOSE, self.OnClose, self)

        # 'graph' sub menu on menu bar
        self.graphmenu = wx.Menu()
        self.label = self.graphmenu.Append(wx.ID_ANY, 'Label', 'Label')
        self.legend = self.graphmenu.Append(wx.ID_ANY, 'Legend', 'Legend')
        self.symbol = self.graphmenu.Append(wx.ID_ANY, 'Symbols...', 'Symbols...')
        self.grid = self.graphmenu.Append(wx.ID_ANY, 'Grid', 'Grid')
        self.Bind(wx.EVT_MENU, self.OnLabel, self.label)
        self.Bind(wx.EVT_MENU, self.OnLegend, self.legend)
        self.Bind(wx.EVT_MENU, self.OnSymbol, self.symbol)
        self.Bind(wx.EVT_MENU, self.OnGrid, self.grid)

        # creates the menu bar and adds the tab to the top of the page
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(self.filemenu, 'File')
        self.menuBar.Append(self.graphmenu, 'Graph')
        self.SetMenuBar(self.menuBar)

        self.annotated = False
        self.isGrid = False
        # ------------------------------ GRAPH ANNOTATION -----------------------------------------------
        self.ann = []

    def OnSave(self, event):

        saveFileDialog = wx.FileDialog(self, "Save", "", "untitled-plot", "PNG (*.PNG)|*.png|"
                                                                          "PDF (*.PDF)|*.pdf|"
                                                                          "RAW (*.RAW)|*.raw", wx.FD_SAVE | wx.FD_SAVE)
        saveFileDialog.CenterOnScreen()
        # shows the dialog on screen when pushes button
        result = saveFileDialog.ShowModal()
        # only saves the file if 'save' in dialog is pressed otherwise if 'cancel' in dialog is pressed closes dialog
        if result == wx.ID_OK:
            # gets the file path
            filepath = saveFileDialog.GetPath()
            # saves the regression plot figure
            self.graph.get_fig().savefig(filepath)
            self.graph.set_saved(True)
            return True
        elif result == wx.ID_CANCEL:
            return False

    def OnClose(self, event):

        self.Hide()

    def OnLabel(self, event):

        t = self.graph.get_axes().get_title()
        x = self.graph.get_axes().get_xlabel()
        y = self.graph.get_axes().get_ylabel()

        labelDialog = LabelDialog(self, t, x, y)
        labelDialog.CenterOnScreen()
        labelDialog.ShowModal()

        self.get_graph().set_titlelabel(labelDialog.get_title())
        self.get_graph().set_xlabel(labelDialog.get_xaxis())
        self.get_graph().set_ylabel(labelDialog.get_yaxis())

        # sets the title, xlabel, ylabel of the regression plot to the user inputs
        self.get_graph().label(labelDialog.get_title(), labelDialog.get_xaxis(), labelDialog.get_yaxis())

    def OnLegend(self, event):

        legendDialog = LegendDialog(self, self.get_saved_legend_text())
        legendDialog.CenterOnScreen()
        res = legendDialog.ShowModal()

        if res == wx.ID_OK:

            legendDialog.SaveString()
            text_list = legendDialog.get_legend_text()
            self.set_saved_legend_text(text_list)

            if legendDialog.get_topL().IsChecked():
                self.add_legend(2, text_list)
            if legendDialog.get_topR().IsChecked():
                self.add_legend(1, text_list)
            if legendDialog.get_botL().IsChecked():
                self.add_legend(3, text_list)
            if legendDialog.get_botR().IsChecked():
                self.add_legend(4, text_list)
            if legendDialog.get_off().IsChecked():
                self.get_graph().get_axes().legend(labels=text_list).remove()
                self.get_graph().set_isLegend(False)
                self.get_graph().set_legendLoc('')
            self.get_graph().get_canvas().draw()

    def OnSymbol(self, event):

        symbolDialog = SymbolDialog(self)
        results = symbolDialog.ShowModal()

        if results == wx.ID_OK:

            self.get_graph().get_axes().cla()

            for yvals in self.get_graph().get_y():
                self.get_graph().get_axes().scatter(self.get_graph().get_x(),
                                                    yvals,
                                                    marker=symbolDialog.selectedSymbol,
                                                    s=int(symbolDialog.size_choices[symbolDialog.size_select.GetSelection()]))

            if self.get_graph().get_isLegend():
                self.get_graph().get_axes().legend(labels=self.legend_txt, loc=self.get_graph().get_legendLoc())

            if self.get_isGrid():
                self.get_graph().get_axes().grid(True)
                self.set_isGrid(True)

            self.get_graph().label(self.get_graph().get_titlelabel(),
                                   self.get_graph().get_xlabel(),
                                   self.get_graph().get_ylabel())

            self.get_graph().get_axes().set_xscale('log')

            if self.get_title() == 'Scale by Relative Area':
                ycurr = []
                ynew = []

                for t in self.get_graph().get_axes().get_yticklabels():
                    ycurr.append(t.get_text())
                    num = t.get_text()
                    if '−' in num:
                        newnum = num.replace('−', '-')
                        ynew.append(np.round_(np.power(10, float(newnum)), 4))
                    else:
                        ynew.append(np.round_(np.power(10, float(num)), 4))

                self.get_graph().get_axes().set_yticklabels(ynew)
            self.get_graph().get_canvas().draw()

    def OnGrid(self, event):

        global customColor
        customColor = ''

        gridDialog = wx.Dialog(self, wx.ID_ANY, "Grid", size=(175, 200))
        gridPanel = wx.Panel(gridDialog, wx.ID_ANY)

        gridOn = wx.CheckBox(gridPanel, wx.ID_ANY, label="Grid On", pos=(10, 10))
        gridOff = wx.CheckBox(gridPanel, wx.ID_ANY, label="Grid Off", pos=(80, 10))

        gridTypeTxt = wx.StaticText(gridPanel, -1, 'Style', pos=(10,45))
        gridColorTxt = wx.StaticText(gridPanel, -1, 'Color', pos=(10, 80))

        gridType = wx.Choice(gridPanel, wx.ID_ANY, pos=(50, 45), choices=['solid', 'dashed', 'dotted', 'dashdot'])
        gridColor = wx.Choice(gridPanel, wx.ID_ANY, pos=(50, 80), choices=['black', 'dark grey', 'grey', 'light grey', 'custom...'])

        okbutton = wx.Button(gridPanel, wx.ID_OK, pos=(65, 130))

        def OnType(event): return str(gridType.GetString(gridType.GetSelection()))
        def OnColor(event):

            if gridColor.GetString(gridColor.GetCurrentSelection()) == 'custom...':
                data = wx.ColourData()
                col = wx.ColourDialog(self, data)
                col.CenterOnScreen()
                res = col.ShowModal()
                if res == wx.ID_OK:
                    global customColor
                    customColor = str(col.GetColourData().GetColour().GetAsString(wx.C2S_HTML_SYNTAX))

            else:
                return str(gridColor.GetString(gridColor.GetSelection()))

        gridType.Bind(wx.EVT_CHOICE, OnType)
        gridColor.Bind(wx.EVT_CHOICE, OnColor)

        gridDialog.CenterOnScreen()
        result = gridDialog.ShowModal()

        if result == wx.ID_OK:

            if gridOn.IsChecked():

                if str(gridColor.GetString(gridColor.GetSelection())) == 'custom...':
                    self.get_graph().get_axes().grid(True, linestyle=str(gridType.GetString(gridType.GetSelection())),
                                                     color=customColor)
                    self.set_isGrid(True)

                else:
                    self.get_graph().get_axes().grid(True, linestyle=str(gridType.GetString(gridType.GetSelection())),
                                                     color='xkcd:'+str(gridColor.GetString(gridColor.GetSelection())))
                    self.set_isGrid(True)

            if gridOff.IsChecked():
                self.get_graph().get_axes().grid(False)
                self.set_isGrid(False)

            self.get_graph().get_canvas().draw()

    def add_legend(self, loc, txt):
        self.get_graph().get_axes().legend(labels=txt, loc=loc)
        self.get_graph().set_isLegend(True)
        self.get_graph().set_legendLoc(loc)

    def get_graph(self): return self.graph
    def get_title(self): return self.title
    def get_popt(self): return self.popt
    def set_popt(self, popt): self.popt = popt
    def get_pcov(self): return self.pcov
    def set_pcov(self, pcov): self.pcov = pcov
    def get_curve(self): return self.curve
    def set_curve(self, curve): self.curve = curve
    def get_annotated(self): return self.annotated
    def set_annotated(self, ann): self.annotated = ann
    def get_ann(self): return self.ann
    def set_ann(self, a): self.ann = a
    def get_isGrid(self): return self.isGrid
    def set_isGrid(self, g): self.isGrid = g
    def get_saved_legend_text(self): return self.legend_txt
    def set_saved_legend_text(self, txt): self.legend_txt = txt
    def get_parent(self): return self.parent
# class for the dialog which contains the R^2 by scale graphs
# the functions OnSave, OnLabel, etc... are the same as described in class RegressionSelectDialog
class R2byScaleDialog(wx.Frame):

    def __init__(self, parent, title, data, error_txt, tree_menu, root, id):
        # wx.Dialog.__init__(self, parent, wx.ID_ANY, "Graph", size=(640, 480))
        wx.Frame.__init__(self, parent, title=title, size=(640, 530), style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.graph = R2byScalePlot(self, data, error_txt, tree_menu, root, id)

        # ----------------------------------- MENU STUFF -----------------------------------------------------
        # 'file' sub menu on menu bar
        self.filemenu = wx.Menu()
        self.save = self.filemenu.Append(wx.ID_SAVE, 'Save', 'Save')
        self.close = self.filemenu.Append(wx.ID_EXIT, 'Close', 'Close')
        self.Bind(wx.EVT_MENU, self.OnSave, self.save)
        self.Bind(wx.EVT_MENU, self.OnClose, self.close)
        self.Bind(wx.EVT_CLOSE, self.OnClose, self)
        self.Bind(wx.EVT_MENU_CLOSE, self.OnClose, self)

        # 'graph' sub menu on menu bar
        self.graphmenu = wx.Menu()
        self.label = self.graphmenu.Append(wx.ID_ANY, 'Label', 'Label')
        self.legend = self.graphmenu.Append(wx.ID_ANY, 'Legend', 'Legend')
        self.symbol = self.graphmenu.Append(wx.ID_ANY, 'Symbols...', 'Symbols...')
        # self.annotate = self.graphmenu.Append(wx.ID_ANY, 'Annotate', 'Annotate')
        self.grid = self.graphmenu.Append(wx.ID_ANY, 'Grid', 'Grid')
        self.gColor = self.graphmenu.Append(wx.ID_ANY, 'Graph Color...', 'Graph Color...')
        self.Bind(wx.EVT_MENU, self.OnGraphColor, self.gColor)
        self.Bind(wx.EVT_MENU, self.OnLabel, self.label)
        self.Bind(wx.EVT_MENU, self.OnLegend, self.legend)
        self.Bind(wx.EVT_MENU, self.OnSymbol, self.symbol)
        # self.Bind(wx.EVT_MENU, self.OnAnnotate, self.annotate)
        self.Bind(wx.EVT_MENU, self.OnGrid, self.grid)

        # creates the menu bar and adds the tab to the top of the page
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(self.filemenu, 'File')
        self.menuBar.Append(self.graphmenu, 'Graph')
        self.SetMenuBar(self.menuBar)

        # -------------------------------------------- TEXT STUFF ----------------------------------------
        self.annotated = False
        self.isGrid = False
        # ------------------------------ GRAPH ANNOTATION -----------------------------------------------
        self.ann = []
        self.legend_text = ['data']
        self.sizer.Add(self.graph, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()
        self.Fit()

    def OnSave(self, event):

        saveFileDialog = wx.FileDialog(self, "Save", "", "untitled-plot", "PNG (*.PNG)|*.png|"
                                                                          "PDF (*.PDF)|*.pdf|"
                                                                          "RAW (*.RAW)|*.raw", wx.FD_SAVE | wx.FD_SAVE)
        saveFileDialog.CenterOnScreen()
        # shows the dialog on screen when pushes button
        result = saveFileDialog.ShowModal()
        # only saves the file if 'save' in dialog is pressed otherwise if 'cancel' in dialog is pressed closes dialog
        if result == wx.ID_OK:
            # gets the file path
            filepath = saveFileDialog.GetPath()
            # saves the regression plot figure
            self.graph.get_fig().savefig(filepath)
            self.graph.set_saved(True)
            return True
        elif result == wx.ID_CANCEL:
            return False

    def OnClose(self, event):
        self.Hide()

    def OnLabel(self, event):

        t = self.graph.get_axes().get_title()
        x = self.graph.get_axes().get_xlabel()
        y = self.graph.get_axes().get_ylabel()

        labelDialog = LabelDialog(self, t, x, y)
        labelDialog.CenterOnScreen()
        labelDialog.ShowModal()

        self.get_graph().set_titlelabel(labelDialog.get_title())
        self.get_graph().set_xlabel(labelDialog.get_xaxis())
        self.get_graph().set_ylabel(labelDialog.get_yaxis())

        # sets the title, xlabel, ylabel of the regression plot to the user inputs
        self.get_graph().label(labelDialog.get_title(), labelDialog.get_xaxis(), labelDialog.get_yaxis())

    def OnLegend(self, event):

        legendDialog = LegendDialog(self, self.get_saved_legend_text())
        legendDialog.CenterOnScreen()
        res = legendDialog.ShowModal()

        if res == wx.ID_OK:

            legendDialog.SaveString()
            text_list = legendDialog.get_legend_text()
            self.set_saved_legend_text(text_list)

            if legendDialog.get_topL().IsChecked():
                self.add_legend(2, text_list)
            if legendDialog.get_topR().IsChecked():
                self.add_legend(1, text_list)
            if legendDialog.get_botL().IsChecked():
                self.add_legend(3, text_list)
            if legendDialog.get_botR().IsChecked():
                self.add_legend(4, text_list)
            if legendDialog.get_off().IsChecked():
                self.get_graph().get_axes().legend(labels=text_list).remove()
                self.get_graph().set_isLegend(False)
                self.get_graph().set_legendLoc('')
            self.get_graph().get_canvas().draw()

    def OnSymbol(self, event):

        symbolDialog = SymbolDialog(self)
        results = symbolDialog.ShowModal()

        if results == wx.ID_OK:
            self.get_graph().set_dataSymbol(symbolDialog.get_selectedSymbol())
            self.get_graph().set_dataSymbolSize(int(symbolDialog.get_sizeChoices()[symbolDialog.get_sizeSelect().GetSelection()]))
            self.get_graph().get_axes().cla()
            self.get_graph().set_annot(
                self.get_graph().get_axes().annotate("", xy=(0, 0), xytext=(8, 8), textcoords="figure pixels",
                                                     bbox=dict(boxstyle="round", fc="w"),
                                                     arrowprops=dict(arrowstyle="->")))
            self.get_graph().get_annot().set_visible(False)

            self.get_graph().get_axes().scatter(self.get_graph().get_x(),
                                                self.get_graph().get_y_plot(),
                                                marker=self.get_graph().get_dataSymbol(),
                                                s=self.get_graph().get_dataSymbolSize(),
                                                color=self.get_graph().get_dataColor())
            if self.get_graph().get_isLegend():
                self.get_graph().get_axes().legend(labels=self.get_graph().get_legendText(), loc=self.get_graph().get_legendLoc())

            if self.get_isGrid():
                self.get_graph().get_axes().grid(True)
                self.set_isGrid(True)

            self.get_graph().label(self.get_graph().get_titlelabel(),
                                   self.get_graph().get_xlabel(),
                                   self.get_graph().get_ylabel())

            self.get_graph().get_axes().set_xscale('log')
            self.get_graph().get_canvas().draw()

    def OnAnnotate(self, event):

        x = []

        if not self.get_annotated():

            for i in range(0, len(self.get_graph().get_x())):
                x.append(self.get_graph().get_axes().annotate(("(" + str(self.get_graph().get_x()[i]) + "," +
                                                               str(self.get_graph().get_y_plot()[i]) + ")"),
                                                               (self.get_graph().get_x()[i],
                                                               self.get_graph().get_y_plot()[i]), fontsize=11))

            self.set_ann(x)
            self.set_annotated(True)
        else:
            for i in self.get_ann():
                i.remove()
            self.set_annotated(False)
            self.set_ann([])

        self.get_graph().get_canvas().draw()

    def OnGrid(self, event):

        global customColor
        customColor = ''

        gridDialog = wx.Dialog(self, wx.ID_ANY, "Grid", size=(175, 200))
        gridPanel = wx.Panel(gridDialog, wx.ID_ANY)

        gridOn = wx.CheckBox(gridPanel, wx.ID_ANY, label="Grid On", pos=(10, 10))
        gridOff = wx.CheckBox(gridPanel, wx.ID_ANY, label="Grid Off", pos=(80, 10))

        gridTypeTxt = wx.StaticText(gridPanel, -1, 'Style', pos=(10,45))
        gridColorTxt = wx.StaticText(gridPanel, -1, 'Color', pos=(10, 80))

        gridType = wx.Choice(gridPanel, wx.ID_ANY, pos=(50, 45), choices=['solid', 'dashed', 'dotted', 'dashdot'])
        gridColor = wx.Choice(gridPanel, wx.ID_ANY, pos=(50, 80), choices=['black', 'dark grey', 'grey', 'light grey', 'custom...'])

        okbutton = wx.Button(gridPanel, wx.ID_OK, pos=(65, 130))

        def OnType(event): return str(gridType.GetString(gridType.GetSelection()))
        def OnColor(event):

            if gridColor.GetString(gridColor.GetCurrentSelection()) == 'custom...':
                data = wx.ColourData()
                col = wx.ColourDialog(self, data)
                col.CenterOnScreen()
                res = col.ShowModal()
                if res == wx.ID_OK:
                    global customColor
                    customColor = str(col.GetColourData().GetColour().GetAsString(wx.C2S_HTML_SYNTAX))

            else:
                return str(gridColor.GetString(gridColor.GetSelection()))

        gridType.Bind(wx.EVT_CHOICE, OnType)
        gridColor.Bind(wx.EVT_CHOICE, OnColor)

        gridDialog.CenterOnScreen()
        result = gridDialog.ShowModal()

        if result == wx.ID_OK:

            if gridOn.IsChecked():

                if str(gridColor.GetString(gridColor.GetSelection())) == 'custom...':
                    self.get_graph().get_axes().grid(True, linestyle=str(gridType.GetString(gridType.GetSelection())),
                                                     color=customColor)
                    self.set_isGrid(True)

                else:
                    self.get_graph().get_axes().grid(True, linestyle=str(gridType.GetString(gridType.GetSelection())),
                                                     color='xkcd:'+str(gridColor.GetString(gridColor.GetSelection())))
                    self.set_isGrid(True)

            if gridOff.IsChecked():
                self.get_graph().get_axes().grid(False)
                self.set_isGrid(False)

            self.get_graph().get_canvas().draw()

            # xcurr = []
            # xnew = []
            #
            # for t in self.get_graph().get_axes().get_xticklabels():
            #
            #     xcurr.append(t.get_text())
            #     num = t.get_text()
            #     if '−' in num:
            #         print('yeet')
            #         newnum = num.replace('−', '-')
            #         xnew.append(np.round_(np.power(10, float(newnum)), 4))
            #     else:
            #         xnew.append(np.round_(np.power(10, float(num)), 4))
            #
            # self.get_graph().get_axes().set_xticklabels(xnew)
            # self.get_graph().get_canvas().draw()

    def OnGraphColor(self, event):

        global customDataColor
        customDataColor = ''

        graphColorDialog = wx.Dialog(self, wx.ID_ANY, "Graph Color", size=(175, 200))
        graphColorPanel = wx.Panel(graphColorDialog, wx.ID_ANY)

        dataColorTxt = wx.StaticText(graphColorPanel, -1, 'Data', pos=(10, 80))

        dataColor = wx.Choice(graphColorPanel, wx.ID_ANY, pos=(50, 80),
                              choices=['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'custom...'])

        okbutton = wx.Button(graphColorPanel, wx.ID_OK, pos=(65, 130))

        def OnDataColor(event):

            global customDataColor
            if dataColor.GetString(dataColor.GetCurrentSelection()) == 'custom...':
                data = wx.ColourData()
                col = wx.ColourDialog(self, data)
                col.CenterOnScreen()
                res = col.ShowModal()
                if res == wx.ID_OK:
                    customDataColor = str(col.GetColourData().GetColour().GetAsString(wx.C2S_HTML_SYNTAX))

            else:
                customDataColor = 'xkcd:' + str(dataColor.GetString(dataColor.GetSelection()))

            self.get_graph().set_dataColor(customDataColor)

        dataColor.Bind(wx.EVT_CHOICE, OnDataColor)

        graphColorDialog.CenterOnScreen()
        result = graphColorDialog.ShowModal()

        if result == wx.ID_OK:

            self.get_graph().get_axes().cla()
            self.get_graph().set_annot(
                self.get_graph().get_axes().annotate("", xy=(0, 0), xytext=(8, 8), textcoords="figure pixels",
                                                     bbox=dict(boxstyle="round", fc="w"),
                                                     arrowprops=dict(arrowstyle="->")))
            self.get_graph().get_annot().set_visible(False)

            self.get_graph().get_axes().scatter(self.get_graph().get_x(),
                                                self.get_graph().get_y_plot(),
                                                marker=self.get_graph().get_dataSymbol(),
                                                s=self.get_graph().get_dataSymbolSize(),
                                                color=self.get_graph().get_dataColor())

            if self.get_graph().get_isLegend():
                self.get_graph().get_axes().legend(labels=self.get_graph().get_legendText(), loc=self.get_graph().get_legendLoc())

            if self.get_isGrid():
                self.get_graph().get_axes().grid(True)
                self.set_isGrid(True)

            self.get_graph().label(self.get_graph().get_titlelabel(),
                                   self.get_graph().get_xlabel(),
                                   self.get_graph().get_ylabel())

            self.get_graph().get_axes().set_xscale('log')
            self.get_graph().get_canvas().draw()

    def add_legend(self, loc, txt):
        self.get_graph().get_axes().legend(labels=txt, loc=loc)
        self.get_graph().set_isLegend(True)
        self.get_graph().set_legendLoc(loc)

    def get_graph(self): return self.graph
    def get_annotated(self): return self.annotated
    def set_annotated(self, ann): self.annotated = ann
    def get_ann(self): return self.ann
    def set_ann(self, a): self.ann = a
    def get_isGrid(self): return self.isGrid
    def set_isGrid(self, g): self.isGrid = g
    def get_saved_legend_text(self): return self.legend_text
    def set_saved_legend_text(self, txt): self.legend_text = txt
# class for the dialog which allows the user to set the x-regression values based on the opened data sets
class XRValuesDialog(wx.Dialog):
    # Dynamic UI stuff
    def __init__(self, parent, x):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "X-Axis Regression Values", size=(450, 350))
        self.main_panel = wx.Panel(self, wx.ID_ANY)

        self.sep = wx.StaticLine(self.main_panel, -1, pos=(10,250), size=(420, -1), style=wx.LI_HORIZONTAL)

        self.scroll_panel = ScrolledPanel(self.main_panel, wx.ID_ANY, pos=(0,0), size=(415, 225))
        self.scroll_panel.SetupScrolling(scroll_y=True, rate_x=20)

        self.btn_panel = wx.Panel(self.main_panel, wx.ID_ANY, pos=(0,275), size=(450, 75))

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.lblxvals = wx.StaticText(self.scroll_panel, label="X Regression Values", pos=(20, 20))
        self.sizer.Add(0, 3, 0)
        self.sizer.Add(self.lblxvals, 1, wx.ALL, 5)

        self.txt_ctrl = []
        # dynamically add a new textbox for each file that is opened
        for value in x:
            # default textbox value is the name of the file
            txt = wx.TextCtrl(self.scroll_panel, value=str(value), pos=(140, 20), size=(250, -1))
            self.txt_ctrl.append(txt)
            self.sizer.Add(txt, 0, wx.ALL, 5)

        self.ok = wx.Button(self.btn_panel, id=wx.ID_OK, label="OK", pos=(240, 0))
        self.cancel = wx.Button(self.btn_panel, id=wx.ID_CANCEL, label="Cancel", pos=(335, 0))

        self.xvals_txt = ''
        self.scroll_panel.SetSizer(self.sizer)
        self.scroll_panel.Layout()
        self.scroll_panel.Fit()
    # function for closing the dialog
    def OnQuit(self, event):

        self.Destroy()
    # function to save the user input values
    def SaveString(self):

        vals = []

        for values in self.get_txtctrl():

            vals.append(float(values.GetValue()))

        self.set_xvals(vals)

    def get_xvals(self): return self.xvals_txt
    def set_xvals(self, x): self.xvals_txt = x
    def get_txtctrl(self): return self.txt_ctrl

class HHPlotDialog(wx.Frame):

    def __init__(self, parent, title):
        # wx.Dialog.__init__(self, parent, wx.ID_ANY, "Graph", size=(640, 480))
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(640, 480), style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)

        self.parent = parent
        self.graph = HHPlot(self)

        self.filemenu = wx.Menu()
        self.open = self.filemenu.Append(wx.ID_ANY, 'Open', 'Open')
        self.Bind(wx.EVT_MENU, self.OnOpen, self.open)

        # creates the menu bar and adds the tab to the top of the page
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(self.filemenu, 'File')
        self.SetMenuBar(self.menuBar)

        self.delimiter = ''
        self.file1 = []
        self.file2 = []
        self.filename1 = ''
        self.filename2 = ''

    def OnOpen(self, event):

        self.parent.EnableCloseButton(False)
        #     # create the open file dialog, if a file exists the user is able to open it will probably change it so
        #     # only the MountainsMap data file format can be opened
        openFileDialog = wx.FileDialog(self.parent, "Open",  # wildcard="CSV UTF-8 (Comma delimited) (*.csv)|*.csv" ,# \ "
                                       # "TXT (*.txt)|*.txt",
                                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE | wx.STAY_ON_TOP)
        openFileDialog.CenterOnScreen()
        # shows the dialog on screen
        result = openFileDialog.ShowModal()
        # only opens the file if 'open' in dialog is pressed otherwise if 'cancel' in dialog is pressed closes dialog
        if result == wx.ID_OK:
            # gets the file path
            filepath = openFileDialog.GetPaths()

            if len(filepath) != 2:

                print('Select only 2 surface files with format XYZ coordinates')
            else:

                self.openfiles(filepath)

            self.parent.EnableCloseButton(True)
            return True
        elif result == wx.ID_CANCEL:
            self.parent.EnableCloseButton(True)
            return False

    def openfiles(self, filepath):

        self.filename1 = filepath[0].split("\\")[len(filepath[0].split("\\")) - 1]
        self.filename2 = filepath[1].split("\\")[len(filepath[1].split("\\")) - 1]

        with open(filepath[0]) as f:

            lines = f.readlines()

            values = '01234567890.-\n'

            for i in lines[0]:

                if i not in values:
                    self.delimiter = i
                    break

            for line in lines:

                line = line.split(self.delimiter)
                self.file1.append(np.array(line, dtype=np.float64))

            f.close()

        with open(filepath[1]) as f:

            lines = f.readlines()

            values = '01234567890.-\n'

            for i in lines[0]:

                if i not in values:
                    self.delimiter = i
                    break

            for line in lines:

                line = line.split(self.delimiter)
                self.file2.append(np.array(line, dtype=np.float64))

            f.close()

        print(self.filename1)
        print(self.filename2)
        print(len(self.file1))
        print(len(self.file2))

        z6 = []
        z7 = []

        for i in zip(self.file1, self.file2):

            if i[0][0] == i[1][0] and i[0][1] == i[1][1]:
                z6.append(i[0][2])
                z7.append(i[1][2])

        self.graph.plot(x=z6, y=z7)
