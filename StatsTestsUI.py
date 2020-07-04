
import wx
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx as NavigationToolbar
from matplotlib.figure import Figure
# from sympy import pretty_print as pp
from scipy import stats
from GraphDialogs import LabelDialog
from GraphDialogs import SymbolDialog
from GraphDialogs import LegendDialog

# class for the dialog that performs the F-test
class FtestDialog(wx.Dialog):
    # this is all just GUI stuff
    def __init__(self, parent, data, errtext, tree_menu, root):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "F-test", size=(840, 680))

        self.parent = parent
        self.tree_menu = tree_menu
        self.root = root

        self.panel = wx.Panel(self, wx.ID_ANY)
        self.data = data
        self.error_log = errtext

        # self.hyp_box = wx.StaticBox(self.panel, wx.ID_ANY, 'Hypotheses', pos=(20,20), size=(600, 80))
        # self.hyp0 = wx.StaticText(self.hyp_box, wx.ID_ANY, "H0: σ1^2 = σ2^2", pos=(15,25))
        # self.hyp1 = wx.StaticText(self.hyp_box, wx.ID_ANY, "H1: σ1^2 ≠ σ2^2", pos=(15, 50))
        # self.def_hyp0 = wx.StaticText(self.hyp_box, wx.ID_ANY,
        #                               "The default assumption is that the variance of group 1 = variance of group 2",
        #                               pos=(115, 25))
        # self.def_hyp1 = wx.StaticText(self.hyp_box, wx.ID_ANY,
        #                               "The default assumption is that the variance of group 1 ≠ variance of group 2",
        #                               pos=(115, 50))

        self.group_selection = GroupSelection(self.panel, self.get_data(), 110)

        # self.tails_txt = wx.StaticText(self.panel, wx.ID_ANY, 'Tails: ', pos=(15, 340))
        self.tails_choices = ['two (σ1 = σ2)', 'left (σ1 ≥ σ2)', 'right (σ1 ≤ σ2)']
        # self.tails_select = wx.Choice(self.panel, wx.ID_ANY, pos=(45, 337), choices=self.tails_choices)
        self.selectedTail = 'two (σ1 = σ2)'

        self.alpha_txt = wx.StaticText(self.panel, wx.ID_ANY, 'Alpha: ', pos=(180, 340))
        self.alpha_select = wx.TextCtrl(self.panel, wx.ID_ANY, '', pos=(220, 337), size=(50, 20))
        self.selectedAlpha = ''
        self.Bind(wx.EVT_TEXT, self.OnAlphaSelect, self.alpha_select)

        self.outlier_txt = wx.StaticText(self.panel, wx.ID_ANY, 'Max F-Val: ', pos=(320, 340))
        self.outlier_select = wx.TextCtrl(self.panel, wx.ID_ANY, '', pos=(380, 337), size=(50, 20))
        self.selectedOutlier = ''
        self.Bind(wx.EVT_TEXT, self.OnOutlierSelect, self.outlier_select)

        self.range_txt = wx.StaticText(self.panel, wx.ID_ANY, 'Scale: ', pos=(480, 340))

        self.range_choices = list(map(str, self.get_data().get_results_scale()))

        self.range_min_select = wx.Choice(self.panel, wx.ID_ANY, pos=(520, 337), choices=self.range_choices)
        self.to = wx.StaticText(self.panel, wx.ID_ANY, ' to ', pos=(635, 340))
        self.range_max_select = wx.Choice(self.panel, wx.ID_ANY, pos=(660, 337), choices=self.range_choices)

        self.range_min = ''
        self.range_max = ''

        self.results_box = wx.StaticBox(self.panel, wx.ID_ANY, 'Results', pos=(20, 375), size=(780, 200))
        self.results_txt = wx.TextCtrl(self.results_box, pos=(15,20), size=(750, 170), style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.results_txt.SetBackgroundColour('#f0f0f0')

        self.helpbutton = wx.Button(self.panel, wx.ID_HELP, pos=(20, 600))
        self.okbutton = wx.Button(self.panel, wx.ID_OK, "OK", pos=(630, 600))
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.okbutton)
        self.cancelbutton = wx.Button(self.panel, wx.ID_CANCEL, "Close", pos=(720, 600))
        self.panel.Fit()
        self.Layout()

        self.flist = []
        self.res_list = []
    # when pressing the OK button
    def OnOK(self, event):

        self.get_results_txt().Clear()
        # self.OnTypeSelect()
        # self.OnTailsSelect()
        self.OnRangeSelect()
        self.set_flist([])
        self.set_res_list([])

        d = []
        alpha = float(self.get_selectedAlpha())
        # default tails for the f-test this is a statistics thing which I figured wasnt a big deal right now
        # code is commented out but this can be selected by the user
        tails = 'two (σ1 = σ2)'
        # typ = self.get_selectedType()
        outlier = self.get_selectedOutlier()
        # the following code is to perform the F-test on every scale if there is more than one data set selected in the
        # data selection area. If there is only one in each an F-test will be performed to compare all of the relative areas
        # of the data set.
        if len(self.get_group_selection().get_group1_choices()) == 1 and len(self.get_group_selection().get_group2_choices()) == 1:

            d = self.get_f_data1()

            # print(self.get_data().get_results_scale()[self.get_data().get_results_scale().index(float(self.get_range_min())):
            #       self.get_data().get_results_scale().index(float(self.get_range_max()))+1])

            if tails == 'two (σ1 = σ2)':
                self.F_TwoTail(alpha, d, len(d))
            if tails == 'left (σ1 ≥ σ2)':
                self.F_LeftTail(alpha, d, len(d))
            if tails == 'right (σ1 ≤ σ2)':
                self.F_RightTail(alpha, d, len(d))

        elif 1 < len(self.get_group_selection().get_group1_choices()) == len(self.get_group_selection().get_group2_choices()) and \
                len(self.get_group_selection().get_group2_choices()) > 1:

            d = self.get_f_data2()

            if tails == 'two (σ1 = σ2)':
                for dset in d:
                    self.F_TwoTail(alpha, dset, len(d))

                if outlier != '':
                    for i in self.get_flist():

                        if i > float(outlier):

                            index = self.get_flist().index(i)
                            self.get_flist().insert(index, 0)
                            self.get_flist().remove(i)

                x = np.array(self.get_data().get_results_scale()[self.get_data().get_results_scale().index(float(self.get_range_min())):
                                                        self.get_data().get_results_scale().index(float(self.get_range_max()))+1])

                plot = ScatterDialog(self.get_parent(), 'Two Tail F-test Results', x,
                                     self.get_flist(), self.get_tree_menu(), self.get_root(), 'F-Value by Scale',
                                     'Scale (um^2)', 'F-Value', self.get_data(), self.get_res_list())
                plot.graphmenu.Remove(plot.annotate)
                statsmenu = plot.menuBar.FindMenu('Statistics')
                if statsmenu >= 0:
                    plot.menuBar.Remove(statsmenu)
                plot.get_graph().draw_scatter()
                self.get_tree_menu().AppendItem(self.get_root(), "Two Tail F-test Results", data=plot)
                self.get_results_txt().AppendText('See graph.')
            if tails == 'left (σ1 ≥ σ2)':
                for dset in d:
                    self.F_LeftTail(alpha, dset, len(d))

                if outlier != '':
                    for i in self.get_flist():

                        if i > float(outlier):

                            index = self.get_flist().index(i)
                            self.get_flist().insert(index, 0)
                            self.get_flist().remove(i)

                # needs log plot
                x = np.array(self.get_data().get_results_scale()[
                                    self.get_data().get_results_scale().index(float(self.get_range_min())):
                                    self.get_data().get_results_scale().index(float(self.get_range_max())) + 1])

                plot = ScatterDialog(self.get_parent(), 'Left Tail F-test Results', x,
                                     self.get_flist(), self.get_tree_menu(), self.get_root(), 'F-Value by Scale',
                                     'Scale (um^2)', 'F-Value', self.get_data(), self.get_res_list())
                plot.statsmenu.Remove(plot.confidence)
                plot.get_graph().draw_scatter()
                self.get_tree_menu().AppendItem(self.get_root(), "Left Tail F-test Results", data=plot)
                self.get_results_txt().AppendText('See graph.')
            if tails == 'right (σ1 ≤ σ2)':
                for dset in d:
                    self.F_RightTail(alpha, dset, len(d))

                if outlier != '':
                    for i in self.get_flist():

                        if i > float(outlier):

                            index = self.get_flist().index(i)
                            self.get_flist().insert(index, 0)
                            self.get_flist().remove(i)
                # needs log plot
                x = np.array(self.get_data().get_results_scale()[
                                    self.get_data().get_results_scale().index(float(self.get_range_min())):
                                    self.get_data().get_results_scale().index(float(self.get_range_max())) + 1])

                plot = ScatterDialog(self.get_parent(), 'Right Tail F-test Results', x,
                                     self.get_flist(), self.get_tree_menu(), self.get_root(), 'F-Value by Scale',
                                     'Scale (um^2)', 'F-Value', self.get_data(), self.get_res_list())
                plot.get_graph().draw_scatter()
                self.get_tree_menu().AppendItem(self.get_root(), "Right Tail F-test Results", data=plot)
                self.get_results_txt().AppendText('See graph.')
        else:

            self.get_errlog().AppendText('F-test: Groups must be the same size \n')

    # def OnTailsSelect(self):
    #     self.set_selectedTails(self.get_tails_choices()[self.get_tails_select().GetSelection()])

    # when selecting the alpha value
    def OnAlphaSelect(self, event):
        try:
            self.set_selectedAlpha(float(self.alpha_select.GetValue()))
        except ValueError as e:
            self.get_errlog().AppendText("Alpha: " + str(e) + '\n')
    # when selecting the range of scales to perform the F-test on
    def OnRangeSelect(self):
        self.set_range_min(self.get_range_choices()[self.get_range_min_select().GetSelection()])
        self.set_range_max(self.get_range_choices()[self.get_range_max_select().GetSelection()])
    # setting the outlier value
    def OnOutlierSelect(self, event):
        try:
            self.set_selectedOutlier(self.outlier_select.GetValue())
        except ValueError as e:
            self.get_errlog().AppendText("Alpha: " + str(e) + '\n')
    # this is the function that does the F-test for to compate 2 relative areas.
    def get_f_data1(self):

        f_data = []

        d1 = self.get_data().get_relative_area()[self.get_data().get_legend_txt().index(*self.get_group_selection().get_group1_choices()[0])]
        d2 = self.get_data().get_relative_area()[self.get_data().get_legend_txt().index(*self.get_group_selection().get_group2_choices()[0])]

        d1 = d1[self.get_data().get_results_scale().index(float(self.get_range_min())):
                  self.get_data().get_results_scale().index(float(self.get_range_max()))+1]
        d2 = d2[self.get_data().get_results_scale().index(float(self.get_range_min())):
                  self.get_data().get_results_scale().index(float(self.get_range_max()))+1]

        f_data.append(d1)
        f_data.append(d2)

        return f_data
    # this is the function that sets up the data to do multiscle F-test
    def get_f_data2(self):

        f_data = []

        d1 = []
        d2 = []
        # create the groups to do the F-test based on the selected data choices
        for data_set in self.get_group_selection().get_group1_choices():

            d1.append(self.get_data().get_relative_area()[self.get_data().get_legend_txt().index(*data_set)])

        for data_set in self.get_group_selection().get_group2_choices():

            d2.append(self.get_data().get_relative_area()[self.get_data().get_legend_txt().index(*data_set)])

        g1 = []
        g2 = []

        for data in zip(*d1):

            g1.append(list(data))

        for data in zip(*d2):

            g2.append(list(data))

        for d in zip(g1, g2):

            f_data.append(list(d))
        # get the groups only for the specified range
        f_data = f_data[self.get_data().get_results_scale().index(float(self.get_range_min())):
                  self.get_data().get_results_scale().index(float(self.get_range_max()))+1]

        return f_data

    def F_Tail_helper(self, alpha, data, num_data, f1, f2):
        var = []
        mean = []
        f_val = 0
        # calculate the variance and mean of all groups in the data set append to a list
        for data_set in data:
            s = np.var(data_set)
            m = np.mean(data_set)
            var.append(s)
            mean.append(m)

        if var[0] >= var[1]:

            f_val = np.round_(var[0] / var[1], 4)
        else:

            f_val = np.round_(var[1] / var[0], 4)

        self.get_flist().append(f_val)
        # for two-tailed only assume σ1 = σ2
        # range for which of the f-value is in the H0 hypothesis is accepted
        # calculate p-value
        p_val = np.round_(2.0 * stats.f.sf(f_val, len(data[0])-1, len(data[1])-1), 4)
        # calculate confidence
        p_r = np.round_((1 - alpha)*100, 4)
        # calculate variance of group
        var1 = np.round_(var[0], 4)
        var2 = np.round_(var[1], 4)
        # calculate mean of group
        mean1 = np.round_(mean[0], 4)
        mean2 = np.round_(mean[1], 4)
        # calculate standard deviation of group
        sd1 = np.round_(np.sqrt(var1), 4)
        sd2 = np.round_(np.sqrt(var2), 4)
        # ACCEPTED CASE results
        
        accepted = """
        1. Variance and mean
        Group 1                                 Group 2
        Variance: {}                            Variance: {}
        Mean: {}                                Mean: {}
        Standard Deviation: {}                  Standard Deviation: {}
        
        2. H0 hypothesis
        Since p-value > α, H0 is accepted.
        The sample standard deviation of the Group 1's population is considered to be equal to the sample
        standard deviation of the Group 2's population. So the difference between the sample standard 
        deviation of the Group 1 and Group 2 populations is not big enough to be statistically significant.

        3. P-value
        p-value equals {}. This means that if we would reject H0,
        the chance of type I error (rejecting a correct H0) would be too high: {} ({}%)
        The larger the p-value the more it supports H0

        4. The statistics
        The test statistic f equals {}, is in the {}% critical value accepted range: [{} : {}]
        """.format(var1, var2, mean1, mean2, sd1, sd2, p_val, p_val, np.round_(p_val * 100, 3), f_val, p_r, f1, f2)
        # REJECTED CASE results
        rejected = """
        1. Variance and mean
        Group 1                             Group 2
        Variance: {}                        Variance: {}
        Mean: {}                            Mean: {}
        Standard Deviation: {}              Standard Deviation: {}
        
        2. H0 hypothesis
        Since p-value < α, H0 is rejected.
        The sample standard deviation of the Group 1's population is considered to be less than the sample 
        standard deviation of the Group 2's population.
         
        3. P-value
        p-value equals {}. This means that the chance of 
        type1 error (rejecting a correct H0) is small: {} ({}%)
        The smaller the p-value the more it supports H1
         
        4. The statistics
        The test statistic f equals {}, is not in the {}% critical value accepted range: [{} : {}]
        """.format(var1, var2, mean1, mean2, sd1, sd2, p_val, p_val, np.round_(p_val * 100, 3), f_val, p_r, f1, f2)
        # check if the test should be accepted or rejected
        if f1 < f_val < f2:
            if num_data == 2:
                self.get_results_txt().AppendText(accepted)
            self.get_res_list().append(['accepted', var1, var2, mean1, mean2, sd1, sd2, p_val, p_val, np.round_(p_val * 100, 3), f_val, p_r, f1, f2])
        else:
            if num_data == 2:
                self.get_results_txt().AppendText(rejected)
            self.get_res_list().append(['rejected', var1, var2, mean1, mean2, sd1, sd2, p_val, p_val,np.round_(p_val * 100, 3), f_val, p_r, f1, f2])

    def F_TwoTail(self, alpha, data, num_data):
        self.F_Tail_helper(alpha, data, num_data,
                           np.round_(stats.f.ppf(alpha / 2.0, len(data[0])-1, len(data[1])-1), 4),
                           np.round_(stats.f.ppf(1.0 - (alpha / 2.0), len(data[0])-1, len(data[1])-1), 4))

    def F_LeftTail(self, alpha, data, num_data):
        self.F_Tail_helper(alpha, data, num_data,
                           np.round_(stats.f.ppf(alpha, len(data[0])-1, len(data[1])-1), 4), '∞')

    def F_RightTail(self, alpha, data, num_data):
        self.F_Tail_helper(alpha, data, num_data,
                           np.round_(stats.f.ppf(1 - alpha, len(data[0])-1, len(data[1])-1), 4), '-∞')

    def get_panel(self): return self.panel
    def get_data(self): return self.data
    def get_errlog(self): return self.error_log
    def get_group_selection(self): return self.group_selection

    def get_selectedTails(self): return self.selectedTail
    def set_selectedTails(self, tail): self.selectedTail = tail
    def get_selectedAlpha(self): return self.selectedAlpha
    def set_selectedAlpha(self, alpha): self.selectedAlpha = alpha
    # def get_selectedType(self): return self.selectedType
    # def set_selectedType(self, typ): self.selectedType = typ
    def get_selectedOutlier(self): return self.selectedOutlier
    def set_selectedOutlier(self, maxf): self.selectedOutlier = maxf

    def get_range_min(self): return self.range_min
    def set_range_min(self, rmin): self.range_min = rmin
    def get_range_max(self): return self.range_max
    def set_range_max(self, rmax): self.range_max = rmax
    def get_range_choices(self): return self.range_choices
    def get_range_min_select(self): return self.range_min_select
    def get_range_max_select(self): return self.range_max_select
    # def get_type_select(self): return self.type_select
    # def get_type_choices(self): return self.type_choices

    # def get_tails_select(self): return self.tails_select
    def get_tails_choices(self): return self.tails_choices

    def get_results_txt(self): return self.results_txt
    def get_flist(self): return self.flist
    def set_flist(self, flist): self.flist = flist
    def get_parent(self): return self.parent
    def get_tree_menu(self): return self.tree_menu
    def get_root(self): return self.root
    def get_res_list(self): return self.res_list
    def set_res_list(self, lst): self.res_list = lst
