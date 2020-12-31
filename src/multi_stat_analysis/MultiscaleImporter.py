import os
import csv
import numpy as np
import __main__
from MountainsImporter.Importer import import_surfaces
from MultiscaleData import MultiscaleData, MultiscaleDisjointDatasetException


def open_sfrax(file_paths) -> list:
    """Opens .csv files from Sfrax using a list of file paths.
    @param file_paths - given file paths
    @return list of generated datasets"""
    dataset = []
    # logs opening in the window
    __main__.error_txt.AppendText("Opening..." + '\n')

    # iterate over each file in the file path
    for file in file_paths:
        scales = []
        area_vals = []
        complex_vals = []
        row_labels = []

        # open the file as 'openfile'
        with open(file) as openfile:
            # create a reader for the .csv file and read each line to find required data
            reader = csv.reader(openfile, dialect='excel')
            for row in reader:
                # the first value in the row is always either text, empty, of a value for the scale
                # in this line the value is converted to a float() if it is text it will throw an error and skip
                # to the next line. However a number can be converted to a float and will not throw an error
                try:
                    # Appends the value of the scale rounded to 4 decimal places to the list of scales
                    scales.append(np.round_(float(row[0]), 4))
                    # the second value in the row is always relative area (or length) which is rounded and appended
                    # to tempList.
                    area_vals.append(np.round_(float(row[1]), 4))
                    # the third value in the row is always complexity which is rounded and appended to complexList
                    complex_vals.append(np.round_(float(row[2]), 4))
                # catch and log errors prints them to main window
                except (ValueError, IndexError) as e:
                    __main__.error_txt.AppendText("Open: " + str(e) + '\n')
        # Create dataset and add to return list
        try:
            dataset.append(MultiscaleData(os.path.basename(file), scales, area_vals, complex_vals))
        except MultiscaleDisjointDatasetException as e:
            __main__.error_txt.AppendText(e)
            continue

    __main__.error_txt.AppendText("Done." + '\n')
    return dataset


def open_results_file(file_paths) -> list:
    """Open .txt result files from mountainsmap
    @param file_paths - given file paths
    @return list of generated datasets"""
    dataset = []
    __main__.error_txt.AppendText("Opening..." + '\n')

    file_info_strs = []

    # iterate over each file to open each file and read the data
    for file in file_paths:
        scales = []
        area_vals = []
        complex_vals = []
        row_labels = []

        # Defines if the data values have been found, so float warnings can be ignored
        dataFound = False
        # open the file
        with open(file) as openfile:
            # Line number
            lineNum = 0
            # variable which contains a list of all of the lines in the text file
            lines = openfile.readlines()
            # iterate over each line in the text file
            for line in lines:
                lineNum += 1  # Increase line counter
                try:
                    # process text in file each line becomes a list of words and numbers
                    line = line.split("\t")
                    # the first value in the list is always either scale value or text
                    # if it is text a value error will be thrown here and is skipped
                    # otherwise check if the scale value is in the list of scales
                    scaleVal = np.sqrt(2 * float(line[0]))
                    scaleVal = np.round_(scaleVal, 4)
                    scales.append(scaleVal)

                    # second value in the line is always relative area add to temp list
                    area_vals.append(np.round_(float(line[1]), 4))
                    # third value in the line is always complexity add to temp list
                    complex_vals.append(np.round_(float(line[2]), 4))
                    # With the float conversions being successful, data has been found
                    dataFound = True
                # throw and log errors
                except ValueError as e:
                    if dataFound:
                        __main__.error_txt.AppendText(
                            "Open (" + openfile.name + ":" + str(lineNum) + "): " + str(e) + '\n')
                    elif not row_labels and len(line) >= 3:
                        row_labels = [line[1], line[2]]
        # Create dataset and add to return list
        dataset.append(MultiscaleData(os.path.basename(file), scales, area_vals, complex_vals, row_labels))

    __main__.error_txt.AppendText("Done." + '\n')
    return dataset


def open_sur(file_paths) -> list:
    """Using the given surface files, use the MountainsMap Importer tool to generate
    MountainsMap results files. These can then be imported with open_result_files.
    @param file_paths - given file paths
    @return list of generated datasets"""
    # Handle surface importing
    result_file_paths = import_surfaces(file_paths)
    # Exit if the value was not found
    if not result_file_paths:
        return
    # Open generated result text files
    return open_results_file(result_file_paths)
