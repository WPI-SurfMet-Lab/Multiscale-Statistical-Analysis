import warnings
import numpy as np
import wx
import CurveFit
from matplotlib import use
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx as NavigationToolbar
from matplotlib.pyplot import figure, yscale
from scipy.optimize import OptimizeWarning
from GraphDialogs import SymbolDialog
from GraphDialogs import LegendDialog
from GraphDialogs import LabelDialog

import logging
import traceback

use('WXAgg')

# Class for the R^2 by scale plots to generate the graphs
class R2byScalePlot(wx.Panel):

    def __init__(self, parent, data, error_txt, tree_menu, root, id):
        # gets the Panel properties
        wx.Panel.__init__(self, parent, size=wx.Size(640, 480), style=wx.SIMPLE_BORDER)
        # id corresponding to regression curve type
        self.id = id
        # to attach the graph in left hand column
        self.root = root
        self.parent = parent
        self.figure = figure()
        # defines the plot using subplot function
        self.axes = self.get_fig().add_subplot(111)

        self.canvas = FigureCanvas(self, -1, self.get_fig())
        self.Fit()
        # get the x and y values for the regression plots from main data object
        self.x = data.get_results_scale()
        self.xr = data.get_x_regress()
        self.y = data.get_regress_sets()
        self.y_plot = []

        self.save_xr = []

        self.data = data
        self.tree_menu = tree_menu

        self.isSaved = False
        self.isLegend = False
        self.legendLoc = 'best'

        # -------------------------- GRAPH LABELS ---------------------------------------
        self.titlelabel = 'Scale by R$^2$'
        self.xlabel = 'Scale ({})'.format(self.data.get_strings()[4][0])
        self.ylabel = 'R$^2$'
        self.get_axes().set_title(self.get_titlelabel())
        self.get_axes().set_xlabel(self.get_xlabel())
        self.get_axes().set_ylabel(self.get_ylabel())
        self.error_txt = error_txt
        # ------------------------- HOVER ANNOTATE -------------------------------
        self.scatter_plot = None
        self.annot = self.get_axes().annotate("", xy=(0, 0), xytext=(0.025, 0.025), textcoords="axes fraction",
                                              bbox=dict(boxstyle="round", fc="w"),
                                              arrowprops=dict(arrowstyle="->"))
        self.get_annot().set_visible(False)
        # function to update the annotation when hovering over a point
        def update_annot(ind):

            pos = self.get_scatter_plot().get_offsets()[ind["ind"][0]]
            self.get_annot().xy = pos
            text = "Point \n{}, {}".format(np.round_(pos[0], 5), np.round_(pos[1], 3))
            self.get_annot().set_text(text)
            self.get_annot().get_bbox_patch().set_alpha(0.4)

        # function to display the annotation when hovering over a point
        def hover(event):
            vis = self.get_annot().get_visible()
            if event.inaxes == self.get_axes():
                cont, ind = self.get_scatter_plot().contains(event)
                if cont:
                    update_annot(ind)
                    self.get_annot().set_visible(True)
                    self.get_fig().canvas.draw_idle()
                else:
                    if vis:
                        self.get_annot().set_visible(False)
                        self.get_fig().canvas.draw_idle()
        self.get_fig().canvas.mpl_connect("motion_notify_event", hover)

        # ------------------ CLICK ON POINTS TO MAKE REGRESSION PLOT --------------------------
        # function to double click on a point and see the corresponding regression point at that scale
        def pick_point(event):

            if event.dblclick:
                if event.inaxes == self.get_axes():
                    cont, ind = self.get_scatter_plot().contains(event)
                    if cont:
                        # Following 5 lines are to get the regression data for the selected scale
                        pos = self.get_scatter_plot().get_offsets()[ind["ind"][0]]
                        scale = pos[0]

                        index = self.get_data().get_results_scale().index(scale)
                        xregress = self.get_save_xr()
                        yregress = self.get_data().get_regress_sets()[index]
                        # checks the given id to perform the correct regression using the data determined above
                        # this needs error exceptions still
                        regression_choices = \
                            {0:("Proportional Regression Plot", dialog.get_graph().proportional_fit_plot, "Proportional Regression at"),
                             1:("Linear Regression Plot", dialog.get_graph().linear_fit_plot, "Linear Regression at"),
                             2:("Quadratic Regression Plot", dialog.get_graph().quadratic_fit_plot, "Quadratic Regression at"),
                             3:("Cubic Regression Plot", dialog.get_graph().cubic_fit_plot, "Cubic Regression at"),
                             4:("Quartic Regression Plot", dialog.get_graph().quartic_fit_plot, "Quartic Regression at"),
                             5:("Quintic Regression Plot", dialog.get_graph().quintic_fit_plot, "Quintic Regression at"),
                             6:("Power Regression Plot", dialog.get_graph().power_fit_plot, "Power Regression at"),
                             7:("Inverse Regression Plot", dialog.get_graph().inverse_fit_plot, "Inverse Regression at"),
                             8:("Inverse Squared Regression Plot", dialog.get_graph().inverse_squared_fit_plot, "Inverse Squared Regression at"),
                             9:("Natural Exponent Regression Plot", dialog.get_graph().naturalexp_fit_plot, "Natural Exponent Regression at"),
                             10:("Natural Log Regression Plot", dialog.get_graph().loge_fit_plot, "Natural Log Regression at"),
                             11:("Log10 Regression Plot", dialog.get_graph().log10_fit_plot, "Log10 Regression at"),
                             12:("Inverse Exponent Regression Plot", dialog.get_graph().inverseexp_fit_plot, "Inverse Exponent Regression at"),
                             13:("Sin Regression Plot", dialog.get_graph().sin_fit_plot, "Sin Regression at"),
                             14:("Cos Regression Plot", dialog.get_graph().cos_fit_plot, "Cos Regression at"),
                             15:("Gaussian Regression Plot", dialog.get_graph().gaussian_fit_plot, "Gaussian Regression at")}
                        title, plot_func, menu_text = regression_choices[self.id]

                        dialog = RegressionSelectDialog(self.get_parent(), title,
                                                        data.get_results_scale(),
                                                        xregress, yregress, index)
                        plot_func()
                        tree_menu.AppendItem(self.get_root(), menu_text + " " + str(scale), data=dialog)

        self.get_fig().canvas.mpl_connect("button_press_event", pick_point)

        # ---------------------------------- GRAPH STYLE DEFAULTS---------------------------
        self.dataColor = 'xkcd:blue'
        self.dataSymbol = 'o'
        self.dataSymbolSize = 8
        self.legend_text = ['data']

        # --------------------- SIZER ---------------------------------
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND) # wx.SHAPED keeps aspect ratio)
        self.add_toolbar()
        self.SetSizer(self.sizer)
        self.Fit()
    # adds the toolbar to the bottom of the plot
    def add_toolbar(self):
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        # By adding toolbar in sizer, we are able to put it at the bottom
        # of the frame - so appearance is closer to GTK version.
        self.sizer.Add(self.toolbar, 0, wx.EXPAND)
        # update the axes menu on the toolbar
        self.toolbar.update()
    # sets and updates the plots labels
    def label(self, title, xlabel, ylabel):

        # labels the title, ylabel, xlabel of the regression plot from user input
        self.get_axes().set_title(title)
        self.get_axes().set_xlabel(xlabel)
        self.get_axes().set_ylabel(ylabel)
        # updates the regression plot's label
        self.get_canvas().draw()

    # uses various regression functions to calculate R^2 values same as following functions but with respective curve type
    def plot_fit(self, data_func, fit_func, error_str):
        warnings.simplefilter('error', OptimizeWarning)
        # iterate over all sets of y-values in regression
        for y_values in self.get_y():
            try:
                # regress against the x-values get linear equation coefficients
                popt, pcov = data_func(np.array(self.get_xr()), np.array(y_values))
                # calculate R^2 values
                r2 = CurveFit.r_squared(np.array(y_values), fit_func(np.array(self.get_xr()), *popt))
            except (RuntimeError, Exception, Warning, TypeError, OptimizeWarning) as e:
                self.get_error_txt().AppendText(error_str + str(e) + '\n')
                # if error R^2 value is set to 0. error is likely due to not being able to find the functional correlation
                r2 = 0
            # append R^2 value to the y values to be plotted
            self.y_plot.append(r2)
        # scatter the R^2 values by the scales at which they occur
        self.set_scatter_plot(self.get_axes().scatter(np.array(self.get_x()), np.array(self.get_y_plot()),
                                                      s=self.get_dataSymbolSize(),
                                                      marker=self.get_dataSymbol(),
                                                      color=self.get_dataColor()))
        self.set_save_xr(np.array(self.get_xr()))
        # set the scale axis to log
        self.get_axes().set_xscale('log')
        self.get_canvas().draw()

    def linear_plot(self):
        self.plot_fit(CurveFit.linear_data, CurveFit.linear_fit, "Linear R^2: ")

    def proportional_plot(self):
        self.plot_fit(CurveFit.prop_data, CurveFit.prop_fit, "Proportional R^2: ")

    def quadratic_plot(self):
        self.plot_fit(CurveFit.quad_data, CurveFit.quad_fit, "Quadratic R^2: ")

    def cubic_plot(self):
        self.plot_fit(CurveFit.cubic_data, CurveFit.cubic_fit, "Cubic R^2: ")

    def quartic_plot(self):
        self.plot_fit(CurveFit.quartic_data, CurveFit.quartic_fit, "Quartic R^2: ")

    def quintic_plot(self):
        self.plot_fit(CurveFit.quintic_data, CurveFit.quintic_fit, "Quintic R^2: ")

    def power_plot(self):
        self.plot_fit(CurveFit.power_data, CurveFit.power_fit, "Power R^2: ")

    def inverse_plot(self):
        self.plot_fit(CurveFit.inverse_data, CurveFit.inverse_fit, "Inverse R^2: ")

    def inverse_squared_plot(self):
        self.plot_fit(CurveFit.insq_data, CurveFit.insq_fit, "Inverse Square R^2: ")

    def natural_exp_plot(self):
        self.plot_fit(CurveFit.nexp_data, CurveFit.nexp_fit, "Natural Exponent R^2: ")

    def loge_plot(self):
        self.plot_fit(CurveFit.ln_data, CurveFit.ln_fit, "Natural Log R^2: ")

    def log10_plot(self):
        self.plot_fit(CurveFit.b10log_data, CurveFit.b10log_fit, "Log10 R^2: ")

    def inverse_exp_plot(self):
        self.plot_fit(CurveFit.invexp_data, CurveFit.invexp_fit, "Inverse Exponent R^2: ")

    def sin_plot(self):
        self.plot_fit(CurveFit.sine_data, CurveFit.sine_fit, "Sine R^2: ")

    def cos_plot(self):
        self.plot_fit(CurveFit.cosine_data, CurveFit.cosine_fit, "Cosine R^2: ")

    def gaussian_plot(self):
        self.plot_fit(CurveFit.gauss_data, CurveFit.gauss_fit, "Gaussian R^2: ")

    def get_axes(self): return self.axes
    def get_x(self): return self.x
    def get_y(self): return self.y
    def get_fig(self): return self.figure
    def get_canvas(self): return self.canvas
    def get_saved(self): return self.isSaved
    def set_saved(self, s): self.isSaved = s
    def get_isLegend(self): return self.isLegend
    def set_isLegend(self, s): self.isLegend = s
    def get_titlelabel(self): return self.titlelabel
    def set_titlelabel(self, title): self.titlelabel = title
    def get_xlabel(self): return self.xlabel
    def set_xlabel(self, xlabel): self.xlabel = xlabel
    def get_ylabel(self): return self.ylabel
    def set_ylabel(self, ylabel): self.ylabel = ylabel
    def get_legendLoc(self): return self.legendLoc
    def set_legendLoc(self, loc): self.legendLoc = loc
    def get_xr(self): return self.xr
    def get_y_plot(self): return self.y_plot
    def get_error_txt(self): return self.error_txt
    def get_scatter_plot(self): return self.scatter_plot
    def set_scatter_plot(self, scatter): self.scatter_plot = scatter
    def get_annot(self): return self.annot
    def set_annot(self, a): self.annot = a
    def get_pos(self): return self.pos
    def set_pos(self, pos): self.pos = pos
    def get_data(self): return self.data
    def get_parent(self): return self.parent
    def get_root(self): return self.root
    def get_id(self): return self.id
    def get_dataColor(self): return self.dataColor
    def set_dataColor(self, color): self.dataColor = color
    def get_dataSymbol(self): return self.dataSymbol
    def set_dataSymbol(self, symbol): self.dataSymbol = symbol
    def get_dataSymbolSize(self): return self.dataSymbolSize
    def set_dataSymbolSize(self, size): self.dataSymbolSize = size
    def get_legendText(self): return self.legend_text
    def set_legendText(self, txt): self.legend_text = txt
    def get_save_xr(self): return self.save_xr
    def set_save_xr(self, x): self.save_xr = x