# class for the dialog that performs the Welch's t-test
class TtestDialog(wx.Dialog):
    # again more GUI stuff for the dialog
    def __init__(self, parent, data, errtext, tree_menu, root):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "T-test", size=(840, 680))

        self.parent = parent
        self.tree_menu = tree_menu
        self.root = root

        self.panel = wx.Panel(self, wx.ID_ANY)
        self.data = data
        self.error_log = errtext

        self.group_selection = GroupSelection(self.panel, self.data, 110)

        # self.tails_txt = wx.StaticText(self.panel, wx.ID_ANY, 'Tails: ', pos=(15, 340))
        # self.tails_choices = ['two (σ1 = σ2)', 'left (σ1 ≥ σ2)', 'right (σ1 ≤ σ2)']
        # self.tails_select = wx.Choice(self.panel, wx.ID_ANY, pos=(45, 337), choices=self.tails_choices)
        # self.selectedTail = ''

        self.alpha_txt = wx.StaticText(self.panel, wx.ID_ANY, 'Alpha: ', pos=(200, 340))
        self.alpha_select = wx.TextCtrl(self.panel, wx.ID_ANY, '', pos=(240, 337), size=(50, 20))
        self.selectedAlpha = ''
        self.Bind(wx.EVT_TEXT, self.OnAlphaSelect, self.alpha_select)

        self.range_txt = wx.StaticText(self.panel, wx.ID_ANY, 'Scale: ', pos=(480, 340))

        self.range_choices = list(map(str, self.get_data().get_results_scale()))

        self.range_min_select = wx.Choice(self.panel, wx.ID_ANY, pos=(520, 337), choices=self.range_choices)
        self.to = wx.StaticText(self.panel, wx.ID_ANY, ' to ', pos=(635, 340))
        self.range_max_select = wx.Choice(self.panel, wx.ID_ANY, pos=(660, 337), choices=self.range_choices)

        self.range_min = ''
        self.range_max = ''

        self.results_box = wx.StaticBox(self.panel, wx.ID_ANY, 'Results', pos=(20, 375), size=(780, 200))
        self.results_txt = wx.TextCtrl(self.results_box, pos=(15, 20), size=(750, 170),
                                       style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.results_txt.SetBackgroundColour('#f0f0f0')

        self.helpbutton = wx.Button(self.panel, wx.ID_HELP, pos=(20, 600))
        self.okbutton = wx.Button(self.panel, wx.ID_OK, "OK", pos=(630, 600))
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.okbutton)
        self.cancelbutton = wx.Button(self.panel, wx.ID_CANCEL, "Close", pos=(720, 600))
        self.panel.Fit()
        self.Layout()

        self.tlist = []
        self.res_list = []

    # need to use own math and also calculate p-value myself if I want user to be able to input a 'd' value
    # built in functions assume the expected difference between the averages = d is 0. If this is ok I can use built in
    # functions really easily.

    # functions here are identical to the ones described in the F-test dialog but with T-test statistics
    def OnOK(self, event):

        self.get_results_txt().Clear()
        # self.OnTypeSelect()
        # self.OnTailsSelect()
        self.OnRangeSelect()
        self.set_tlist([])
        self.set_res_list([])

        d = []
        alpha = float(self.get_selectedAlpha())
        # tails = self.get_selectedTails()
        # typ = self.get_selectedType()
        outlier = '' # self.get_selectedOutlier()

        if len(self.get_group_selection().get_group1_choices()) == 1 and len(self.get_group_selection().get_group2_choices()) == 1:

            d = self.get_f_data1()

            # print(self.get_data().get_results_scale()[self.get_data().get_results_scale().index(float(self.get_range_min())):
            #       self.get_data().get_results_scale().index(float(self.get_range_max()))+1])

            # if tails == 'two (σ1 = σ2)':
            #     self.WelchsTTest(alpha, d, len(d))
            # if tails == 'left (σ1 ≥ σ2)':
            #     self.WelchsTTest(alpha, d, len(d))
            # if tails == 'right (σ1 ≤ σ2)':
            #     self.WelchsTTest(alpha, d, len(d))
            self.WelchsTTest(alpha, d, len(d))

        elif 1 < len(self.get_group_selection().get_group1_choices()) == len(self.get_group_selection().get_group2_choices()) and \
                len(self.get_group_selection().get_group2_choices()) > 1:

            d = self.get_f_data2()

            for dset in d:
                self.WelchsTTest(alpha, dset, len(d))

            if outlier != '':
                for i in self.get_tlist():

                    if i > float(outlier):

                        index = self.get_tlist().index(i)
                        self.get_tlist().insert(index, 0)
                        self.get_tlist().remove(i)
            # needs log plot
            x = np.array(self.get_data().get_results_scale()[self.get_data().get_results_scale().index(float(self.get_range_min())):
                                                    self.get_data().get_results_scale().index(float(self.get_range_max()))+1])

            plot = ScatterDialog(self.get_parent(), "Welch\'s T-test Results", x,
                                 self.get_tlist(), self.get_tree_menu(), self.get_root(), 'T-Value by Scale',
                                 'Scale (um^2)', 'T-Value', self.get_data(), self.get_res_list())
            plot.graphmenu.Remove(plot.annotate)
            statsmenu = plot.menuBar.FindMenu('Statistics')
            if statsmenu >= 0:
                plot.menuBar.Remove(statsmenu)
            plot.get_graph().draw_scatter()
            self.get_tree_menu().AppendItem(self.get_root(), "Welch\'s T-test Results", data=plot)

            self.get_results_txt().AppendText('See graph.')

            # if tails == 'two (σ1 = σ2)':
            #     for dset in d:
            #         self.WelchsTTest(alpha, dset, len(d))
            #
            #     if outlier != '':
            #         for i in self.get_tlist():
            #
            #             if i > float(outlier):
            #
            #                 index = self.get_tlist().index(i)
            #                 self.get_tlist().insert(index, 0)
            #                 self.get_tlist().remove(i)
            #     # needs log plot
            #     x = np.array(self.get_data().get_results_scale()[self.get_data().get_results_scale().index(float(self.get_range_min())):
            #                                             self.get_data().get_results_scale().index(float(self.get_range_max()))+1])
            #
            #     plot = ScatterDialog(self.get_parent(), 'Two Tail T-test Results', x,
            #                          self.get_tlist(), self.get_tree_menu(), self.get_root(), 'T-Value by Scale',
            #                          'Scale (um^2)', 'T-Value', self.get_data(), self.get_res_list())
            #     plot.statsmenu.Remove(plot.confidence)
            #     plot.get_graph().draw_scatter()
            #     self.get_tree_menu().AppendItem(self.get_root(), "Two Tail T-test Results", data=plot)
            # if tails == 'left (σ1 ≥ σ2)':
            #     for dset in d:
            #         self.WelchsTTest(alpha, dset, len(d))
            #
            #     if outlier != '':
            #         for i in self.get_tlist():
            #
            #             if i > float(outlier):
            #                 # instead of setting outliers to 0 should just remove all together
            #                 index = self.get_tlist().index(i)
            #                 self.get_tlist().insert(index, 0)
            #                 self.get_tlist().remove(i)
            #
            #     # needs log plot
            #     x = np.array(self.get_data().get_results_scale()[
            #                         self.get_data().get_results_scale().index(float(self.get_range_min())):
            #                         self.get_data().get_results_scale().index(float(self.get_range_max())) + 1])
            #
            #     plot = ScatterDialog(self.get_parent(), 'Left Tail T-test Results', x,
            #                          self.get_tlist(), self.get_tree_menu(), self.get_root(), 'T-Value by Scale',
            #                          'Scale (um^2)', 'T-Value', self.get_data(), self.get_res_list())
            #     plot.statsmenu.Remove(plot.confidence)
            #     plot.get_graph().draw_scatter()
            #     self.get_tree_menu().AppendItem(self.get_root(), "Left Tail T-test Results", data=plot)
            # if tails == 'right (σ1 ≤ σ2)':
            #     for dset in d:
            #         self.WelchsTTest(alpha, dset, len(d))
            #
            #     if outlier != '':
            #         for i in self.get_tlist():
            #
            #             if i > float(outlier):
            #
            #                 index = self.get_tlist().index(i)
            #                 self.get_tlist().insert(index, 0)
            #                 self.get_tlist().remove(i)
            #     # needs log plot
            #     x = np.array(self.get_data().get_results_scale()[
            #                         self.get_data().get_results_scale().index(float(self.get_range_min())):
            #                         self.get_data().get_results_scale().index(float(self.get_range_max())) + 1])
            #
            #     plot = ScatterDialog(self.get_parent(), 'Right Tail T-test Results', x,
            #                          self.get_tlist(), self.get_tree_menu(), self.get_root(), 'T-Value by Scale',
            #                          'Scale (um^2)', 'T-Value', self.get_data(), self.get_res_list())
            #     plot.statsmenu.Remove(plot.confidence)
            #     plot.get_graph().draw_scatter()
            #     self.get_tree_menu().AppendItem(self.get_root(), "Right Tail T-test Results", data=plot)
            # somethings wrong with this and the picker....
            # print(self.get_res_list())
        else:

            self.get_errlog().AppendText('T-test: Groups must be the same size \n')

    # def OnTailsSelect(self):
    #     self.set_selectedTails(self.get_tails_choices()[self.get_tails_select().GetSelection()])
    # def OnTypeSelect(self):
    #     self.set_selectedType(self.get_type_choices()[self.get_type_select().GetSelection()])
    def OnRangeSelect(self):
        self.set_range_min(self.get_range_choices()[self.get_range_min_select().GetSelection()])
        self.set_range_max(self.get_range_choices()[self.get_range_max_select().GetSelection()])
    def OnAlphaSelect(self, event):
        try:
            self.set_selectedAlpha(float(self.alpha_select.GetValue()))
        except ValueError as e:
            self.get_errlog().AppendText("Alpha: " + str(e) + '\n')

    def get_f_data1(self):

        f_data = []

        d1 = self.get_data().get_relative_area()[self.get_data().get_legend_txt().index(*self.get_group_selection().get_group1_choices()[0])]
        d2 = self.get_data().get_relative_area()[self.get_data().get_legend_txt().index(*self.get_group_selection().get_group2_choices()[0])]

        d1 = d1[self.get_data().get_results_scale().index(float(self.get_range_min())):
                  self.get_data().get_results_scale().index(float(self.get_range_max()))+1]
        d2 = d2[self.get_data().get_results_scale().index(float(self.get_range_min())):
                  self.get_data().get_results_scale().index(float(self.get_range_max()))+1]

        f_data.append(d1)
        f_data.append(d2)

        return f_data

    def get_f_data2(self):

        f_data = []

        d1 = []
        d2 = []

        for data_set in self.get_group_selection().get_group1_choices():

            d1.append(self.get_data().get_relative_area()[self.get_data().get_legend_txt().index(*data_set)])

        for data_set in self.get_group_selection().get_group2_choices():

            d2.append(self.get_data().get_relative_area()[self.get_data().get_legend_txt().index(*data_set)])

        g1 = []
        g2 = []

        for data in zip(*d1):

            g1.append(list(data))

        for data in zip(*d2):

            g2.append(list(data))

        for d in zip(g1, g2):

            f_data.append(list(d))

        f_data = f_data[self.get_data().get_results_scale().index(float(self.get_range_min())):
                  self.get_data().get_results_scale().index(float(self.get_range_max()))+1]

        return f_data

    # Two sample T-Test (Welch's T-test) not equal standard deviation between groups
    def WelchsTTest(self, a, data, num_data):

        sets = []
        diff = []
        N = 0

        alpha = a
        num = num_data

        for data_set in data:
            sets.append(data_set)
            # print(data_set)

        # print(sets)
        diff = np.array(sets[0]) - np.array(sets[1])
        N = len(diff)

        d = 0.0
        t_score = np.round_((np.average(sets[0]) - np.average(sets[1]) - d) / np.sqrt(
            (np.var(sets[0]) / len(sets[0])) + (np.var(sets[1]) / len(sets[1]))), 5)

        self.get_tlist().append(np.round_(t_score, 5))

        avg1 = np.round_(np.average(sets[0]), 5)
        avg2 = np.round_(np.average(sets[1]), 5)

        var1 = np.round_(np.var(sets[0]), 5)
        var2 = np.round_(np.var(sets[1]), 5)

        std1 = np.round_(np.sqrt(np.var(sets[0])), 5)
        std2 = np.round_(np.sqrt(np.var(sets[1])), 5)

        pval = np.round_(stats.t.sf(np.abs(t_score), N - 1) * 2, 5)

        Lpval = np.round_(stats.t.sf(np.abs(t_score), N - 1), 5)

        Rpval = np.round_(1 - stats.t.sf(np.abs(t_score), N - 1), 5)

        confidence = np.round_((1-alpha)*100, 2)

        results_text = """
        Welch's T-Test Results
        
        Groups Size: {}
        
        1. Variance and Mean
        Group 1                             Group 2
        Variance: {}                        Variance: {}
        Average: {}                         Average: {}
        Standard Deviation: {}              Standard Deviation: {}
        
        2. Statistics 
        T-Score: {}
        Left-Tailed P-Value: {}
        Right-Tailed P-Value: {}
        Two-Tailed P-Value: {}
        Confidence: {}%""".format(N, var1, var2, avg1, avg2, std1, std2, t_score, Lpval, Rpval, pval, confidence)

        if num_data == 2:
            self.get_results_txt().AppendText(results_text)

        self.get_res_list().append([var1, var2, avg1, avg2, std1, std2, t_score, pval, Lpval, Rpval, confidence])

    def get_data(self): return self.data
    def get_errlog(self): return self.error_log
    def get_group_selection(self): return self.group_selection

    # def get_selectedTails(self): return self.selectedTail
    # def set_selectedTails(self, tail): self.selectedTail = tail
    def get_selectedAlpha(self): return self.selectedAlpha
    def set_selectedAlpha(self, alpha): self.selectedAlpha = alpha
    # def get_selectedType(self): return self.selectedType
    # def set_selectedType(self, typ): self.selectedType = typ

    # def get_type_select(self): return self.type_select
    # def get_type_choices(self): return self.type_choices

    # def get_tails_select(self): return self.tails_select
    # def get_tails_choices(self): return self.tails_choices

    def get_range_min(self): return self.range_min
    def set_range_min(self, rmin): self.range_min = rmin
    def get_range_max(self): return self.range_max
    def set_range_max(self, rmax): self.range_max = rmax
    def get_range_choices(self): return self.range_choices
    def get_range_min_select(self): return self.range_min_select
    def get_range_max_select(self): return self.range_max_select

    def get_results_txt(self): return self.results_txt
    def get_tlist(self): return self.tlist
    def set_tlist(self, tlist): self.tlist = tlist
    def get_parent(self): return self.parent
    def get_tree_menu(self): return self.tree_menu
    def get_root(self): return self.root
    def get_res_list(self): return self.res_list
    def set_res_list(self, lst): self.res_list = lst
