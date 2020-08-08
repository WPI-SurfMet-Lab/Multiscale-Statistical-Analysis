from enum import Enum

class MulticaleDataset:
    """Maintains the multiscale-dataset for relative area and complexity"""
    
    def set_vals_at_scale(self, scale, relative_area, complexity):
        """Assign relative area & complexity values at the given scale."""
        self._scales.add(scale)
        self._area_map[scale] = relative_area
        self._complexity_map[scale] = complexity
    
    def __init__(self, name="",
                 scales=[], relative_area=[], complexity=[],
                 row_labels=["Relative Area", "Fractal complexity"]):
        """Generate MultiscaleDataset using given values."""
        self.name = name
        self.regress_val = self.name
        self.row_labels = row_labels
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
        super().__init__("The dataset " + dataset.name + " being added has disjoint scale values.")

_TABLE_SCALE_COLUMN_LABEL = "Scale of Analysis"

class MultiscaleCollection:
    """Maintains the full dataset being used for analysis, and helps with handling scale discrepencies."""
    def __init__(self):
        """Creates empty dataset collection. To add to the dataset, use append_data."""
        # Set of unified scales, used for efficient scale checking
        self._scales = set()
        # List of unified scales, equivalent to scales set but in order
        self._scales_list = [] 

        # List of datasets in collection
        self._datasets = []
        # --- Following lists are in corresponding order to _datasets ---
        self._names = []
        self._regress_vals = []
        self._row_labels = []
        # Unified 2D list of list of area values for each set
        self._areas = []
        # Unified 2D list of list of complexity values for each set
        self._complexities = []
        # Unified 2D list of list of regression set rows
        self._regress_sets = []

    def append_data(self, dataset, option:DatasetAppendOptions=DatasetAppendOptions.IgnoreUnaligned):
        """Add data to dataset.
        @param scale_data - scale data to be inserted. Needs to be either a MulticaleDataset or list of MulticaleDatasets.
        @param option - Option configuration option for appending data."""
        if isinstance(dataset, list): self._append_data_list(dataset, option)
        elif isinstance(dataset, MulticaleDataset): self._append_data_single(dataset, option)
        else: raise ValueError("Argument 'dataset' cannot be of type '" + type(dataset).__name__ + "'.")

    def _append_data_single(self, dataset:MulticaleDataset, option:DatasetAppendOptions=DatasetAppendOptions.IgnoreUnaligned):
        """Add data to dataset.
        @param scale_data - scale data to be inserted.
        @param option - Option configuration option for appending data."""
        # If dataset has not been initialized, define it
        if not self._datasets:
            self._scales = dataset.get_scales()
            self._scales_list = self.build_ordered_scales()
            self._datasets.append(dataset)
            self._names.append(dataset.name)
            self._regress_vals.append(dataset.regress_val)
            self._row_labels.append(dataset.row_labels)
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

    def _append_ignore_unaligned_scales(self, dataset:MulticaleDataset):
        """Add new result data to dataset. Ignores unaligned scales.
        @param scale_data - scale data to be inserted. Cannot be none."""
        # if the dataset is unusable (scales are disjoint) do not continue
        new_scales = dataset.get_scales()
        if self._scales.isdisjoint(new_scales):
            raise MultiscaleDisjointCollectionException(dataset)

        # Add dataset to collection
        new_index = len(self._datasets)
        self._datasets.append(dataset)
        self._names.append(dataset.name)
        self._regress_vals.append(dataset.regress_val)
        self._row_labels.append(dataset.row_labels)

        # Create unified scale set through intersection of scale sets
        unified_scales = self._scales.intersection(new_scales)
        # Check if the unified scale values have not changed
        scales_changed = not self._scales == unified_scales
        self._scales = unified_scales
        del unified_scales
        # Update scales list if needed
        if scales_changed: self._scales_list = self.build_ordered_scales()

        # Run through dataset and generate/modify unified data values
        for index in range(new_index, -1, -1):
            # Get current dataset being looked at
            curr_dataset = self._datasets[index]
            # Generate new area lists, and complexity lists
            new_areas = []
            new_complexities = []
            for scale in self._scales_list:
                new_areas.append(curr_dataset.get_relative_area(scale))
                new_complexities.append(curr_dataset.get_complexity(scale))

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

    def build_ordered_scales(self):
        """Outputs and builds the scale set as an ordered list."""
        return sorted(self._scales)

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
        data_dict = {(1,0): _TABLE_SCALE_COLUMN_LABEL}
        data_column_lists = (self._areas, self._complexities)

        # Define scale columns
        data_dict[(1, 0)] = _TABLE_SCALE_COLUMN_LABEL
        for index in range(len(self._scales_list)):
            data_dict[(index + 2, 0)] = self._scales_list[index]
        
        # Define data columns
        for col_index in range(1, len(self._datasets) * 2 + 1):
            # Pre-calculate indexes for later
            offset_index = col_index - 1
            data_col_pos = offset_index % 2
            dataset_index = offset_index // 2

            # Write data name labels
            data_dict[(0,col_index)] = self._names[dataset_index]
            # Write data column labels
            data_dict[(1,col_index)] = self._row_labels[dataset_index][data_col_pos]

            # Write data columns
            selected_data = data_column_lists[data_col_pos][dataset_index]
            for row in range(len(selected_data)):
                data_dict[(row + 2), col_index] = selected_data[row]

        return data_dict

    def get_size(self): return len(self._datasets)
    def get_results_scale(self): return self._scales_list
    def get_legend_txt(self): return self._names
    def get_row_labels(self): return self._row_labels
    def get_x_regress(self): return self._regress_vals
    def set_x_regress(self, new_regress_vals): self._regress_vals = new_regress_vals
    def get_relative_area(self): return self._areas
    def get_complexity(self): return self._complexities
    def get_regress_sets(self): return self._regress_sets

# Define functions for DatasetAppendOptions
DatasetAppendOptions.IgnoreUnaligned.append = MultiscaleCollection._append_ignore_unaligned_scales