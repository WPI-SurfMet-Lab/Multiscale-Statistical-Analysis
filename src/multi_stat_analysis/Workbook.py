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

    def hide_graph(self):
        if self.graph_panel is not None:
            self.graph_panel.Hide()

    def show_graph(self):
        if self.graph_panel is not None:
            self.graph_panel.Show()

    def clear_graph_panel(self):
        """Delete current graph if it has been created previously. Otherwise do nothing."""
        if self.graph_panel is not None:
            self.graph_panel.Destroy()
            self.graph_panel = None
