from MultiscaleData import MultiscaleDataset, MultiscaleData, DatasetAppendOutput
import wx.grid

class Workbook(wx.grid.GridTableBase):

    def __init__(self, dataset, name:str, rows:int, columns:int):
        super().__init__()
        self.name = name
        self._dataset = dataset
        self._table_data = {}
        self._rows = rows
        self._columns = columns
        self._IsSaved = False

    def GetNumberRows(self):
        return self.get_rows()

    def GetNumberCols(self):
        return self.get_cols()

    def IsEmptyCell(self, row, col):
        return self._table_data.get((row, col)) is not None

    def GetValue(self, row, col):
        value = self._table_data.get((row, col))
        if value is not None:
            return value
        else:
            return ''

    def SetValue(self, row, col, value):
        self._table_data[(row, col)] = value

    def get_dataset(self): return self._dataset
    def append_data(self, data:MultiscaleData) -> DatasetAppendOutput:
        """Append data to the dataset."""
        output = self._dataset.append_data(data)
        self._table_data = self._dataset.build_table_data()
        return output

    def get_relative_area(self): return self._dataset.get_relative_area()
    def get_complexity(self): return self._dataset.get_complexity()

    def get_table_data(self): return self._table_data
    def set_table_data(self, data): self._table_data = data
    def get_rows(self): return self._rows
    def get_cols(self): return self._columns
    def get_IsSaved(self): return self._IsSaved
    def set_IsSaved(self, saved): self._IsSaved = saved