# class for the dialog that performs the ANOVA test
# functions same as in the above 2 classes.
class ANOVAtestDialog(wx.Dialog):

    def __init__(self, parent, data, errtext, tree_menu, root):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "ANOVA", size=(840, 680))

        self.parent = parent
        self.tree_menu = tree_menu
        self.root = root

        self.panel = wx.Panel(self, wx.ID_ANY)
        self.data = data
        self.error_log = errtext

        # self.hyp_box = wx.StaticBox(self.panel, wx.ID_ANY, 'Hypotheses', pos=(20, 20), size=(600, 80))
        # self.hyp0 = wx.StaticText(self.hyp_box, wx.ID_ANY, "H0: σ1^2 = σ2^2", pos=(15, 25))
        # self.hyp1 = wx.StaticText(self.hyp_box, wx.ID_ANY, "H1: σ1^2 ≠ σ2^2", pos=(15, 50))
        # self.def_hyp0 = wx.StaticText(self.hyp_box, wx.ID_ANY,
        #                               "The default assumption is that the variance of group 1 = variance of group 2",
        #                               pos=(115, 25))
        # self.def_hyp1 = wx.StaticText(self.hyp_box, wx.ID_ANY,
        #                               "The default assumption is that the variance of group 1 ≠ variance of group 2",
        #                               pos=(115, 50))

        self.group_selection = GroupSelection(self.panel, self.get_data(), 110)

        # self.tails_txt = wx.StaticText(self.panel, wx.ID_ANY, 'Tails: ', pos=(15, 340))
        # self.tails_choices = ['two (σ1 = σ2)', 'left (σ1 ≥ σ2)', 'right (σ1 ≤ σ2)']
        # self.tails_select = wx.Choice(self.panel, wx.ID_ANY, pos=(45, 337), choices=self.tails_choices)
        # self.selectedTail = ''

        self.alpha_txt = wx.StaticText(self.panel, wx.ID_ANY, 'Alpha: ', pos=(30, 340))
        self.alpha_select = wx.TextCtrl(self.panel, wx.ID_ANY, '', pos=(70, 337), size=(50, 20))
        self.selectedAlpha = ''
        self.Bind(wx.EVT_TEXT, self.OnAlphaSelect, self.alpha_select)

        self.range_txt = wx.StaticText(self.panel, wx.ID_ANY, 'Scale: ', pos=(180, 340))

        self.range_choices = list(map(str, self.get_data().get_results_scale()))

        self.range_min_select = wx.Choice(self.panel, wx.ID_ANY, pos=(220, 337), choices=self.range_choices)
        self.to = wx.StaticText(self.panel, wx.ID_ANY, ' to ', pos=(335, 340))
        self.range_max_select = wx.Choice(self.panel, wx.ID_ANY, pos=(360, 337), choices=self.range_choices)

        self.range_min = ''
        self.range_max = ''

        self.results_box = wx.StaticBox(self.panel, wx.ID_ANY, 'Results', pos=(20, 375), size=(780, 200))
        self.results_txt = wx.TextCtrl(self.results_box, pos=(15, 20), size=(750, 170),
                                       style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.results_txt.SetBackgroundColour('#f0f0f0')

        # self.outlier_txt = wx.StaticText(self.panel, wx.ID_ANY, 'Max F-Val: ', pos=(650, 25))
        # self.outlier_select = wx.TextCtrl(self.panel, wx.ID_ANY, '', pos=(720, 25), size=(50, 20))
        # self.selectedOutlier = ''
        # self.Bind(wx.EVT_TEXT, self.OnOutlierSelect, self.outlier_select)

        self.helpbutton = wx.Button(self.panel, wx.ID_HELP, pos=(20, 600))
        self.okbutton = wx.Button(self.panel, wx.ID_OK, "OK", pos=(630, 600))
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.okbutton)
        self.cancelbutton = wx.Button(self.panel, wx.ID_CANCEL, "Close", pos=(720, 600))
        self.panel.Fit()
        self.Layout()

        self.flist = []
        self.res_list = []

    def OnOK(self, event):

        self.get_results_txt().Clear()
        # self.OnTypeSelect()
        # self.OnTailsSelect()
        self.OnRangeSelect()
        self.set_flist([])
        self.set_res_list([])

        d = []
        alpha = float(self.get_selectedAlpha())
        # tails = self.get_selectedTails()
        # typ = self.get_selectedType()
        # outlier = self.get_selectedOutlier()

        if len(self.get_group_selection().get_group1_choices()) == 1 and len(self.get_group_selection().get_group2_choices()) == 1:

            d = self.get_f_data1()
            self.F_anova(alpha, d, len(d))

        elif 1 < len(self.get_group_selection().get_group1_choices()) == len(self.get_group_selection().get_group2_choices()) and \
                len(self.get_group_selection().get_group2_choices()) > 1:

            d = self.get_f_data2()

            # find degrees of freedom
            n = len(d[0][0])
            N = len(d[0]) * n
            c = len(d[0])
            dfn = c - 1
            dfd = (N - 1) - (c - 1)
            # min msr plot line
            MSR_min = np.round_(stats.f.ppf(1 - alpha, dfn, dfd), 5)

            for dset in d:
                self.F_anova(alpha, dset, len(d))

            # if outlier != '':
            #     for i in self.get_flist():
            #
            #         if i > float(outlier):
            #             index = self.get_flist().index(i)
            #             self.get_flist().insert(index, 0)
            #             self.get_flist().remove(i)

            x = self.get_data().get_results_scale()[
                                self.get_data().get_results_scale().index(float(self.get_range_min())):
                                self.get_data().get_results_scale().index(float(self.get_range_max())) + 1]
            # needs log plot
            xlog = np.array(self.get_data().get_results_scale()[
                                self.get_data().get_results_scale().index(float(self.get_range_min())):
                                self.get_data().get_results_scale().index(float(self.get_range_max())) + 1])

            plot = ScatterDialog(self.get_parent(), 'ANOVA Results', xlog,
                                 self.get_flist(), self.get_tree_menu(), self.get_root(), 'MSR by Scale',
                                 'Scale (um^2)', 'MSR', self.get_data(), self.get_res_list())
            plot.get_graph().set_min_msr(MSR_min)
            plot.get_graph().draw_scatter()
            plot.get_graph().draw_line(x, MSR_min)
            plot.get_graph().set_df1(dfn)
            plot.get_graph().set_df2(dfd)
            plot.get_graph().set_alpha(1-alpha)
            self.get_tree_menu().AppendItem(self.get_root(), "Two Tail ANOVA test Results", data=plot)

            self.get_results_txt().AppendText('See graph.')

        else:

            self.get_errlog().AppendText('Anova: Groups must be the same size \n')

    # def OnTailsSelect(self):
    #     self.set_selectedTails(self.get_tails_choices()[self.get_tails_select().GetSelection()])

    # def OnTypeSelect(self):
    #     self.set_selectedType(self.get_type_choices()[self.get_type_select().GetSelection()])

    def OnAlphaSelect(self, event):
        try:
            self.set_selectedAlpha(float(self.alpha_select.GetValue()))
        except ValueError as e:
            self.get_errlog().AppendText("Alpha: " + str(e) + '\n')

    def OnRangeSelect(self):
        self.set_range_min(self.get_range_choices()[self.get_range_min_select().GetSelection()])
        self.set_range_max(self.get_range_choices()[self.get_range_max_select().GetSelection()])

    # def OnOutlierSelect(self, event):
    #     try:
    #         self.set_selectedOutlier(self.outlier_select.GetValue())
    #     except ValueError as e:
    #         self.get_errlog().AppendText("Alpha: " + str(e) + '\n')

    def get_f_data1(self):

        f_data = []

        d1 = self.get_data().get_relative_area()[
            self.get_data().get_legend_txt().index(*self.get_group_selection().get_group1_choices()[0])]
        d2 = self.get_data().get_relative_area()[
            self.get_data().get_legend_txt().index(*self.get_group_selection().get_group2_choices()[0])]

        d1 = d1[self.get_data().get_results_scale().index(float(self.get_range_min())):
                self.get_data().get_results_scale().index(float(self.get_range_max())) + 1]
        d2 = d2[self.get_data().get_results_scale().index(float(self.get_range_min())):
                self.get_data().get_results_scale().index(float(self.get_range_max())) + 1]

        f_data.append(d1)
        f_data.append(d2)

        return f_data

    def get_f_data2(self):

        f_data = []

        d1 = []
        d2 = []

        for data_set in self.get_group_selection().get_group1_choices():
            d1.append(self.get_data().get_relative_area()[self.get_data().get_legend_txt().index(*data_set)])

        for data_set in self.get_group_selection().get_group2_choices():
            d2.append(self.get_data().get_relative_area()[self.get_data().get_legend_txt().index(*data_set)])

        g1 = []
        g2 = []

        for data in zip(*d1):
            g1.append(list(data))

        for data in zip(*d2):
            g2.append(list(data))

        for d in zip(g1, g2):
            f_data.append(list(d))

        f_data = f_data[self.get_data().get_results_scale().index(float(self.get_range_min())):
                        self.get_data().get_results_scale().index(float(self.get_range_max())) + 1]

        return f_data

    def F_anova(self, alpha, data, num_data):

        # all sets of data must be of equal size

        MSc = 0
        MSresid = 0
        MSR = 0
        SSc = 0
        SStot = 0
        SSresid = 0
        n = len(data[0])
        N = len(data) * n
        c = len(data)
        dfn = c - 1
        dfd = (N - 1) - (c - 1)

        Tc = []

        all_data = []

        for data_set in data:

            Tc.append(sum(data_set))
            for val in data_set:

                all_data.append(val)


        SSc = (np.sum(np.square(Tc)) / n) - (np.square(np.sum(Tc)) / N)
        SStot = np.sum(np.square(all_data)) - (np.square(np.sum(Tc)) / N)
        SSresid = SStot - SSc

        MSc = SSc / dfn
        MSresid = SSresid / dfd
        MSR = np.round_(MSc / MSresid, 5)

        MSR_min = np.round_(stats.f.ppf(1 - alpha, dfn, dfd), 5)

        res_txt = """
        Mean Square Ratio (MSR): {}
        Minimum MSR: {}
        Confidence: {}
        Degrees of Freedom (Numerator, Denominator): {}, {}
        """.format(MSR, MSR_min, (1-alpha)*100, dfn, dfd)

        # print(num_data)
        self.get_res_list().append([MSR, MSR_min, (1-alpha)*100, dfn, dfd])

        if num_data == 2:
            self.get_results_txt().AppendText(res_txt)

        self.get_flist().append(MSR)

    def get_panel(self): return self.panel
    def get_data(self): return self.data
    def get_errlog(self): return self.error_log
    def get_group_selection(self): return self.group_selection

    # def get_selectedTails(self): return self.selectedTail
    # def set_selectedTails(self, tail): self.selectedTail = tail
    def get_selectedAlpha(self): return self.selectedAlpha
    def set_selectedAlpha(self, alpha): self.selectedAlpha = alpha
    # def get_selectedType(self): return self.selectedType
    # def set_selectedType(self, typ): self.selectedType = typ
    # def get_selectedOutlier(self): return self.selectedOutlier
    # def set_selectedOutlier(self, maxf): self.selectedOutlier = maxf

    def get_range_min(self): return self.range_min
    def set_range_min(self, rmin): self.range_min = rmin
    def get_range_max(self): return self.range_max
    def set_range_max(self, rmax): self.range_max = rmax
    def get_range_choices(self): return self.range_choices
    def get_range_min_select(self): return self.range_min_select
    def get_range_max_select(self): return self.range_max_select

    # def get_type_select(self): return self.type_select
    # def get_type_choices(self): return self.type_choices
    # def get_tails_select(self): return self.tails_select
    # def get_tails_choices(self): return self.tails_choices

    def get_results_txt(self): return self.results_txt
    def get_flist(self): return self.flist
    def set_flist(self, flist): self.flist = flist

    def get_parent(self): return self.parent
    def get_tree_menu(self): return self.tree_menu
    def get_root(self): return self.root
    def get_res_list(self): return self.res_list
    def set_res_list(self, l): self.res_list = l

