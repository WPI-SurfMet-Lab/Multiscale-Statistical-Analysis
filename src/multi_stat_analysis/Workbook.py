from MultiscaleData import MultiscaleDataset


class Workbook:

    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self._dataset = MultiscaleDataset()
        self.graph_panel = None
        self.results = []

    def get_dataset(self) -> MultiscaleDataset:
        return self._dataset

    def get_relative_area(self):
        return self._dataset.get_relative_area()

    def get_complexity(self):
        return self._dataset.get_complexity()
