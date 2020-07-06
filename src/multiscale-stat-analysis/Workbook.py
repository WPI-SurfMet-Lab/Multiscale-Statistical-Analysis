
import wx.grid


class Workbook(wx.grid.GridTableBase):

    def __init__(self, data:dict, name:str, rows:int, columns:int):
        wx.grid.GridTableBase.__init__(self)
        self.data = data
        self.name = name
        self.rows = rows
        self.columns = columns
        self.IsSaved = False

    def GetNumberRows(self):
        return self.get_rows()

    def GetNumberCols(self):
        return self.get_cols()

    def IsEmptyCell(self, row, col):
        return self.data.get((row, col)) is not None

    def GetValue(self, row, col):
        value = self.data.get((row, col))
        if value is not None:
            return value
        else:
            return ''

    def SetValue(self, row, col, value):
        self.data[(row, col)] = value

    def get_name(self): return self.name
    def set_name(self, name): self.name = name
    def get_data(self): return self.data
    def set_data(self, data): self.data = data
    def get_rows(self): return self.rows
    def get_cols(self): return self.columns
    def get_IsSaved(self): return self.IsSaved
    def set_IsSaved(self, saved): self.IsSaved = saved