# ---------- Group Selection Object ---------------
# future: make static box names variables, add x-pos, only have one data/group pair so just make 2 objects to make the double one
# this is the class for the group data selection in the above 3 class dialogs
class GroupSelection:
    # more GUI stuff
    def __init__(self, panel, data, y):

        self.panel = panel
        self.data = data
        # group 1
        self.data_box1 = wx.StaticBox(self.panel, wx.ID_ANY, 'Data', pos=(20, y), size=(150, 200))
        self.data_selection1 = wx.ListCtrl(self.data_box1, id=wx.ID_ANY, size=(130, 175), style=wx.LC_REPORT |
                                                                                                wx.LC_NO_HEADER |
                                                                                                wx.NO_BORDER,
                                           pos=(10, 20))
        self.data_selection1.SetBackgroundColour('#f0f0f0')
        self.data_selection1.InsertColumn(0, "0", width=130)
        self.data_choices1 = []
        [self.data_choices1.append([data_set]) for data_set in self.get_data().get_legend_txt()]
        [self.data_selection1.Append(item) for item in self.get_data_choices1()]

        self.group1_box = wx.StaticBox(self.panel, wx.ID_ANY, 'Group 1', pos=(230, y), size=(150, 200))
        self.group1_selection = wx.ListCtrl(self.group1_box, wx.ID_ANY, size=(130, 175), style=wx.LC_REPORT |
                                                                                               wx.LC_NO_HEADER |
                                                                                               wx.NO_BORDER,
                                            pos=(10, 20))
        self.group1_selection.SetBackgroundColour('#f0f0f0')
        self.group1_selection.InsertColumn(0, "0", width=130)
        self.group1_choices = []

        self.data_selection1.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect1, self.data_selection1)
        self.data_selection1.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnDeselect1, self.data_selection1)
        self.group1_selection.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect1, self.group1_selection)
        self.group1_selection.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnDeselect1, self.group1_selection)

        self.toGroup1btn = wx.Button(self.panel, wx.ID_ANY, '>>>', pos=(180, y + 65), size=(40, 20))
        self.fromGroup1btn = wx.Button(self.panel, wx.ID_ANY, '<<<', pos=(180, y + 95), size=(40, 20))

        self.selectedList1 = []

        self.toGroup1btn.Bind(wx.EVT_BUTTON, self.OnToGroup1, self.toGroup1btn)
        self.fromGroup1btn.Bind(wx.EVT_BUTTON, self.OnFromGroup1, self.fromGroup1btn)
        # group 2
        self.data_box2 = wx.StaticBox(self.panel, wx.ID_ANY, 'Data', pos=(420, y), size=(150, 200))
        self.data_selection2 = wx.ListCtrl(self.data_box2, id=wx.ID_ANY, size=(130, 175), style=wx.LC_REPORT |
                                                                                                wx.LC_NO_HEADER |
                                                                                                wx.NO_BORDER,
                                           pos=(10, 20))
        self.data_selection2.SetBackgroundColour('#f0f0f0')
        self.data_selection2.InsertColumn(0, "0", width=130)
        self.data_choices2 = []
        [self.data_choices2.append([data_set]) for data_set in self.get_data().get_legend_txt()]
        [self.data_selection2.Append(item) for item in self.get_data_choices2()]

        self.group2_box = wx.StaticBox(self.panel, wx.ID_ANY, 'Group 2', pos=(630, y), size=(150, 200))
        self.group2_selection = wx.ListCtrl(self.group2_box, wx.ID_ANY, size=(130, 175), style=wx.LC_REPORT |
                                                                                               wx.LC_NO_HEADER |
                                                                                               wx.NO_BORDER,
                                            pos=(10, 20))
        self.group2_selection.SetBackgroundColour('#f0f0f0')
        self.group2_selection.InsertColumn(0, "0", width=130)
        self.group2_choices = []

        self.data_selection2.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect2, self.data_selection2)
        self.data_selection2.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnDeselect2, self.data_selection2)
        self.group2_selection.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect2, self.group2_selection)
        self.group2_selection.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnDeselect2, self.group2_selection)

        self.toGroup2btn = wx.Button(self.panel, wx.ID_ANY, '>>>', pos=(580, y + 65), size=(40, 20))
        self.fromGroup2btn = wx.Button(self.panel, wx.ID_ANY, '<<<', pos=(580, y + 95), size=(40, 20))

        self.selectedList2 = []

        self.toGroup2btn.Bind(wx.EVT_BUTTON, self.OnToGroup2, self.toGroup2btn)
        self.fromGroup2btn.Bind(wx.EVT_BUTTON, self.OnFromGroup2, self.fromGroup2btn)
    # functions to select and deselect the data sets
    # functions to move the data to and form the groups by pressing buttons
    def OnSelect1(self, event):
        info = [event.GetText()]
        if not self.get_selectedList1().__contains__(info):
            self.get_selectedList1().append(info)
    def OnDeselect1(self, event):
        info = [event.GetText()]
        if self.get_selectedList1().__contains__(info):
            self.get_selectedList1().remove(info)
    def OnToGroup1(self, event):
        for selected in self.get_selectedList1():
            if not self.get_group1_choices().__contains__(selected):
                self.get_group1_choices().append(selected)
                self.get_data_choices1().remove(selected)
        self.set_selectedList1([])
        self.UpdateSelection1()
    def OnFromGroup1(self, event):
        for selected in self.get_selectedList1():
            if not self.get_data_choices1().__contains__(selected):
                self.get_data_choices1().append(selected)
                self.get_group1_choices().remove(selected)
        self.set_selectedList1([])
        self.UpdateSelection1()
    # updates the groups
    def UpdateSelection1(self):
        self.get_data_selection1().ClearAll()
        self.get_group1_selection().ClearAll()
        self.get_data_selection1().InsertColumn(0, "0", width=130)
        self.get_group1_selection().InsertColumn(0, "0", width=130)
        [self.get_data_selection1().Append(item) for item in self.get_data_choices1()]
        [self.get_group1_selection().Append(item) for item in self.get_group1_choices()]

    # functions to select and deselect the data sets
    # functions to move the data to and form the groups by pressing buttons
    def OnSelect2(self, event):
        info = [event.GetText()]
        if not self.get_selectedList2().__contains__(info):
            self.get_selectedList2().append(info)
    def OnDeselect2(self, event):
        info = [event.GetText()]
        if self.get_selectedList2().__contains__(info):
            self.get_selectedList2().remove(info)
    def OnToGroup2(self, event):
        for selected in self.get_selectedList2():
            if not self.get_group2_choices().__contains__(selected):
                self.get_group2_choices().append(selected)
                self.get_data_choices2().remove(selected)
        self.set_selectedList2([])
        self.UpdateSelection2()
    def OnFromGroup2(self, event):
        for selected in self.get_selectedList2():
            if not self.get_data_choices2().__contains__(selected):
                self.get_data_choices2().append(selected)
                self.get_group2_choices().remove(selected)
        self.set_selectedList2([])
        self.UpdateSelection2()
    # updates the groups
    def UpdateSelection2(self):
        self.get_data_selection2().ClearAll()
        self.get_group2_selection().ClearAll()
        self.get_data_selection2().InsertColumn(0, "0", width=130)
        self.get_group2_selection().InsertColumn(0, "0", width=130)
        [self.get_data_selection2().Append(item) for item in self.get_data_choices2()]
        [self.get_group2_selection().Append(item) for item in self.get_group2_choices()]

    def get_panel(self): return self.panel
    def get_data(self): return self.data

    def get_data_choices1(self): return self.data_choices1
    def set_data_choices1(self, choices): self.data_choices1 = choices
    def get_group1_choices(self): return self.group1_choices
    def set_group1_choices(self, choices): self.group1_choices = choices
    def get_data_selection1(self): return self.data_selection1
    def get_group1_selection(self): return self.group1_selection
    def get_selectedList1(self): return self.selectedList1
    def set_selectedList1(self, slist): self.selectedList1 = slist

    def get_data_choices2(self): return self.data_choices2
    def set_data_choices2(self, choices): self.data_choices2 = choices
    def get_group2_choices(self): return self.group2_choices
    def set_group2_choices(self, choices): self.group2_choices = choices
    def get_data_selection2(self): return self.data_selection2
    def get_group2_selection(self): return self.group2_selection
    def get_selectedList2(self): return self.selectedList2
    def set_selectedList2(self, slist): self.selectedList2 = slist

