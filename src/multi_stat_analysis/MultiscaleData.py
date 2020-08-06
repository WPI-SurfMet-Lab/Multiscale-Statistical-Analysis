from enum import Enum

class MulticaleDataset:
    """Maintains the multiscale-dataset for relative area and complexity"""
    
    def set_vals_at_scale(self, scale, relative_area, complexity):
        """Assign relative area & complexity values at the given scale."""
        self._scales.add(scales)
        self._area_map[scale] = relative_area
        self._complexity_map[scale] = complexity
    
    def __init__(self, name="",
                 scales=[], relative_area=[], complexity=[],
                 row_titles=["Relative Area", "Fractal complexity"]):
        """Generate MultiscaleDataset using given values."""
        self.name = name
        self.regress_val = self.name
        self.row_titles = row_titles
        self._scales = set()
        self._area_map = {}
        self._complexity_map = {}

        # Run through collected scales and map them in order to areas and complexities
        for i, scale in enumerate(scales):
            self.set_vals_at_scale(scale, relative_area[i], complexity[i])

    def get_scales(self): return self._scales
    def get_relative_area(self, scale): return self._area_map.get(scale)
    def get_complexity(self, scale): return self._complexity_map.get(scale)

class DatasetAppendOptions(Enum):
    """Used to define the insert function to be used by Dataset.insertData."""
    # Functions are defined further down
    IgnoreUnaligned = (None)

    def __init__(self, insert_func):
        self.append = insert_func

class MultiscaleDisjointCollectionException(Exception):
    def __init__(self, dataset:MulticaleDataset):
        super().__init__("The dataset" + dataset.name + " being added to MultiscaleCollection has disjoint scale values.")

_TABLE_SCALE_COLUMN_LABEL = "Scale of Analysis"

