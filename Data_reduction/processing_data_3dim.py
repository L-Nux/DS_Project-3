###importing libraries###
import sys
import os
import zipfile
import bz2
import pandas as pd
import glob
from timeit import default_timer as timer

def reducing_single_csvs():
    """This function only works with an input zip file compressed with method bzip2"""

    #path to zip folder
    zip_folder_3dim = '/media/lisnux/EXTERNE FESTPLATTE LISA NUX/20211007_3dim_rohdaten_rezipped.zip'
    print("Files originate in folder: ", zip_folder_3dim)
    #path to reduced single csvs
    destination_folder_3dim = '/home/lisnux/Desktop/UniWien/WS2122/DS_Project/data/reduced_datasets/3dim/'

    selected_cols = ['totalTravelTimeInSec', 'totalPrice', 'totalNumberOfChanges', 'totalWalkingDistance',
                     'totalWaitingTime', 'objective', 'finiteAutomaton', 'consideredPreferences',
                     'finalSolutionUsedLabels', 'sourceName', 'targetName']
    print("Selected columns: ", selected_cols)

    counter = 0

    # access archive:
    with zipfile.ZipFile(zip_folder_3dim, 'r', zipfile.ZIP_BZIP2) as z:
    #with zipfile.PyZipFile(zip_folder_3dim, 'r', zipfile.ZIP_BZIP2)) as z:
        print(z.infolist())
        for filename in z.namelist():
            print(filename)
            if not os.path.isdir(filename):
                #read the file
                with z.open(filename, 'r') as f:
                    temp = pd.read_csv(f, encoding="utf-8", delimiter=";")
                    temp_cols = temp[selected_cols]
                    temp_cols_dd = temp_cols.drop_duplicates()
                    removed_rows = temp.shape[0] - temp_cols_dd.shape[0]
                    print("For file {} {} rows have been removed!".format(filename, removed_rows))
                    print()
                    file_name = filename.split('.')
                    file_name = file_name[0] + '_reduced.' + file_name[2]
                    temp_cols_dd.to_csv(destination_folder_3dim + file_name, encoding='utf-8')
                    counter += 1

    print("Number of processed files:", counter)

def merging_files():
    #path to single reduced csv files
    os.chdir('/home/lisnux/Desktop/UniWien/WS2122/DS_Project/data/reduced_datasets/3dim/')

    extension = 'csv'
    all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
    # combine all files in the list
    combined_csv = pd.concat([pd.read_csv(f, index_col=0, encoding='utf-8') for f in all_filenames])

    print(combined_csv.head())
    print(combined_csv.tail())
    # export to csv
    combined_csv.to_csv("combined_csvs/combined_csv_3dim.csv", index=False, encoding='utf-8')
    print("Merged file saved!")

def main():
    sys.stdout = open("dimensionalityReduction_project#3_3dim.txt", "a")
    start = timer()

    ###############################################################
    ###
    # STEP1: take subset from dataframe
    ###
    reducing_single_csvs()
    ###
    # STEP2: merge reduced datafiles into one csv
    ###
    merging_files()

    ###############################################################

    time_needed = timer() - start
    print("Time needed for data processing:", time_needed)
    print("---"*50)
    sys.stdout.close()

    ###


if __name__ == '__main__':
    main()