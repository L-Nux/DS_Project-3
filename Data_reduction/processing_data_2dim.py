###importing libraries###
import sys
import os
import zipfile
import glob
import pandas as pd
from timeit import default_timer as timer

def reducing_single_csvs():
    #path to original csv files
    os.chdir("/home/lisnux/Desktop/UniWien/WS2122/DS_Project/data/20211007_2dim_rohdaten/")

    #selected_cols = ['totalTravelTimeInSec', 'totalPrice', 'totalNumberOfChanges','totalWalkingDistance',
    #                 'totalWaitingTime', 'valueForK', 'finiteAutomaton', 'consideredPreferences',
    #                 'finalSolutionUsedLabels', 'sourceName', 'targetName']

    selected_cols = ['totalTravelTimeInSec', 'totalPrice', 'totalNumberOfChanges','totalWalkingDistance',
                     'totalWaitingTime', 'objective', 'finiteAutomaton', 'consideredPreferences',
                     'finalSolutionUsedLabels', 'sourceName', 'targetName']
    print("Selected columns: ", selected_cols)

    #specify folder paths for input and output
    folder_2dim = '/home/lisnux/Desktop/UniWien/WS2122/DS_Project/data/20211007_2dim_rohdaten/'
    destination_folder_2dim = '/home/lisnux/Desktop/UniWien/WS2122/DS_Project/data/reduced_datasets/2dim/'
    
    #counter variable to keep track of number of processed files
    counter = 0

    for filename in os.listdir(folder_2dim):
        temp = os.path.join(folder_2dim, filename)
        temp = pd.read_csv(temp, encoding='utf-8', delimiter=";")
        #get subset with selected columns
        temp_cols = temp[selected_cols]
        #drop duplicate rows
        temp_cols_dd = temp_cols.drop_duplicates()
        removed_rows = temp.shape[0] - temp_cols_dd.shape[0]
        print("For file {} {} rows have been removed.".format(filename, removed_rows))
        print()
        file_name = filename.split('.')
        #create new file name
        file_name = file_name[0] + '_trimmed.' + file_name[2]
        #save csv
        temp_cols_dd.to_csv(destination_folder_2dim + file_name, encoding='utf-8')
        counter += 1

    print("Number of processed files:", counter)
    print("Processed files saved in folder: ", destination_folder_2dim)

def merging_files():
    #path to single reduced csv files
    os.chdir('/home/lisnux/Desktop/UniWien/WS2122/DS_Project/data/reduced_datasets/2dim/')

    extension = 'csv'
    all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
    # combine all files in the list
    combined_csv = pd.concat([pd.read_csv(f, index_col=0, encoding='utf-8') for f in all_filenames])

    print("First part of combined csv:", combined_csv.head())
    print("Last part of combined csv: ", combined_csv.tail())
    # export to csv
    combined_csv.to_csv("combined_csvs/combined_csv_2dim.csv", index=False, encoding='utf-8')
    print("Merged file saved!")

def binning():
    print("Test")


def main():
    sys.stdout = open("dimensionalityReduction_project#3.txt", "a")
    start = timer()
    ###############################################################
    ###
    #STEP1: take subset from dataframe
    ###
    reducing_single_csvs()
    ###
    #STEP2: merge reduced datafiles into one csv
    ###
    merging_files()

    ###############################################################
    time_needed = timer() - start
    print("Time needed for data processing:", time_needed)
    print("---"*50)
    sys.stdout.close()

if __name__ == "__main__":
    main()
