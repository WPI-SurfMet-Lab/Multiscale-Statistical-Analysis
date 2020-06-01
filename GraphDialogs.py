
import wx
from wx.lib.scrolledpanel import ScrolledPanel

# Class LegendDialog:
# generic dialog used to add legends to graphs.
class LegendDialog(wx.Dialog):

    def __init__(self, parent, txt):
        # inherits the wx.Dialog class, set the ID, name, size of dialog
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Legend", size=(320, 400))

        # create panel to hold gui object
        self.legendPanel = wx.Panel(self, wx.ID_ANY)

        self.legend_text = ''
        # create check boxes with labels for each position for the legend on the axes.
        self.topL = wx.CheckBox(self.legendPanel, wx.ID_ANY, label="Top Left", pos=(10, 10))
        self.topR = wx.CheckBox(self.legendPanel, wx.ID_ANY, label="Top Right", pos=(10, 35))
        self.botL = wx.CheckBox(self.legendPanel, wx.ID_ANY, label="Bottom Left", pos=(10, 60))
        self.botR = wx.CheckBox(self.legendPanel, wx.ID_ANY, label="Bottom Right", pos=(10, 85))
        self.off = wx.CheckBox(self.legendPanel, wx.ID_ANY, label="Off", pos=(10, 110))

        self.lbltxt = wx.StaticText(self.legendPanel, label="Legend Text", pos=(10, 135))
        # self.legend_text = wx.TextCtrl(self.legendPanel, value=str(txt), pos=(10, 155), size=(210, -1))

        self.sep = wx.StaticLine(self.legendPanel, -1, pos=(10, 160), size=(280, -1), style=wx.LI_HORIZONTAL)
        # create a scroll-able panel
        self.scroll_panel = ScrolledPanel(self.legendPanel, wx.ID_ANY, pos=(5, 170), size=(280, 125))
        self.scroll_panel.SetupScrolling(scroll_y=True, rate_x=20)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.txt_ctrl = []

        for legend_label in txt:
            # create a text box default legend label in the txt list which is an input for the class
            txt = wx.TextCtrl(self.scroll_panel, value=str(legend_label), pos=(140, 20), size=(250, -1))
            # add to txt ctrl list
            self.txt_ctrl.append(txt)
            # text box is added to the panel
            self.sizer.Add(txt, 0, wx.ALL, 5)

        # self.ok = wx.Button(self.btn_panel, id=wx.ID_OK, label="OK", pos=(240, 0))
        # self.cancel = wx.Button(self.btn_panel, id=wx.ID_CANCEL, label="Cancel", pos=(335, 0))

        # create ok button
        self.okbutton = wx.Button(self.legendPanel, wx.ID_OK, pos=(190, 330))

        # setup gui
        self.scroll_panel.SetSizer(self.sizer)
        self.scroll_panel.Layout()
        self.scroll_panel.Fit()

    # function to get a list containing the text in the text boxes
    def SaveString(self):
        # list of strings typed in for legend
        legend_txt = []
        # iterate over the text boxes
        for txt in self.get_txtctrl():
            # append the string to list
            legend_txt.append(txt.GetValue())
        # update list based on user inputs
        self.set_legend_text(legend_txt)

    def get_topL(self): return self.topL
    def get_topR(self): return self.topR
    def get_botL(self): return self.botL
    def get_botR(self): return self.botR
    def get_off(self): return self.off
    def get_lbltxt(self): return self.lbltxt
    def get_legend_text(self): return self.legend_text
    def set_legend_text(self, text): self.legend_text = text
    def get_txtctrl(self): return self.txt_ctrl