class MultiscaleCollection:
    """Maintains the full dataset being used for analysis, and helps with handling scale discrepencies."""
    def __init__(self):
        """Creates empty dataset collection. To add to the dataset, use append_data."""
        # List of datasets being added
        self._datasets = []
        # Set of unified scales, which ignores unidentical scales
        self._scales = set()
        # Unified 2D list of list of area values for each set
        self._areas = []
        # Unified 2D list of list of complexity values for each set
        self._complexities = []
        # Unified 2D list of list of regression set rows
        self._regress_sets = []

    def _append_data_single(self, dataset:MulticaleDataset, option:DatasetAppendOptions=DatasetAppendOptions.IgnoreUnaligned):
        """Add data to dataset.
        @param scale_data - scale data to be inserted.
        @param option - Option configuration option for appending data."""
        # If dataset has not been initialized, define it
        if not self._datasets:
            self._datasets.append(dataset)
            self._scales = dataset.get_scales()
            self._areas.append([dataset.get_relative_area(scale) for scale in sorted(self._scales)])
            self._complexities.append([dataset.get_complexity(scale) for scale in sorted(self._scales)])
            self._regress_sets = self.build_regress_sets()
        # Add to dataset
        else:
            option.append(self, dataset)

    def _append_data_list(self, dataset_list:list, option:DatasetAppendOptions=DatasetAppendOptions.IgnoreUnaligned):
        """Add list of data to dataset.
        @param scale_data - list of scale data to be inserted.
        @param option - Option configuration option for appending data."""
        for dataset in dataset_list:
            self._append_data_single(dataset, option)

    def _append_ignore_unaligned_scales(self, scale_data:MulticaleDataset):
        """Add new result data to dataset. Ignores unaligned scales.
        @param scale_data - scale data to be inserted. Cannot be none."""
        # if the dataset is unusable (scales are disjoint) do not continue
        new_scales = scale_data.get_scales()
        if self._scales.isdisjoint(new_scales):
            raise MultiscaleDisjointCollectionException(scale_data)

        # Add to set of usable dataset indicies
        new_index = len(self._datasets)
        self._datasets.append(scale_data)

        # Create unified scale set through intersection of scale sets
        unified_scales = self._scales.intersection(new_scales)
        # Check if the unified scale values have not changed
        scales_changed = not self._scales == unified_scales
        self._scales = unified_scales

        # Generate new area lists, complexity lists, and regression sets
        for index in range(new_index, -1, -1):
            new_areas = []
            new_complexities = []
            for scale in sorted(self._scales):
                new_areas.append(scale_data.get_relative_area(scale))
                new_complexities.append(scale_data.get_complexity(scale))

            # replacable_list - Defines the lists that needed to be be given modified items
            # at the current index. For relative area and complexity.
            #   [0] = List to be changed
            #   [1] = Item to be added
            replacable_lists = [(self._areas, new_areas), 
                                (self._complexities, new_complexities)]
            # Replace currently selected dataset lists for area and complexity
            for curr_list, new_item in replacable_lists:
                if index != new_index:
                    curr_list.pop(index)
                curr_list.insert(index, new_item)

            # If the scale values have not changed and the newly added dataset has been added
            # stop generating new data lists
            if not scales_changed and index == new_index:
                break

        # Build regression sets after creating new relative area list
        self._regress_sets = self.build_regress_sets()

    def append_data(self, dataset, option:DatasetAppendOptions=DatasetAppendOptions.IgnoreUnaligned):
        """Add data to dataset.
        @param scale_data - scale data to be inserted. Needs to be either a MulticaleDataset or list of MulticaleDatasets.
        @param option - Option configuration option for appending data."""
        if isinstance(dataset, list): self._append_data_list(dataset, option)
        elif isinstance(dataset, MulticaleDataset): self._append_data_single(dataset, option)
        else: raise ValueError("Argument 'dataset' cannot be of type '" + type(dataset).__name__ + "'.")

    def build_regress_sets(self):
        """Iterate over all of the relative areas from each dataset, and compile them into a regress set.
        Create a list of relative areas for each scale at each index.
        @return List of compiled regression sets from relative areas."""
        output_reg_set = []
        for y_values in zip(*self.get_relative_area()):
            # the list of all relative areas at the same scale for the different data sets
            # these lists are then appended to regress sets such that
            # there is a list of relative areas for each scale.
            output_reg_set.append(list(y_values))
        return output_reg_set

    def build_table_data(self):
        """Builds data to be display on the table.
        @return Dictionary with (row,column) position tuple as key"""
        # Start with scale of analysis column label
        data_dict = {(start - 1, 0): _TABLE_SCALE_COLUMN_LABEL}
        row_titles = self.get_row_titles()
        start = 1

        for num in range(start + 1, len(self.get_results_scale()) + 1 + start):
            data_dict[(num, 0)] = self.get_results_scale()[num - (1 + start)]

        for num in range(2, 2*len(self.get_legend_txt()) + 1, 2):
            data_dict[(start, int(num - 1))] = self.get_legend_txt()[int(num / 2) - 1][:len(self.get_legend_txt()[int(num / 2) - 1]) - 4]
            # relative area
            data_dict[(start - 1, num - 1)] = row_titles[0]
            data_dict[(start, int(num))] = self.get_legend_txt()[int(num / 2) - 1][:len(self.get_legend_txt()[int(num / 2) - 1]) - 4]
            # Fractal complexity
            data_dict[(start - 1, num)] = row_titles[1]

            for i in range(start + 1, len(self.get_relative_area()[int(num / 2) - 1]) + 1 + start):
                data_dict[(i, int(num - 1))] = self.get_relative_area()[int(num / 2) - 1][i - (1 + start)]

            for i in range(start + 1, len(self.get_complexity()[int(num / 2) - 1]) + 1 + start):
                data_dict[(i, int(num))] = self.get_complexity()[int(num / 2) - 1][i - (1 + start)]

        return data_dict

    def get_results_scale(self): return sorted(self._scales)
    def get_legend_txt(self): return [dataset.name for dataset in self._datasets]
    def get_row_titles(self): return [dataset.row_titles for dataset in self._datasets]
    def get_x_regress(self): return [dataset.regress_val for dataset in self._datasets]
    def get_relative_area(self): return self._areas
    def get_complexity(self): return self._complexities
    def get_regress_sets(self): return self._regress_sets

# Define functions for DatasetAppendOptions
DatasetAppendOptions.IgnoreUnaligned.append = MultiscaleCollection._append_ignore_unaligned_scales