# ---------- For F-Test Plotted Results ------------
# Class to draw the scatter plots with the F-value, T-value, MSR value  from the above tests
class ScatterPlot(wx.Panel):
    # more GUI stuff similar to other plots
    def __init__(self, parent, x, y, tree_menu, root, titlelbl, xlbl, ylbl, data, res):
        # gets the Panel properties
        wx.Panel.__init__(self, parent, size=wx.Size(640, 480), style=wx.SIMPLE_BORDER)
        self.root = root
        self.parent = parent
        self.figure = Figure()
        # defines the plot not entirely sure what the numbers in add_subplot mean
        self.axes = self.get_fig().add_subplot(111)

        self.canvas = FigureCanvas(self, -1, self.get_fig())
        self.Fit()

        self.x = x
        self.y = y
        self.data = data
        self.res_list = res

        self.tree_menu = tree_menu

        self.isSaved = False
        self.isLegend = False
        self.legendLoc = 'best'

        self.df1 = 0
        self.df2 = 0
        self.alpha = 0
        self.min_msr = 0

        # -------------------------- GRAPH LABELS ---------------------------------------
        self.titlelabel = titlelbl
        self.xlabel = xlbl
        self.ylabel = ylbl
        self.get_axes().set_title(self.get_titlelabel())
        self.get_axes().set_xlabel(self.get_xlabel())
        self.get_axes().set_ylabel(self.get_ylabel())
        # ------------------------- HOVER ANNOTATE -------------------------------
        self.annot = self.get_axes().annotate("", xy=(0, 0), xytext=(0.025, 0.025), textcoords="axes fraction",
                                              bbox=dict(boxstyle="round", fc="w"),
                                              arrowprops=dict(arrowstyle="->"))
        self.get_annot().set_visible(False)

        self.line_annot = self.get_axes().annotate("", xy=(0, 0),
                                                   xytext=(0.5, 0.5), textcoords="figure fraction",
                                                   bbox=dict(boxstyle="round", fc="w"))
        self.line_annot.draggable()
        self.line_annot_pos = [0, 0]
        self.line_annot.set_visible(False)

        def update_annot(ind):

            pos = self.get_scatter_plot().get_offsets()[ind["ind"][0]]
            self.get_annot().xy = pos
            text = "Point \n{}, {}".format(np.round_(pos[0], 5), np.round_(pos[1], 3))
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

        # ---------------------------------- GRAPH STYLE ---------------------------
        self.dataColor = 'xkcd:blue'
        self.dataSymbol = 'o'
        self.dataSymbolSize = 8
        self.legend_text = ['data']
        self.lineColor = 'xkcd:red'
        # ---------------------------------------------------------------
        self.scatter_plot = None

        def pick_point(event):

            if event.dblclick:
                if event.inaxes == self.get_axes():
                    cont, ind = self.get_scatter_plot().contains(event)
                    if cont:

                        pos = self.get_scatter_plot().get_offsets()[ind["ind"][0]]

                        scale = pos[0]
                        index = self.get_data().get_results_scale().index(scale)
                        # print("Scale: {}".format(scale))
                        # print("Pos: {}".format(pos))
                        # print('Scale List: {}'.format(self.get_data().get_results_scale()))
                        # print('Index: {}'.format(index))
                        # print('Results List: {}'.format(self.get_res_list()))
                        results = self.get_res_list()[index]

                        if len(results) == 14:
                            vals = results[1:]

                            if results[0] == 'accepted':

                                # ACCEPTED CASE
                                accepted = """
                                0. Hypotheses
                                H0: σ1^2 = σ2^2
                                H1: σ1^2 ≠ σ2^2
                                
                                1. Variance and mean
                                Group 1                                   Group 2
                                Variance: {}                              Variance: {}
                                Mean: {}                                  Mean: {}
                                Standard Deviation: {}                    Standard Deviation: {}
    
                                2. H0 hypothesis
                                Since p-value > α, H0 is accepted.
                                The sample standard deviation of the Group 1's population is considered to be equal to the sample
                                standard deviation of the Group 2's population. So the difference between the sample standard 
                                deviation of the Group 1 and Group 2 populations is not big enough to be statistically significant.
    
                                3. P-value
                                p-value equals {}. This means that if we would reject H0,
                                the chance of type I error (rejecting a correct H0) would be too high: {} ({}%)
                                The larger the p-value the more it supports H0
    
                                4. The statistics
                                The test statistic f equals {}, is in the {}% critical value accepted range: [{} : {}]
                                """.format(*vals)
                                dlg = StatsResultDialog(self.get_parent(), accepted, scale)

                            elif results[0] == 'rejected':

                                # REJECTED CASE
                                rejected = """
                                0. Hypotheses
                                H0: σ1^2 = σ2^2
                                H1: σ1^2 ≠ σ2^2
                                
                                1. Variance and mean
                                Group 1                                     Group 2
                                Variance: {}                                Variance: {}
                                Mean: {}                                    Mean: {}
                                Standard Deviation: {}                      Standard Deviation: {}
    
                                2. H0 hypothesis
                                Since p-value < α, H0 is rejected.
                                The sample standard deviation of the Group 1's population is considered to be less than the sample 
                                standard deviation of the Group 2's population.
    
                                3. P-value
                                p-value equals {}. This means that the chance of 
                                type1 error (rejecting a correct H0) is small: {} ({}%)
                                The smaller the p-value the more it supports H1
    
                                4. The statistics
                                The test statistic f equals {}, is not in the {}% critical value accepted range: [{} : {}]
                                """.format(*vals)
                                dlg = StatsResultDialog(self.get_parent(), rejected, scale)

                        if len(results) == 11:

                            text = """ 
                                    1. Variance and mean
                                    Group 1                                               Group 2
                                    Variance: {}                                        Variance: {}
                                    Mean: {}                                        Mean: {}
                                    Standard Deviation: {}                       Standard Deviation: {}
                            
                                    2. Statistics
                                    T-Value: {}
                                    Two-Tailed P-value: {}
                                    Left-Tailed P-value: {}
                                    Right-Tailed P-value: {}
                                    Confidence: {}
                                    """.format(*results)
                            dlg = StatsResultDialog(self.get_parent(), text, scale)

                        if len(results) == 5:

                            text = """
                                    Mean Square Ratio (MSR): {}
                                    Minimum MSR: {}
                                    Confidence: {}
                                    Degrees of Freedom (Numerator, Denominator): {}, {}
                                    """.format(*results)
                            dlg = StatsResultDialog(self.get_parent(), text, scale)

        self.get_fig().canvas.mpl_connect("button_press_event", pick_point)

        # --------------------- SIZER ---------------------------------
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND) # wx.SHAPED keeps aspect ratio)
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
    # set labels from user input
    def label(self, title, xlabel, ylabel):

        # labels the title, ylabel, xlabel of the regression plot from user input
        self.get_axes().set_title(title)
        self.get_axes().set_xlabel(xlabel)
        self.get_axes().set_ylabel(ylabel)
        # updates the regression plot's label
        self.get_canvas().draw()
    # draw the scatter plot
    def draw_scatter(self):

        self.set_scatter_plot(self.get_axes().scatter(self.get_x(), self.get_y(), s=self.get_dataSymbolSize(), marker=self.get_dataSymbol(),
                                color=self.get_dataColor()))
        # log scale on x-axis
        self.get_axes().set_xscale('log')
        self.get_canvas().draw()
    # draw the line for the minimum MSR value given the size of the data sets
    def draw_line(self, x, min_msr):

        y = []

        for i in x:

            y.append(min_msr)

        self.get_axes().plot(x, y, '-', color=self.get_lineColor())
        self.get_axes().set_xscale('log')

        # this will need to be movable such that it never overlaps scattered points it should be movable now
        # self.get_axes().text(x=2, y=(min_msr + 0.2), s='Minimum MSR = {}'.format(min_msr), fontsize=8)

        self.get_canvas().draw()

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
    def get_parent(self): return self.parent
    def get_root(self): return self.root
    def get_lineColor(self): return self.lineColor
    def set_lineColor(self, color): self.lineColor = color
    def get_dataColor(self): return self.dataColor
    def set_dataColor(self, color): self.dataColor = color
    def get_dataSymbol(self): return self.dataSymbol
    def set_dataSymbol(self, symbol): self.dataSymbol = symbol
    def get_dataSymbolSize(self): return self.dataSymbolSize
    def set_dataSymbolSize(self, size): self.dataSymbolSize = size
    def get_legendText(self): return self.legend_text
    def set_legendText(self, txt): self.legend_text = txt
    def get_scatter_plot(self): return self.scatter_plot
    def set_scatter_plot(self, plt): self.scatter_plot = plt
    def get_data(self): return self.data
    def get_res_list(self): return self.res_list
    def get_line_annot(self): return self.line_annot
    def set_line_annot(self, annot): self.line_annot = annot
    def get_min_msr(self): return self.min_msr
    def set_min_msr(self, msr): self.min_msr = msr

    def get_df1(self): return self.df1
    def set_df1(self, df1): self.df1 = df1
    def get_df2(self): return self.df2
    def set_df2(self, df2): self.df2 = df2
    def get_alpha(self): return self.alpha
    def set_alpha(self, a): self.alpha = a
    def get_annot(self): return self.annot