# Class for single scale scatter plots with regression line
# y-axis is relative area
# x-axis is regression parameter
class RegressionPlot(wx.Panel):

    def __init__(self, parent, x, xr, y, swb, tree):
        # gets the Panel properties
        wx.Panel.__init__(self, parent, size=wx.Size(640, 480), style=wx.SIMPLE_BORDER)

        self.tree_menu = tree
        self.workbook = self.tree_menu.GetItemData(swb).get_wb()
        self.swb = swb
        self.figure = figure()
        # defines the plot
        self.axes = self.get_fig().add_subplot(111)

        self.canvas = FigureCanvas(self, -1, self.get_fig())
        self.Fit()
        self.x = x
        self.xr = np.array(xr).astype(np.float)
        self.y = y
        self.yr = None

        self.isSaved = False
        self.isLegend = False
        self.legendLoc = 'best'

        # ---- Regression line ---
        self.mn = np.min(self.get_xr())
        self.mx = np.max(self.get_xr())
        self.x_plot = np.linspace(self.mn, self.mx, num=5*len(self.get_xr()))
        # -------------------------- GRAPH LABELS ---------------------------------------
        self.titlelabel = 'Relative Area Regression'
        self.xlabel = ''
        self.ylabel = 'Relative Area'
        self.get_axes().set_title(self.get_titlelabel())
        self.get_axes().set_xlabel(self.get_xlabel())
        self.get_axes().set_ylabel(self.get_ylabel())

        self.best_r_squared = 0
        self.best_scale = 0
        self.curve = None
        # ------------------------- HOVER ANNOTATE -------------------------------
        self.scatter_plot = None
        self.annot = self.get_axes().annotate("", xy=(0, 0), xytext=(0.025, 0.025), textcoords="axes fraction",
                                              bbox=dict(boxstyle="round", fc="w"),
                                              arrowprops=dict(arrowstyle="->"))
        self.get_annot().set_visible(False)

        self.line_annot = self.get_axes().annotate("", xy=(0,0),
                                                   xytext=(0.5,0.5), textcoords="figure fraction",
                                                   bbox=dict(boxstyle="round", fc="w"),
                                                   arrowprops=dict(arrowstyle="->"))
        self.line_annot.set_visible(False)
        self.line_annot.draggable()
        self.line_annot_pos = [0, 0]
        # this function is described in class R2byScalePlot
        def update_annot(ind):

            pos = self.get_scatter_plot().get_offsets()[ind["ind"][0]]
            self.get_annot().xy = pos
            text = "Point \n({}, {})".format(pos[0], pos[1])
            self.get_annot().set_text(text)
            self.get_annot().get_bbox_patch().set_alpha(0.4)
        # this function is described in class R2byScalePlot
        def hover(event):
            vis = self.get_annot().get_visible()
            if event.inaxes == self.get_axes():
                cont, ind = self.get_scatter_plot().contains(event)
                if cont:
                    update_annot(ind)
                    self.get_annot().set_visible(True)
                    self.get_fig().canvas.draw_idle()
                else:
                    if vis:
                        self.get_annot().set_visible(False)
                        self.get_fig().canvas.draw_idle()
        self.get_fig().canvas.mpl_connect("motion_notify_event", hover)

        # ---------------------------------- GRAPH STYLE ---------------------------
        self.dataColor = 'xkcd:blue'
        self.lineColor = 'xkcd:red'
        self.dataSymbol = 'o'
        self.dataSymbolSize = 24
        self.legend_text = ['line', 'data']

        # --------------------- SIZER ---------------------------------
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.add_toolbar()
        self.SetSizer(self.sizer)
        self.Fit()

        self.popt = ''

    # function to add the toolbar to the bottom of the plot panel
    def add_toolbar(self):
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        # By adding toolbar in sizer, we are able to put it at the bottom
        # of the frame - so appearance is closer to GTK version.
        self.sizer.Add(self.toolbar, 0, wx.EXPAND)
        # update the axes menu on the toolbar
        self.toolbar.update()
    # function to set the labels of the graph form user input
    def label(self, title, xlabel, ylabel):

        # labels the title, ylabel, xlabel of the regression plot from user input
        self.get_axes().set_title(title)
        self.get_axes().set_xlabel(xlabel)
        self.get_axes().set_ylabel(ylabel)
        # updates the regression plot's label
        self.get_canvas().draw()

    # function to perform the regression of the scattered data points.
    # produces the scatter plot at the scale with the highest correlation
    def plot_fit(self, data_func, fit_func, popt_str):
        bestr2 = -1
        bestscale = -1
        poptbest = None
        pcovbest = None
        y = None

        for y_values in self.get_y():
            try:
                popt, pcov = data_func(np.array(self.get_xr()), np.array(y_values))
                fit_func(self.get_x_plot(), *popt)
                r2 = CurveFit.r_squared(np.array(y_values), fit_func(self.get_xr(), *popt))
            except (RuntimeError, Exception, Warning, TypeError) as e:
                if __debug__:
                    r2 = 0
                    popt = 0
                    pcov = 0
                else:
                    raise e
            if r2 > bestr2:
                bestr2 = r2
                bestscale = self.get_x()[self.get_y().index(y_values)]
                y = y_values
                poptbest = popt
                pcovbest = pcov

        best_plot_fit = fit_func(np.array(self.get_x_plot()), *poptbest)
        self.set_yr(np.array(y))
        self.set_curve(best_plot_fit)
        self.set_scatter_plot(self.get_axes().scatter(np.array(self.get_xr()), np.array(y),
                                                      s=self.get_dataSymbolSize(),
                                                      marker=self.get_dataSymbol(),
                                                      color=self.get_dataColor()))
        self.get_axes().plot(self.get_x_plot(), best_plot_fit, '-', color=self.get_lineColor())
        self.get_canvas().draw()

        self.set_popt(popt_str.format(*np.round(poptbest, 3)))

        self.set_best_r_squared(bestr2)
        self.set_best_scale(bestscale)
        self.set_line_annot_pos((int((min(self.get_xr()) + max(self.get_xr())) / 2),
                                 fit_func(int((min(self.get_xr()) + max(self.get_xr())) / 2),
                                                           *poptbest)))

    def linear_fit_plot(self):
        self.plot_fit(CurveFit.linear_data, CurveFit.linear_fit, 'y = {}x + {}')

    def proportional_fit_plot(self):
        self.plot_fit(CurveFit.prop_data, CurveFit.prop_fit, 'y = {}x')

    def quadratic_fit_plot(self):
        self.plot_fit(CurveFit.quad_data, CurveFit.quad_fit, 'y = {}x^2 + {}x + {}')

    def cubic_fit_plot(self):
        self.plot_fit(CurveFit.cubic_data, CurveFit.cubic_fit, 'y = {}x^3 + {}x^2 + {}x + {}')

    def quartic_fit_plot(self):
        self.plot_fit(CurveFit.quartic_data, CurveFit.quartic_fit, 'y = {}x^4 + {}x^3 + {}x^2 + {}x + {}')

    def quintic_fit_plot(self):
        self.plot_fit(CurveFit.quintic_data, CurveFit.quintic_fit, 'y = {}x^5 + {}x^4 + {]x^3 + {}x^2 + {}x + {}')

    def power_fit_plot(self):
        self.plot_fit(CurveFit.power_data, CurveFit.power_fit, 'y = {}x^{}')

    def inverse_fit_plot(self):
        self.plot_fit(CurveFit.inverse_data, CurveFit.inverse_fit, 'y = {}/x')

    def inverse_squared_fit_plot(self):
        self.plot_fit(CurveFit.insq_data, CurveFit.insq_fit, 'y = {}/x^2')

    def naturalexp_fit_plot(self):
        self.plot_fit(CurveFit.nexp_data, CurveFit.nexp_fit, 'y = {}*exp(-1*{}x) + {}')

    def loge_fit_plot(self):
        self.plot_fit(CurveFit.ln_data, CurveFit.ln_fit, 'y = {}ln({}x)')

    def log10_fit_plot(self):
        self.plot_fit(CurveFit.b10log_data, CurveFit.b10log_fit, 'y = {}log10({}x)')

    def inverseexp_fit_plot(self):
        self.plot_fit(CurveFit.invexp_data, CurveFit.invexp_fit, 'y = {}(1 - exp(-1*{}x)) + {}')

    def sin_fit_plot(self):
        self.plot_fit(CurveFit.sine_data, CurveFit.sine_fit, 'y = {}sin({}x + {}) + {}')

    def cos_fit_plot(self):
        self.plot_fit(CurveFit.cosine_data, CurveFit.cosine_fit, 'y = {}cos({}x + {}) + {}')

    def gaussian_fit_plot(self):
        self.plot_fit(CurveFit.gauss_data, CurveFit.gauss_fit, 'y = {}*exp(-1*((x-{})^2)/({}^2)) + {}')

    def get_axes(self): return self.axes
    def get_x(self): return self.x
    def get_y(self): return self.y
    def get_fig(self): return self.figure
    def get_canvas(self): return self.canvas
    def get_saved(self): return self.isSaved
    def set_saved(self, s): self.isSaved = s
    def get_isLegend(self): return self.isLegend
    def set_isLegend(self, s): self.isLegend = s
    def get_x_plot(self): return self.x_plot
    def get_titlelabel(self): return self.titlelabel
    def set_titlelabel(self, title): self.titlelabel = title
    def get_xlabel(self): return self.xlabel
    def set_xlabel(self, xlabel): self.xlabel = xlabel
    def get_ylabel(self): return self.ylabel
    def set_ylabel(self, ylabel): self.ylabel = ylabel
    def get_legendLoc(self): return self.legendLoc
    def set_legendLoc(self, loc): self.legendLoc = loc
    def get_xr(self): return self.xr
    def set_yr(self, yr): self.yr = yr
    def get_best_r_squared(self): return self.best_r_squared
    def set_best_r_squared(self, r2): self.best_r_squared = r2
    def get_best_scale(self): return self.best_scale
    def set_best_scale(self, scl): self.best_scale = scl
    def get_yr(self): return self.yr
    def get_curve(self): return self.curve
    def set_curve(self, curve): self.curve = curve
    def get_cvf(self): return self.cvf
    def get_scatter_plot(self): return self.scatter_plot
    def set_scatter_plot(self, scatter): self.scatter_plot = scatter
    def get_annot(self): return self.annot
    def set_annot(self, a): self.annot = a
    def get_annot_line(self): return self.line_annot
    def set_annot_line(self, a): self.line_annot = a
    def get_line_annot_pos(self): return self.line_annot_pos
    def set_line_annot_pos(self, pos): self.line_annot_pos = pos
    def get_dataColor(self): return self.dataColor
    def set_dataColor(self, color): self.dataColor = color
    def get_lineColor(self): return self.lineColor
    def set_lineColor(self, color): self.lineColor = color
    def get_dataSymbol(self): return self.dataSymbol
    def set_dataSymbol(self, symbol): self.dataSymbol = symbol
    def get_dataSymbolSize(self): return self.dataSymbolSize
    def set_dataSymbolSize(self, size): self.dataSymbolSize = size
    def get_legendText(self): return self.legend_text
    def set_legendText(self, txt): self.legend_text = txt
    def get_mn(self): return self.mn
    def get_mx(self): return self.mx
    def get_wb(self): return self.workbook
    def get_swb(self): return self.swb
    def get_tree_menu(self): return self.tree_menu
    def get_popt(self): return self.popt
    def set_popt(self, popt): self.popt = popt
