import pandas as pd
import copy


class MultiscaleData:
    """Maintains the multiscale data for relative area and complexity"""

    def _set_vals_at_scale(self, scale, relative_area, complexity):
        """Assign relative area & complexity values at the given scale."""
        self._scales.add(scale)
        self._area_map[scale] = relative_area
        self._complexity_map[scale] = complexity

    def __init__(self, name="",
                 scales=None, relative_area=[], complexity=[],
                 row_labels=list(["Relative Area", "Multiscale complexity"])):
        """Generate MultiscaleData using given values."""
        if scales is None:
            scales = []
        self.name = name
        self.row_labels = row_labels
        self._scales = set()
        self._area_map = {}
        self._complexity_map = {}

        # Run through collected scales and map them in order to areas and complexities
        for i, scale in enumerate(scales):
            self._set_vals_at_scale(scale, relative_area[i], complexity[i])

    def get_scales(self): return self._scales

    def get_relative_area(self, scale): return self._area_map.get(scale)

    def get_complexity(self, scale): return self._complexity_map.get(scale)


_SUCCESS = 0


class DatasetAppendOutput:
    """Stores output values and flags from appending functions.
    By default is a success flag and no output."""
    # Used to define various outputs that are returns by the append function.
    SUCCESS = _SUCCESS  # SUCCESS - Has no output values
    SCALES_IGNORED_ERROR = -2  # SCALES_IGNORED - Outputs list of MulticaleDatasets that had ignored scales
    ERROR = -1  # ERROR - A general error has occured

    def __init__(self, flag=_SUCCESS, output=None):
        """Output for MultiscaleDataset append function.
        @param flag - Integer flag value that corresponds to the success/error value of output.
        @param output - Value of output. If SUCCESS, output None."""
        self.value = output
        self.flag = flag

    def __eq__(self, other):
        """Can be used to compare against itself or against AppendOutputEnums."""
        if isinstance(other, DatasetAppendOutput):
            return other.flag == self.flag
        elif isinstance(other, int):
            return other == self.flag
        else:
            return False

    def __bool__(self):
        """Can be used to check if an append was successful."""
        return self.flag == _SUCCESS

    def get_value(self):
        """Get value of output."""
        return self.value


class MultiscaleDisjointDatasetException(Exception):
    def __init__(self, dataset: MultiscaleData):
        super().__init__("The dataset " + dataset.name + " being added has disjoint scale values.")


def _multiscaledataset_append_ignore_unaligned_scales(self, dataset: MultiscaleData) -> DatasetAppendOutput:
    """Add new result data to dataset. Ignores unaligned scales.
    @param dataset - scale data to be inserted. Cannot be none."""
    # if the dataset is unusable (scales are disjoint) do not continue
    new_scales = dataset.get_scales()
    if self._scales.isdisjoint(new_scales):
        raise MultiscaleDisjointDatasetException(dataset)

    # Add data to dataset
    new_index = len(self.datasets)
    self.datasets.append(dataset)
    self._names.append(dataset.name)
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
        curr_dataset = self.datasets[index]
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

    # Add to regression table
    self.regress_table.add_dataset(dataset)
    # Build regression sets after creating new relative area list
    self._regress_sets = self.build_regress_sets()

    # Output SCALES_IGNORED_ERROR if scales were in-fact ignored
    if scales_changed:
        return DatasetAppendOutput(DatasetAppendOutput.SCALES_IGNORED_ERROR, [dataset])
    # Otherwise, output successful value
    else:
        return DatasetAppendOutput()


class _DatasetOptionCallables:
    """Used to define the insert functions to be used by Dataset.insertData."""

    def __init__(self, append_func):
        """Defines enum which stores a function that can be called later."""
        self.append_func = append_func

    def __call__(self, dataset, multiscale_data: MultiscaleData) -> DatasetAppendOutput:
        return self.append_func(dataset, multiscale_data)


class DatasetAppendOptions:
    """Used to organize the insert functions to be used by Dataset.insertData."""
    IgnoreUnaligned = _DatasetOptionCallables(_multiscaledataset_append_ignore_unaligned_scales)


class RegressValTable:
    DEFAULT_GROUP = "Default"

    def __init__(self):
        self._regress_group_table = pd.DataFrame()
        self.clear()

    def clear(self):
        self._regress_group_table = pd.DataFrame(columns=[RegressValTable.DEFAULT_GROUP])

    def copy(self):
        return copy.deepcopy(self)

    def get_regress_groups(self) -> list:
        return [col for col in self._regress_group_table.columns]

    def add_regress_group(self, group_name: str):
        self._regress_group_table[group_name] = 0.0

    def del_regress_group(self, group_name: str):
        del self._regress_group_table[group_name]

    def rename_regress_group(self, group_name: str, new_group_name: str):
        self._regress_group_table = self._regress_group_table.rename(columns={group_name: new_group_name})

    def does_group_exist(self, group_name: str) -> bool:
        return group_name in self._regress_group_table.columns

    def get_regress_group_list(self, group_name: str) -> list:
        return self._regress_group_table[group_name]

    def add_dataset(self, dataset: MultiscaleData):
        new_dataset_row = pd.DataFrame(data=0.0, index=[dataset], columns=self._regress_group_table.columns)
        self._regress_group_table = pd.concat([self._regress_group_table, new_dataset_row])

    def set_regress_val(self, group_name: str, dataset: MultiscaleData, new_regress_val: float):
        self._regress_group_table.at[dataset, group_name] = new_regress_val

    def get_regress_val(self, group_name: str, dataset: MultiscaleData) -> float:
        return self._regress_group_table.at[dataset, group_name]


