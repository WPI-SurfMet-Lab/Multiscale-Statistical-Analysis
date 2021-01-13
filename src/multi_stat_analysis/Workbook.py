from MultiscaleData import MultiscaleDataset


class Workbook:

    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.dataset = MultiscaleDataset()
        self.graph_panel = None
        self.results = []

    def get_relative_area(self):
        return self.dataset.get_relative_area()

    def get_complexity(self):
        return self.dataset.get_complexity()