# Class for the Scale by area plot as well as complexity by scale
# TODO: rename the class name
class SclbyAreaPlot(wx.Panel):

    def __init__(self, parent, x, y, data):
        # gets the Panel properties
        wx.Panel.__init__(self, parent, size=wx.Size(640, 530), style=wx.SIMPLE_BORDER)
        self.figure = figure()
        # defines the plot not entirely sure what the numbers in add_subplot mean
        self.axes = self.get_fig().add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.get_fig())
        self.Fit()
        self.xlin = x
        self.ylin = y
        self.x = []
        self.y = []
        [self.get_x().append(i) for i in x]
        [self.get_y().append(np.array(i)) for i in y]
        self.isSaved = False
        self.isLegend = False
        self.legendLoc = 'best'

        self.data = data

        # -------------------------- GRAPH LABELS ---------------------------------------
        # self.titlelabel = 'Title'
        # self.xlabel = 'Scale (um^2)'
        # self.ylabel = 'Relative Area'
        self.titlelabel = ''
        self.xlabel = ''
        self.ylabel = ''
        # ------------------------- HOVER ANNOTATE -------------------------------
        self.scatter_plot = None
        self.annot = self.get_axes().annotate("", xy=(0, 0), xytext=(0.025, 0.025), textcoords="axes fraction",
                                              bbox=dict(boxstyle="round", fc="w"),
                                              arrowprops=dict(arrowstyle="->"))
        self.get_annot().set_visible(False)
        # this only currently works for when there is one curve on the area -scale plot or complexoty scale plot
        def update_annot(ind):

            for plot in self.get_scatter_plot():
                pos = plot.get_offsets()[ind["ind"][0]]
                self.get_annot().xy = pos
                text = "{}, {}".format(pos[0], np.round_(np.power(10, pos[1]), 4))
                self.get_annot().set_text(text)
                self.get_annot().get_bbox_patch().set_alpha(0.4)
        def hover(event):
            vis = self.get_annot().get_visible()
            if event.inaxes == self.get_axes():
                for plot in self.get_scatter_plot():
                    cont, ind = plot.contains(event)
                    if cont:
                        update_annot(ind)
                        self.get_annot().set_visible(True)
                        self.get_fig().canvas.draw_idle()
                    else:
                        if vis:
                            self.get_annot().set_visible(False)
                            self.get_fig().canvas.draw_idle()
        self.get_fig().canvas.mpl_connect("motion_notify_event", hover)
        # --------------------- SIZER ---------------------------------
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.add_toolbar()
        self.SetSizer(self.sizer)
        self.Fit()
    # add toolbar to bottom of plot
    def add_toolbar(self):
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        # By adding toolbar in sizer, we are able to put it at the bottom
        # of the frame - so appearance is closer to GTK version.
        self.sizer.Add(self.toolbar, 0, wx.EXPAND)
        # update the axes menu on the toolbar
        self.toolbar.update()
    # add labels to graph based on user inputs
    def label(self, title, xlabel, ylabel):

        # labels the title, ylabel, xlabel of the regression plot from user input
        self.get_axes().set_title(title)
        self.get_axes().set_xlabel(xlabel)
        self.get_axes().set_ylabel(ylabel)
        # updates the regression plot's label
        self.get_canvas().draw()
    # function to create range of floats.
    def frange(self, x, y, jump):
        while x < y:
            yield x
            x += jump
    # draws a scatter plot of the area scale plot
    def draw_plot(self):

        scatterList = []

        # self.get_axes().locator_params(axis='x', nbins=8)
        # self.get_axes().locator_params(axis='y', nbins=6)

        newy = []

        for yvals in self.get_y():
            # plot log of y-values
            scatterList.append(self.get_axes().scatter(self.get_x(), np.log10(yvals), marker="o", s=8))
            newy.append(np.log10(yvals))

        self.set_y(newy)
        self.get_axes().set_title('')
        self.get_axes().set_xlabel(self.data.get_strings()[3][0] + ' ' + self.data.get_strings()[4][0])
        self.get_axes().set_ylabel(self.data.get_strings()[3][1])
        self.set_scatter_plot(scatterList)
        # set the x-scale to log plot
        self.get_axes().set_xscale('log')
        # self.get_axes().set_yscale('log')

        self.get_canvas().draw()

        ycurr = []
        ynew = []
        # update the y-tick labels to be the actual values not log values
        for t in self.get_axes().get_yticklabels():
            ycurr.append(t.get_text())
            num = t.get_text()
            if '−' in num:
                newnum = num.replace('−', '-')
                ynew.append(np.round_(np.power(10, float(newnum)), 4))
            else:
                ynew.append(np.round_(np.power(10, float(num)), 4))

        self.get_axes().set_yticklabels(ynew)
        self.get_canvas().draw()
    # draws a scatter plot of the complexity scale plot
    # tick labels are messed up on complexity scale graph
    def draw_complexity_plot(self):

        scatterList = []

        # self.get_axes().locator_params(axis='x', nbins=8)

        for yvals in self.get_y():
            # Prevent negative input into log10
            if np.any(yvals < 0) :
                raise Exception("Y-values cannot be negative because of log scale.")
            # scatter log of complexity values
            scatterList.append(self.get_axes().scatter(self.get_x(), np.log10(yvals), marker="o", s=8))

        self.get_axes().set_title('')
        self.get_axes().set_xlabel(self.data.get_strings()[3][0] + ' ' + self.data.get_strings()[4][0])
        self.get_axes().set_ylabel(self.data.get_strings()[3][2] + ' log10 scale')
        self.set_scatter_plot(scatterList)
        # set x-axis to log scale
        self.get_axes().set_xscale('log')

        self.get_canvas().draw()

    def get_axes(self): return self.axes
    def get_x(self): return self.x
    def get_y(self): return self.y
    def set_y(self, y): self.y = y
    def get_fig(self): return self.figure
    def get_canvas(self): return self.canvas
    def get_saved(self): return self.isSaved
    def set_saved(self, s): self.isSaved = s
    def get_isLegend(self): return self.isLegend
    def set_isLegend(self, s): self.isLegend = s
    def get_titlelabel(self): return self.titlelabel
    def set_titlelabel(self, title): self.titlelabel = title
    def get_xlabel(self): return self.xlabel
    def set_xlabel(self, xlabel): self.xlabel = xlabel
    def get_ylabel(self): return self.ylabel
    def set_ylabel(self, ylabel): self.ylabel = ylabel
    def get_legendLoc(self): return self.legendLoc
    def set_legendLoc(self, loc): self.legendLoc = loc
    def get_scatter_plot(self): return self.scatter_plot
    def set_scatter_plot(self, scatter): self.scatter_plot = scatter
    def get_xlin(self): return self.xlin
    def get_ylin(self): return self.ylin
    def get_annot(self): return self.annot