_TABLE_SCALE_COLUMN_LABEL = "Scale of Analysis"


class MultiscaleDataset:
    """Maintains the full dataset being used for analysis, and helps with handling scale discrepencies."""

    def __init__(self):
        """Creates empty dataset. To add to the dataset, use append_data."""
        # Set of unified scales, used for efficient scale checking
        self._scales = set()
        # List of unified scales, equivalent to scales set but in order
        self._scales_list = []

        # List of data in dataset
        self.datasets = []
        # --- Following lists are in corresponding order to _datasets ---
        self._names = []
        self.regress_table = RegressValTable()
        self._row_labels = []
        # Unified 2D list of list of area values for each set
        self._areas = []
        # Unified 2D list of list of complexity values for each set
        self._complexities = []
        # Unified 2D list of list of regression set rows
        self._regress_sets = []

    def append_data(self, dataset, option: _DatasetOptionCallables = DatasetAppendOptions.IgnoreUnaligned) -> DatasetAppendOutput:
        """Add data to dataset.
        @param dataset - scale data to be inserted. Needs to be either a MulticaleDataset or list of MulticaleDatasets.
        @param option - Option configuration option for appending data."""
        if isinstance(dataset, list):
            return self._append_data_list(dataset, option)
        elif isinstance(dataset, MultiscaleData):
            return self._append_data_single(dataset, option)
        else:
            raise ValueError("Argument 'dataset' cannot be of type '" + type(dataset).__name__ + "'.")

    def _append_data_single(self, dataset: MultiscaleData, option: _DatasetOptionCallables) -> DatasetAppendOutput:
        """Add data to dataset.
        @param dataset - scale data to be inserted.
        @param option - Option configuration option for appending data."""
        # If dataset has not been initialized, define it
        if not self.datasets:
            self._scales = dataset.get_scales()
            self._scales_list = self.build_ordered_scales()
            self.datasets.append(dataset)
            self.regress_table.add_dataset(dataset)
            self._names.append(dataset.name)
            self._row_labels.append(dataset.row_labels)
            self._areas.append([dataset.get_relative_area(scale) for scale in sorted(self._scales)])
            self._complexities.append([dataset.get_complexity(scale) for scale in sorted(self._scales)])
            self._regress_sets = self.build_regress_sets()
            return DatasetAppendOutput()
        # Add to dataset
        else:
            return option(self, dataset)

    def _append_data_list(self, dataset_list: list, option: _DatasetOptionCallables) -> DatasetAppendOutput:
        """Add list of data to dataset.
        @param dataset_list - list of scale data to be inserted.
        @param option - Option configuration option for appending data."""
        ignore_list = []
        for dataset in dataset_list:
            output = self._append_data_single(dataset, option)
            # If ignore error occured, added to ignore list
            if not output and output == DatasetAppendOutput.SCALES_IGNORED_ERROR:
                ignore_list += output.value

        # If ignore error occured, output error
        if ignore_list:
            return DatasetAppendOutput(DatasetAppendOutput.SCALES_IGNORED_ERROR, ignore_list)
        # Return successful output
        else:
            return DatasetAppendOutput()

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

    def get_size(self):
        return len(self.datasets)

    def get_results_scale(self):
        return self._scales_list

    def get_legend_txt(self):
        return self._names

    def get_row_labels(self):
        return self._row_labels

    def get_relative_area(self):
        return self._areas

    def get_complexity(self):
        return self._complexities

    def get_regress_sets(self):
        return self._regress_sets

    def is_empty(self) -> bool:
        return self.get_size() == 0

    def clear(self):
        # Set of unified scales, used for efficient scale checking
        self._scales = set()
        # List of unified scales, equivalent to scales set but in order
        self._scales_list = []
        # List of data in dataset
        self.datasets = []
        # --- Following lists are in corresponding order to _datasets ---
        self._names = []
        self.regress_table.clear()
        self._row_labels = []
        # Unified 2D list of list of area values for each set
        self._areas = []
        # Unified 2D list of list of complexity values for each set
        self._complexities = []
        # Unified 2D list of list of regression set rows
        self._regress_sets = []