# Class for the dialog with the scatter plot it in
class ScatterDialog(wx.Frame):
    # GUI stuff
    def __init__(self, parent, title, x, y, tree_menu, root, titlelbl, xlbl, ylbl, data, res):
        # wx.Dialog.__init__(self, parent, wx.ID_ANY, "Graph", size=(640, 480))
        wx.Frame.__init__(self, parent, title=title, size=(640, 530), style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)

        self.parent = parent
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.graph = ScatterPlot(self, x, y, tree_menu, root, titlelbl, xlbl, ylbl, data, res)

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
        self.annotate = self.graphmenu.Append(wx.ID_ANY, 'Annotate', 'Annotate')
        self.grid = self.graphmenu.Append(wx.ID_ANY, 'Grid', 'Grid')
        self.gColor = self.graphmenu.Append(wx.ID_ANY, 'Graph Color...', 'Graph Color...')
        self.Bind(wx.EVT_MENU, self.OnGraphColor, self.gColor)
        self.Bind(wx.EVT_MENU, self.OnLabel, self.label)
        self.Bind(wx.EVT_MENU, self.OnLegend, self.legend)
        self.Bind(wx.EVT_MENU, self.OnSymbol, self.symbol)
        self.Bind(wx.EVT_MENU, self.OnAnnotate, self.annotate)
        self.Bind(wx.EVT_MENU, self.OnGrid, self.grid)

        self.statsmenu = wx.Menu()
        self.confidence = self.statsmenu.Append(wx.ID_ANY, 'Confidence', 'Confidence')
        self.Bind(wx.EVT_MENU, self.OnConfidence, self.confidence)

        # creates the menu bar and adds the tab to the top of the page
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(self.filemenu, 'File')
        self.menuBar.Append(self.graphmenu, 'Graph')
        self.menuBar.Append(self.statsmenu, 'Statistics')
        self.SetMenuBar(self.menuBar)

        # -------------------------------------------- TEXT STUFF ----------------------------------------
        self.annotated = False
        self.isGrid = False
        # ------------------------------ GRAPH ANNOTATION -----------------------------------------------
        # self.ann = []
        self.legend_text = ['Line', 'Data']
        self.sizer.Add(self.graph, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Layout()
        self.Fit()
    # these following functions are the same as whats commented in the RegressionSelectDialog class
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
            self.get_graph().set_line_annot(self.get_graph().get_axes().annotate("", xy=(0, 0),
                                                                                 xytext=(0.5, 0.5), textcoords="figure fraction",
                                                                                 bbox=dict(boxstyle="round", fc="w")))
            self.get_graph().get_line_annot().set_visible(False)
            self.get_graph().get_line_annot().draggable()

            self.get_graph().get_axes().scatter(self.get_graph().get_x(),
                                                self.get_graph().get_y(),
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

            if self.get_graph().get_ylabel() == 'MSR':
                self.get_graph().draw_line(self.get_graph().get_x(), self.get_graph().get_min_msr())

            self.get_graph().get_canvas().draw()

    def OnAnnotate(self, event):

        xvals = self.get_graph().get_x()

        xmax = max(xvals)
        xmin = min(xvals)

        diff = xmax - xmin

        min_msr = self.get_graph().get_min_msr()

        text = 'Minimum MSR = {}'.format(min_msr)

        self.get_graph().get_line_annot().xy = [diff, min_msr]

        self.get_graph().get_line_annot().set_text(text)
        self.get_graph().get_line_annot().set_fontsize(9)
        self.get_graph().get_line_annot().get_bbox_patch().set_alpha(0)

        if self.get_graph().get_line_annot().get_visible():
            self.get_graph().get_line_annot().set_visible(False)
            self.get_graph().get_fig().canvas.draw_idle()
        else:
            self.get_graph().get_line_annot().set_visible(True)
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

            self.get_graph().set_line_annot(self.get_graph().get_axes().annotate("", xy=(0, 0),
                                                                                 xytext=(0.5, 0.5),
                                                                                 textcoords="figure fraction",
                                                                                 bbox=dict(boxstyle="round", fc="w")))
            self.get_graph().get_line_annot().set_visible(False)
            self.get_graph().get_line_annot().draggable()

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

            if self.get_graph().get_ylabel() == 'MSR':
                self.get_graph().draw_line(self.get_graph().get_x(), self.get_graph().get_min_msr())

            self.get_graph().get_canvas().draw()

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

        if self.get_graph().get_ylabel() == 'MSR':

            lineColorTxt = wx.StaticText(graphColorPanel, -1, 'Line', pos=(10, 45))
            lineColor = wx.Choice(graphColorPanel, wx.ID_ANY, pos=(50, 45),
                                  choices=['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'custom...'])

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

            lineColor.Bind(wx.EVT_CHOICE, OnLineColor)

        graphColorDialog.CenterOnScreen()
        result = graphColorDialog.ShowModal()

        if result == wx.ID_OK:

            self.get_graph().get_axes().cla()
            self.get_graph().set_line_annot(self.get_graph().get_axes().annotate("", xy=(0, 0),
                                                                                 xytext=(0.5, 0.5),
                                                                                 textcoords="figure fraction",
                                                                                 bbox=dict(boxstyle="round", fc="w")))
            self.get_graph().get_line_annot().set_visible(False)
            self.get_graph().get_line_annot().draggable()

            self.get_graph().get_axes().scatter(self.get_graph().get_x(),
                                                self.get_graph().get_y(),
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

            if self.get_graph().get_ylabel() == 'MSR':

                self.get_graph().draw_line(self.get_graph().get_x(), self.get_graph().get_min_msr())

            self.get_graph().get_canvas().draw()

    def add_legend(self, loc, txt):
        self.get_graph().get_axes().legend(labels=txt, loc=loc)
        self.get_graph().set_isLegend(True)
        self.get_graph().set_legendLoc(loc)
    # set the confidence value only for min MSR line enabled for ANOVA results only
    def OnConfidence(self, event):

        dlg = ConfidenceDialog(self, self.get_graph().get_alpha())
        dlg.CenterOnScreen()
        res = dlg.ShowModal()

        if res == wx.ID_OK:

            dlg.set_val(float(dlg.get_t().GetValue()))
            self.get_graph().set_alpha(dlg.get_val())

            min_msr = np.round_(stats.f.ppf(self.get_graph().get_alpha(), self.get_graph().get_df1(), self.get_graph().get_df2()), 5)

            self.get_graph().set_min_msr(min_msr)
            self.get_graph().get_axes().cla()
            self.get_graph().set_line_annot(self.get_graph().get_axes().annotate("", xy=(0, 0),
                                                                                 xytext=(0.5, 0.5),
                                                                                 textcoords="figure fraction",
                                                                                 bbox=dict(boxstyle="round", fc="w")))
            self.get_graph().get_line_annot().set_visible(False)
            self.get_graph().get_line_annot().draggable()

            self.get_graph().get_axes().scatter(self.get_graph().get_x(),
                                                self.get_graph().get_y(),
                                                marker=self.get_graph().get_dataSymbol(),
                                                s=self.get_graph().get_dataSymbolSize(),
                                                color=self.get_graph().get_dataColor())
            if self.get_graph().get_isLegend():
                self.get_graph().get_axes().legend(labels=self.get_graph().get_legendText(),
                                                   loc=self.get_graph().get_legendLoc())

            if self.get_isGrid():
                self.get_graph().get_axes().grid(True)
                self.set_isGrid(True)

            self.get_graph().label(self.get_graph().get_titlelabel(),
                                   self.get_graph().get_xlabel(),
                                   self.get_graph().get_ylabel())
            self.get_graph().get_axes().set_xscale('log')

            self.get_graph().draw_line(self.get_graph().get_x(), min_msr)

    def get_graph(self): return self.graph
    # def get_annotated(self): return self.annotated
    # def set_annotated(self, ann): self.annotated = ann
    # def get_ann(self): return self.ann
    # def set_ann(self, a): self.ann = a
    def get_isGrid(self): return self.isGrid
    def set_isGrid(self, g): self.isGrid = g
    def get_legend_text(self): return self.legend_text
    def set_legend_text(self, txt): self.legend_text = txt
    def get_parent(self): return self.parent
    def get_saved_legend_text(self): return self.legend_text
    def set_saved_legend_text(self, txt): self.legend_text = txt
# dialog which displays the statistics for each test this is displayed when clicking on one of the points in the
# scale by T-value, F-value, or MSR plots
class StatsResultDialog(wx.Dialog):

    def __init__(self, parent, txt, scale):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Results at Scale: " + str(scale) + "um^2", size=(720, 480))

        self.panel = wx.Panel(self, wx.ID_ANY)

        self.text = wx.TextCtrl(self.panel, pos=(0,0), size=(694,400), style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.text.SetBackgroundColour('#f0f0f0')
        self.text.AppendText(txt)

        self.okbtn = wx.Button(self.panel, wx.ID_OK, "OK", pos=(600, 410))

        self.panel.Fit()
        self.Layout()
        self.ShowModal()
# dialog to set the confidence value fot he ANOVA test to find the minimum MSR
class ConfidenceDialog(wx.Dialog):
    # GUI stuff
    def __init__(self, parent, t):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Confidence", size=(300, 220))
        self.panel = wx.Panel(self, wx.ID_ANY)

        self.lbltitle = wx.StaticText(self.panel, label="Confidence: ", pos=(20, 20))
        self.title = wx.TextCtrl(self.panel, value=str(t), pos=(160, 20), size=(100, -1))
        self.ok = wx.Button(self.panel, id=wx.ID_OK, label="OK", pos=(80, 140))
        self.cancel = wx.Button(self.panel, id=wx.ID_CANCEL, label="Cancel", pos=(175, 140))
        # self.ok.Bind(wx.EVT_BUTTON, self.SaveString)
        self.cancel.Bind(wx.EVT_BUTTON, self.OnQuit)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)

        self.title_txt = t

    def OnQuit(self, event):

        self.Destroy()

    def SaveString(self, event):

        self.set_val(float(self.title.GetValue()))
        self.Destroy()

    def get_val(self): return self.title_txt
    def set_val(self, t): self.title_txt = t
    def get_t(self): return self.title