# --------------------- SCALE SELECTED REGRESSION PLOT ----------------------------------
# Class to produce the regression plots when selecting the R^2 values on the R^2 by scale plot
class RegressionSelectPlot(wx.Panel):

    def __init__(self, parent, x, xr, y, scale):
        # gets the Panel properties
        wx.Panel.__init__(self, parent, size=wx.Size(640, 480), style=wx.SIMPLE_BORDER)

        self.popt = ''

        self.scale = scale
        self.figure = figure()
        # defines the plot not entirely sure what the numbers in add_subplot mean
        self.axes = self.get_fig().add_subplot(111)

        self.canvas = FigureCanvas(self, -1, self.get_fig())
        self.Fit()
        self.x = x
        self.xr = np.array(xr).astype(np.float)
        self.yr = y

        self.isSaved = False
        self.isLegend = False
        self.legendLoc = 'best'

        # ---- Regression line ---
        self.mn = np.min(self.get_xr())
        self.mx = np.max(self.get_xr())
        self.x_plot = np.linspace(self.mn, self.mx, num=5*len(self.get_xr()))
        # -------------------------- GRAPH LABELS ---------------------------------------
        self.titlelabel = 'Relative Area Regression'
        self.xlabel = ''
        self.ylabel = 'Relative Area'
        self.get_axes().set_title(self.get_titlelabel())
        self.get_axes().set_xlabel(self.get_xlabel())
        self.get_axes().set_ylabel(self.get_ylabel())

        self.best_r_squared = 0
        self.best_scale = 0
        self.curve = None
        # ------------------------- HOVER ANNOTATE -------------------------------
        self.scatter_plot = None
        self.annot = self.get_axes().annotate("", xy=(0, 0), xytext=(0.025, 0.025), textcoords="axes fraction",
                                              bbox=dict(boxstyle="round", fc="w"),
                                              arrowprops=dict(arrowstyle="->"))
        self.get_annot().set_visible(False)

        self.line_annot = self.get_axes().annotate("", xy=(0,0),
                                                   xytext=(0.5,0.5), textcoords="figure fraction",
                                                   bbox=dict(boxstyle="round", fc="w"),
                                                   arrowprops=dict(arrowstyle="->"))
        self.line_annot.set_visible(False)
        self.line_annot.draggable()
        self.line_annot_pos = (0,0)

        def update_annot(ind):

            pos = self.get_scatter_plot().get_offsets()[ind["ind"][0]]
            self.get_annot().xy = pos
            text = "Point \n{}, {}".format(pos[0], pos[1])
            self.get_annot().set_text(text)
            self.get_annot().get_bbox_patch().set_alpha(0.4)
        def hover(event):
            vis = self.get_annot().get_visible()
            if event.inaxes == self.get_axes():
                cont, ind = self.get_scatter_plot().contains(event)
                if cont:
                    update_annot(ind)
                    self.get_annot().set_visible(True)
                    self.get_fig().canvas.draw_idle()
                else:
                    if vis:
                        self.get_annot().set_visible(False)
                        self.get_fig().canvas.draw_idle()
        self.get_fig().canvas.mpl_connect("motion_notify_event", hover)

        self.pos = []

        # ---------------------------------- GRAPH STYLE ---------------------------
        self.dataColor = 'xkcd:blue'
        self.lineColor = 'xkcd:red'
        self.dataSymbol = 'o'
        self.dataSymbolSize = 24
        self.legend_text = ['line', 'data']

        # --------------------- SIZER ---------------------------------
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.add_toolbar()
        self.SetSizer(self.sizer)
        self.Fit()
    # function to add toolbar to plot
    def add_toolbar(self):
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        # By adding toolbar in sizer, we are able to put it at the bottom
        # of the frame - so appearance is closer to GTK version.
        self.sizer.Add(self.toolbar, 0, wx.EXPAND)
        # update the axes menu on the toolbar
        self.toolbar.update()
    # function to set plot labels
    def label(self, title, xlabel, ylabel):

        # labels the title, ylabel, xlabel of the regression plot from user input
        self.get_axes().set_title(title)
        self.get_axes().set_xlabel(xlabel)
        self.get_axes().set_ylabel(ylabel)
        # updates the regression plot's label
        self.get_canvas().draw()

    # function scatter the plot and perform the linear regression used in the pick_point function in
    # the R2byScalePlot class
    def fit_plot(self, data_func, fit_func, popt_str):
        popt, pcov = data_func(np.array(self.get_xr()), np.array(self.get_yr()))
        fit_func(self.get_x_plot(), *popt)

        self.set_popt(popt_str.format(*np.round(popt, 3)))

        # calculate R^2 value
        r2 = CurveFit.r_squared(np.array(self.get_yr()), fit_func(self.get_xr(), *popt))

        self.set_curve(fit_func(np.array(self.get_x_plot()), *popt))
        # scatter plot
        self.set_scatter_plot(self.get_axes().scatter(np.array(self.get_xr()), self.get_yr(), s=self.get_dataSymbolSize(),
                                                      marker=self.get_dataSymbol(),
                                                      color=self.get_dataColor()))
        # linear fit line
        self.get_axes().plot(self.get_x_plot(), fit_func(np.array(self.get_x_plot()), *popt), '-', color=self.get_lineColor())
        self.get_canvas().draw()
        self.set_best_r_squared(r2)
        self.set_best_scale(self.get_scale())
        self.set_line_annot_pos((int((min(self.get_xr()) + max(self.get_xr()))/2),
                                 fit_func(int((min(self.get_xr()) + max(self.get_xr()))/2), *popt)))

    def linear_fit_plot(self):
        self.plot_fit(CurveFit.linear_data, CurveFit.linear_fit, 'y = {}x + {}')

    def proportional_fit_plot(self):
        self.plot_fit(CurveFit.prop_data, CurveFit.prop_fit, 'y = {}x')

    def quadratic_fit_plot(self):
        self.plot_fit(CurveFit.quad_data, CurveFit.quad_fit, 'y = {}x^2 + {}x + {}')

    def cubic_fit_plot(self):
        self.plot_fit(CurveFit.cubic_data, CurveFit.cubic_fit, 'y = {}x^3 + {}x^2 + {}x + {}')

    def quartic_fit_plot(self):
        self.plot_fit(CurveFit.quartic_data, CurveFit.quartic_fit, 'y = {}x^4 + {}x^3 + {}x^2 + {}x + {}')

    def quintic_fit_plot(self):
        self.plot_fit(CurveFit.quintic_data, CurveFit.quintic_fit, 'y = {}x^5 + {}x^4 + {]x^3 + {}x^2 + {}x + {}')

    def power_fit_plot(self):
        self.plot_fit(CurveFit.power_data, CurveFit.power_fit, 'y = {}x^{}')

    def inverse_fit_plot(self):
        self.plot_fit(CurveFit.inverse_data, CurveFit.inverse_fit, 'y = {}/x')

    def inverse_squared_fit_plot(self):
        self.plot_fit(CurveFit.insq_data, CurveFit.insq_fit, 'y = {}/x^2')

    def naturalexp_fit_plot(self):
        self.plot_fit(CurveFit.nexp_data, CurveFit.nexp_fit, 'y = {}*exp(-1*{}x) + {}')

    def loge_fit_plot(self):
        self.plot_fit(CurveFit.ln_data, CurveFit.ln_fit, 'y = {}ln({}x)')

    def log10_fit_plot(self):
        self.plot_fit(CurveFit.b10log_data, CurveFit.b10log_fit, 'y = {}log10({}x)')

    def inverseexp_fit_plot(self):
        self.plot_fit(CurveFit.invexp_data, CurveFit.invexp_fit, 'y = {}(1 - exp(-1*{}x)) + {}')

    def sin_fit_plot(self):
        self.plot_fit(CurveFit.sine_data, CurveFit.sine_fit, 'y = {}sin({}x + {}) + {}')

    def cos_fit_plot(self):
        self.plot_fit(CurveFit.cosine_data, CurveFit.cosine_fit, 'y = {}cos({}x + {}) + {}')

    def gaussian_fit_plot(self):
        self.plot_fit(CurveFit.gauss_data, CurveFit.gauss_fit, 'y = {}*exp(-1*((x-{})^2)/({}^2)) + {}')

    def get_axes(self): return self.axes
    def get_x(self): return self.x
    # def get_y(self): return self.y
    def get_fig(self): return self.figure
    def get_canvas(self): return self.canvas
    def get_saved(self): return self.isSaved
    def set_saved(self, s): self.isSaved = s
    def get_isLegend(self): return self.isLegend
    def set_isLegend(self, s): self.isLegend = s
    def get_x_plot(self): return self.x_plot
    def get_titlelabel(self): return self.titlelabel
    def set_titlelabel(self, title): self.titlelabel = title
    def get_xlabel(self): return self.xlabel
    def set_xlabel(self, xlabel): self.xlabel = xlabel
    def get_ylabel(self): return self.ylabel
    def set_ylabel(self, ylabel): self.ylabel = ylabel
    def get_legendLoc(self): return self.legendLoc
    def set_legendLoc(self, loc): self.legendLoc = loc
    def get_xr(self): return self.xr
    def set_yr(self, yr): self.yr = yr
    def get_best_r_squared(self): return self.best_r_squared
    def set_best_r_squared(self, r2): self.best_r_squared = r2
    def get_best_scale(self): return self.best_scale
    def set_best_scale(self, scl): self.best_scale = scl
    def get_yr(self): return self.yr
    def get_curve(self): return self.curve
    def set_curve(self, curve): self.curve = curve
    def get_scatter_plot(self): return self.scatter_plot
    def set_scatter_plot(self, scatter): self.scatter_plot = scatter
    def get_annot(self): return self.annot
    def set_annot(self, a): self.annot = a
    def get_annot_line(self): return self.line_annot
    def set_annot_line(self, a): self.line_annot = a
    def get_line_annot_pos(self): return self.line_annot_pos
    def set_line_annot_pos(self, pos): self.line_annot_pos = pos
    def get_pos(self): return self.pos
    def set_pos(self, pos): self.pos = pos
    def get_scale(self): return self.scale
    def get_dataColor(self): return self.dataColor
    def set_dataColor(self, color): self.dataColor = color
    def get_lineColor(self): return self.lineColor
    def set_lineColor(self, color): self.lineColor = color
    def get_dataSymbol(self): return self.dataSymbol
    def set_dataSymbol(self, symbol): self.dataSymbol = symbol
    def get_dataSymbolSize(self): return self.dataSymbolSize
    def set_dataSymbolSize(self, size): self.dataSymbolSize = size
    def get_legendText(self): return self.legend_text
    def set_legendText(self, txt): self.legend_text = txt
    def get_mn(self): return self.mn
    def get_mx(self): return self.mx
    def get_popt(self): return self.popt
    def set_popt(self, popt): self.popt = popt