# Class SymbolDialog:
# generic dialog used to change symbol and size on graphs
class SymbolDialog(wx.Dialog):

    def __init__(self, parent):
        # set up dialog gui stuff
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Symbol Selection", size=(330,250))
        self.symbolPanel = wx.Panel(self, wx.ID_ANY)
        self.symbol_box = wx.StaticBox(self.symbolPanel, wx.ID_ANY, "Symbol", size=(220, 150), pos=(10,10))
        # symbol selection list
        self.symbol_selection = wx.ListCtrl(self.symbol_box, id=wx.ID_ANY, size=(200, 130), pos=(10,15), style=wx.LC_REPORT |
                                                                                                   wx.LC_NO_HEADER |
                                                                                                   wx.NO_BORDER |
                                                                                                   wx.LC_SINGLE_SEL)
        self.symbol_selection.SetBackgroundColour('#f0f0f0')
        self.symbol_selection.InsertColumn(0, "0", width=175)
        # all of the possible symbol type descriptions
        self.choices = [["Point"],["Pixel"],["Circle"],["Triangle Down"],["Triangle Up"],["Triangle Left"],["Triangle Right"],
                        ["Tri Down"],["Tri Up"],["Tri Left"],["Tri Right"],["Octagon"],["Square"],["Pentagon"],["Plus (filled)"],
                        ["Star"],["Hexagon 1"],["Hexagon 2"],["Plus"],["X"],["X (filled)"],["Diamond"],["This Diamond"],["Vertical Line"],
                        ["Horizontal Line"],["Tick Left"],["Tick Right"],["Tick Up"],["Tick Down"],["Caret Left"],["Caret Right"],
                        ["Caret Up"],["Caret Down"],["Caret Left (center at base)"],["Caret Right (center at base)"],
                        ["Caret Up (center at base)"],["Caret Down (center at base)"]]
        # all of the codes used for each symbol in same list order as above. These are from documentation
        self.symbols = [".", ",", "o", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "*", "h", "H", "+",
                        "x", "X", "D", "d", "|", "_", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        # add to gui list selection
        [self.symbol_selection.Append(i) for i in self.choices]
        # default size choices for symbol
        self.size_choices = ["1", "2", "4", "8", "10", "12", "14", "16", "18", "20", "22", "24", "26", "28", "36", "48", "72"]
        # create symbol size selection gui object
        self.size_box = wx.StaticBox(self.symbolPanel, wx.ID_ANY, 'Size', size=(60,150), pos=(240,10))
        self.size_select = wx.Choice(self.size_box, wx.ID_ANY, pos=(10,20), choices=self.size_choices)

        # ok button and other gui set up stuff
        self.okbutton = wx.Button(self.symbolPanel, wx.ID_OK, pos=(220, 175))
        self.symbolPanel.Fit()
        self.symbolPanel.Layout()
        # connect the OnSelect function to left clicking on an object in the symbol list selection object
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect, self.symbol_selection)
        # hold selected symbol
        self.selectedSymbolName = ""
        self.selectedSymbol = ""
    # called when selecting item in list
    def OnSelect(self, event):

        self.selectedSymbolName = ""
        info = event.GetText()

        self.selectedSymbolName = info
        # uh some stuff that I don't remember how it works anymore but it
        # does so just go with it can be copied to other code

        def do_select():
            map(lambda x: self.symbol_selection.Select(x, 1), set(self.selectedSymbolName))

        wx.CallLater(100, do_select)
        self.selectedSymbol = self.symbols[self.choices.index([self.selectedSymbolName])]

    def get_selectedSymbol(self): return self.selectedSymbol
    def get_sizeChoices(self): return self.size_choices
    def get_sizeSelect(self): return self.size_select

# Call LabelDialog:
# generic dialog used to label the x, y -axis and title of graph plot
class LabelDialog(wx.Dialog):

    def __init__(self, parent, t, x, y):
        # inherit basic dialog and properties
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Label", size=(300, 220))
        self.panel = wx.Panel(self, wx.ID_ANY)
        # gui dialog labels and text boxes
        self.lbltitle = wx.StaticText(self.panel, label="Title: ", pos=(20, 20))
        self.title = wx.TextCtrl(self.panel, value=t, pos=(60, 20), size=(200, -1))
        self.lblxaxis = wx.StaticText(self.panel, label="X-Axis: ", pos=(20, 60))
        self.xaxis = wx.TextCtrl(self.panel, value=x, pos=(60, 60), size=(200, -1))
        self.lblyaxis = wx.StaticText(self.panel, label="Y-Axis: ", pos=(20, 100))
        self.yaxis = wx.TextCtrl(self.panel, value=y, pos=(60, 100), size=(200, -1))
        self.ok = wx.Button(self.panel, id=wx.ID_OK, label="OK", pos=(80, 140))
        self.cancel = wx.Button(self.panel, id=wx.ID_CANCEL, label="Cancel", pos=(175, 140))
        # bind save string function to ok button
        self.ok.Bind(wx.EVT_BUTTON, self.SaveString)
        # bind quit function to cancel button
        self.cancel.Bind(wx.EVT_BUTTON, self.OnQuit)
        self.Bind(wx.EVT_CLOSE, self.OnQuit)

        self.title_txt = ''
        self.xaxis_txt = ''
        self.yaxis_txt = ''

    def OnQuit(self, event):

        # destroy the dialog when closing it

        self.Destroy()

    def SaveString(self, event):
        # set these variables to the values in the text boxes
        self.set_title(self.title.GetValue())
        self.set_xaxis(self.xaxis.GetValue())
        self.set_yaxis(self.yaxis.GetValue())
        self.Destroy()

    def get_title(self): return self.title_txt
    def set_title(self, t): self.title_txt = t
    def get_xaxis(self): return self.xaxis_txt
    def set_xaxis(self, x): self.xaxis_txt = x
    def get_yaxis(self): return self.yaxis_txt
    def set_yaxis(self, y): self.yaxis_txt = y
