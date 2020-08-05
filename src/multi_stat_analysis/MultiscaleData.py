from enum import Enum

class MulticaleDataset:
    """Maintains the multiscale-dataset for relative area and complexity"""
    def __init__(self, name, scales=set(), relative_area=[], complexity=[], regress_set=[], row_titles=[]):
        self.name = name
        self.regress_val = self.name
        self.row_titles = row_titles
        self._scales = scales
        self._area_map = {}
        self._complexity_map = {}
        self._regress_map = {}

        # Run through collected scales and map them in order to areas and complexities
        for i, scale in enumerate(scales):
            self._area_map[scale] = relative_area[i]
            self._complexity_map[scale] = complexity[i]
            self._regress_map[scale] = regress_set[i]

    @staticmethod
    def _map_setter(map, scale, value): self.map[scale] = value
    @staticmethod
    def _map_getter(map, scale):
        if scale in map:
            return map[scale]
        else:
            return None

    def get_scales(self): return self._scales
    def get_relative_area(self, scale): return _map_getter(self._area_map, scale)
    def set_relative_area(self, scale, area): _map_setter(self._area_map, scale, area)
    def get_complexity(self, scale): return _map_getter(self._complexity_map, scale)
    def set_complexity(self, scale, complexity): _map_setter(self._complexity_map, scale, complexity)
    def get_regress_set(self, scale): return _map_getter(self._regress_map, scale)
    def set_regress_set(self, scale, regress_val): _map_setter(self._regress_map, scale, regress_val)

class DatasetAppendOptions(Enum):
    """Used to define the insert function to be used by Dataset.insertData."""
    # Functions are defined further down
    IgnoreUnaligned = (None)

    def __init__(self, insert_func):
        self.append = insert_func

class MultiscaleDisjointCollectionException(Exception):
    def __init__(self, dataset:MulticaleDataset):
        super().__init__("The dataset" + dataset.name + " being added to MultiscaleCollection has disjoint scale values.")

class MultiscaleCollection:
    """Maintains the full dataset being used for analysis, and helps with handling scale discrepencies."""
    def __init__(self):
        """Creates empty dataset. To add to the dataset, use append_data."""
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

    def append_data(self, scale_data:MulticaleDataset, option:DatasetAppendOptions=DatasetAppendOptions.IgnoreUnaligned):
        """Add new result data to dataset.
        @param scale_data - scale data to be inserted. If none is given, nothing will occur.
        @param option - Option configuration option for appending data."""
        # Check for null data
        if scale_data is None:
            return
        # If dataset has not been initialized, define it
        if not self._datasets:
            self._datasets.append(scale_data)
            self._scales = scale_data.get_scales()
            self._areas.append([scale_data.get_relative_area(scale) for scale in sorted(self._scales)])
            self._complexities.append([scale_data.get_complexity(scale) for scale in sorted(self._scales)])
            self._regress_sets = self.build_regress_sets()
        # Add to dataset
        else:
            option.append(self, scale_data)

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

    def get_results_scale(self): return sorted(self._scales)
    def get_legend_txt(self): return [self._datasets[i].name for i in self._dataset_indicies]
    def get_row_titles(self): return [self._datasets[i].row_titles for i in self._dataset_indicies]
    def get_x_regress(self): return [self._datasets[i].regress_val for i in self._dataset_indicies]
    def get_relative_area(self): return self._areas
    def get_complexity(self): return self._complexities
    def get_regress_sets(self): return self._regress_sets

# Define functions for DatasetAppendOptions
DatasetAppendOptions.IgnoreUnaligned.append = MultiscaleCollection._append_ignore_unaligned_scales