# Dialog for the Regression select plot which contains the graph and menu for graph options
class RegressionSelectDialog(wx.Frame):

    def __init__(self, parent, title, x, xr, y, scale):
        # wx.Dialog.__init__(self, parent, wx.ID_ANY, "Graph", size=(640, 480))
        wx.Frame.__init__(self, parent, title=title, size=(640, 530), style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.graph = RegressionSelectPlot(self, x, xr, y, scale)
        # ------------------- Regression stuff -----------------------

        self.data_scale = x

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
    # function to save image of the plot
    def OnSave(self, event):
        # dialog to save a file
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
    # function to close the dialog
    def OnClose(self, event):

        self.Hide()
    # function to get labels of user input
    def OnLabel(self, event):
        # gets the current labels
        t = self.graph.get_axes().get_title()
        x = self.graph.get_axes().get_xlabel()
        y = self.graph.get_axes().get_ylabel()
        # create the label dialog with current labels in text boxes
        labelDialog = LabelDialog(self, t, x, y)
        labelDialog.CenterOnScreen()
        labelDialog.ShowModal()
        # update the new labels
        self.get_graph().set_titlelabel(labelDialog.get_title())
        self.get_graph().set_xlabel(labelDialog.get_xaxis())
        self.get_graph().set_ylabel(labelDialog.get_yaxis())

        # sets the title, xlabel, ylabel of the regression plot to the user inputs
        self.get_graph().label(labelDialog.get_title(), labelDialog.get_xaxis(), labelDialog.get_yaxis())
    # function to show the legend on the plot
    def OnLegend(self, event):
        # create the legend dialog
        legendDialog = LegendDialog(self, self.get_saved_legend_text())
        legendDialog.CenterOnScreen()
        res = legendDialog.ShowModal()
        # when pressing ok button
        if res == wx.ID_OK:
            # save the strings for the legend in the text boxes
            legendDialog.SaveString()
            text_list = legendDialog.get_legend_text()
            self.set_saved_legend_text(text_list)
            # display the legend in selected area or remove legend
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
    # function to add the legend to the graph
    def add_legend(self, loc, txt):
        self.get_graph().get_axes().legend(labels=txt, loc=loc)
        self.get_graph().set_isLegend(True)
        self.get_graph().set_legendLoc(loc)
    # function to put a grid on the graph
    def OnGrid(self, event):
        # variable to hold the color selected for the grid
        global customColor
        customColor = ''
        # make the basic grid dialog
        # Update: this could be its own class
        gridDialog = wx.Dialog(self, wx.ID_ANY, "Grid", size=(175, 200))
        gridPanel = wx.Panel(gridDialog, wx.ID_ANY)
        # add on / off check boxes
        gridOn = wx.CheckBox(gridPanel, wx.ID_ANY, label="Grid On", pos=(10, 10))
        gridOff = wx.CheckBox(gridPanel, wx.ID_ANY, label="Grid Off", pos=(80, 10))

        gridTypeTxt = wx.StaticText(gridPanel, -1, 'Style', pos=(10,45))
        gridColorTxt = wx.StaticText(gridPanel, -1, 'Color', pos=(10, 80))
        # choice selectors to select the style and grid color
        gridType = wx.Choice(gridPanel, wx.ID_ANY, pos=(50, 45), choices=['solid', 'dashed', 'dotted', 'dashdot'])
        gridColor = wx.Choice(gridPanel, wx.ID_ANY, pos=(50, 80), choices=['black', 'dark grey', 'grey', 'light grey', 'custom...'])
        # the ok button on the dialog
        okbutton = wx.Button(gridPanel, wx.ID_OK, pos=(65, 130))
        # get the grid style
        def OnType(event): return str(gridType.GetString(gridType.GetSelection()))
        # get the selected color
        def OnColor(event):
            # there are default colors or select custom colors using the color dialog
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
        # when the ok button is pressed
        if result == wx.ID_OK:
            # display the grid with the given color and style
            if gridOn.IsChecked():

                if str(gridColor.GetString(gridColor.GetSelection())) == 'custom...':
                    self.get_graph().get_axes().grid(True, linestyle=str(gridType.GetString(gridType.GetSelection())),
                                                     color=customColor)
                    self.set_isGrid(True)

                else:

                    self.get_graph().get_axes().grid(True, linestyle=str(gridType.GetString(gridType.GetSelection())),
                                                     color='xkcd:'+str(gridColor.GetString(gridColor.GetSelection())))
                    self.set_isGrid(True)
            # remove the grid from the graph if off
            if gridOff.IsChecked():
                self.get_graph().get_axes().grid(False)
                self.set_isGrid(False)

            self.get_graph().get_canvas().draw()
    # function to change the symbol and size of the symbol in the scatter plot
    def OnSymbol(self, event):
        # make the symbol dialog
        symbolDialog = SymbolDialog(self)
        results = symbolDialog.ShowModal()

        if results == wx.ID_OK:
            # x = []
            # get the selected symbol and size
            self.get_graph().set_dataSymbol(symbolDialog.get_selectedSymbol())
            self.get_graph().set_dataSymbolSize(int(symbolDialog.get_sizeChoices()[symbolDialog.get_sizeSelect().GetSelection()]))
            # clear the axes
            self.get_graph().get_axes().cla()
            # redefine the stuff for annotations
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
            # redraw the scatter plot with new symbols and size
            self.get_graph().get_axes().scatter(self.get_graph().get_xr(),
                                                self.get_graph().get_yr(),
                                                marker=self.get_graph().get_dataSymbol(),
                                                s=self.get_graph().get_dataSymbolSize(),
                                                color=self.get_graph().get_dataColor())
            self.get_graph().get_axes().plot(self.get_graph().get_x_plot(), self.get_graph().get_curve(), '-',
                                             color=self.get_graph().get_lineColor())
            # if there is a legend redraw it
            if self.get_graph().get_isLegend():
                self.get_graph().get_axes().legend(labels=self.get_graph().get_legendText(), loc=self.get_graph().get_legendLoc())
            # if self.get_annotated():
            #     for i in range(0, len(self.get_graph().get_xr())):
            #         x.append(self.get_graph().get_axes().annotate("("+str(self.get_graph().get_xr()[i]) + "," +
            #                                                        str(self.get_graph().get_yr()[i]) + ")",
            #                                                       (self.get_graph().get_xr()[i],
            #                                                        self.get_graph().get_yr()[i]), fontsize=11))
            #
            #     self.set_ann(x)
            #     self.set_annotated(True)
            # if there is a grid redraw it
            if self.get_isGrid():
                self.get_graph().get_axes().grid(True)
                self.set_isGrid(True)
            # set the labels of the graph
            self.get_graph().label(self.get_graph().get_titlelabel(),
                                   self.get_graph().get_xlabel(),
                                   self.get_graph().get_ylabel())
            self.get_graph().get_canvas().draw()
    # function to annotate the regression line
    def OnAnnotate(self, event):

        # self.get_graph().get_annot_line().xy = self.get_graph().get_line_annot_pos()
        mn = self.get_graph().get_mn()
        mx = self.get_graph().get_mx()
        y = self.get_graph().get_curve()[int(len(self.get_graph().get_curve()) / 2)]
        self.get_graph().get_annot_line().xy = [((mx - mn) / 2.0) + mn, y]
        # show the R^2 value and scale value
        text = 'R^2: ' + str(np.round_(self.get_graph().get_best_r_squared(), 3)) + '\n' + \
               'Scale: ' + str(self.get_data_scale()[self.get_graph().get_best_scale()]) + '\n' + self.get_graph().get_popt()
        self.get_graph().get_annot_line().set_text(text)
        self.get_graph().get_annot_line().set_fontsize(10)
        self.get_graph().get_annot_line().get_bbox_patch().set_alpha(0.4)
        # draw the annotation
        if self.get_graph().get_annot_line().get_visible():
            self.get_graph().get_annot_line().set_visible(False)
            self.get_graph().get_fig().canvas.draw_idle()
        else:
            self.get_graph().get_annot_line().set_visible(True)
            self.get_graph().get_fig().canvas.draw_idle()
    # function to set the graph color
    def OnGraphColor(self, event):
        # variable for the color of the line and the data points
        global customLineColor
        customLineColor = ''
        global customDataColor
        customDataColor = ''

        graphColorDialog = wx.Dialog(self, wx.ID_ANY, "Graph Color", size=(175, 200))
        graphColorPanel = wx.Panel(graphColorDialog, wx.ID_ANY)

        lineColorTxt = wx.StaticText(graphColorPanel, -1, 'Line', pos=(10, 45))
        dataColorTxt = wx.StaticText(graphColorPanel, -1, 'Data', pos=(10, 80))
        # choices for the line color and data color
        lineColor = wx.Choice(graphColorPanel, wx.ID_ANY, pos=(50, 45),
                              choices=['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'custom...'])
        dataColor = wx.Choice(graphColorPanel, wx.ID_ANY, pos=(50, 80),
                              choices=['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'custom...'])

        okbutton = wx.Button(graphColorPanel, wx.ID_OK, pos=(65, 130))
        # function to get the line color
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
        # function to get the data color
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
            # clearing the graph and redrawing it with previously selected properties.
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
    def get_data_scale(self): return self.data_scale

class HHPlot(wx.Panel):

    def __init__(self, parent):
        # gets the Panel properties
        wx.Panel.__init__(self, parent, size=wx.Size(640, 480), style=wx.SIMPLE_BORDER)

        self.figure = figure()
        # defines the plot not entirely sure what the numbers in add_subplot mean
        self.axes = self.get_fig().add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.get_fig())
        self.Fit()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.add_toolbar()
        self.SetSizer(self.sizer)
        self.Fit()

    # add toolbar to bottom of plot
    def add_toolbar(self):
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        # By adding toolbar in sizer, we are able to put it at the bottom
        # of the frame - so appearance is closer to GTK version.
        self.sizer.Add(self.toolbar, 0, wx.EXPAND)
        # update the axes menu on the toolbar
        self.toolbar.update()

    def plot(self, x, y):

        self.get_axes().scatter(x, y, marker="o", s=8)
        self.get_canvas().draw()

    def get_fig(self): return self.figure
    def get_axes(self): return self.axes
    def get_canvas(self): return self.canvas
