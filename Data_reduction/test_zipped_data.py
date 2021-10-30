###importing libraries###
import sys
import os
import zipfile
import pandas as pd
from timeit import default_timer as timer


def main():
    sys.stdout = open("dimensionalityReduction_project#3.txt", "a")

    start = timer()

    os.chdir("C:\\Users\\z003zewu\\PycharmProjects\\project#3\\")

    selected_cols = ['totalTravelTimeInSec', 'totalPrice', 'totalNumberOfChanges', 'totalWalkingDistance',
                     'totalWaitingTime', 'valueForK', 'finiteAutomaton', 'consideredPreferences',
                     'finalSolutionUsedLabels', 'sourceName', 'targetName']
    print("Selected columns: ", selected_cols)

    #destination_folder_2dim = 'C:\\Users\\z003zewu\\PycharmProjects\\project#3\\reduced_datasets\\2dim\\'
    destination_folder_3dim = 'C:\\Users\\z003zewu\\PycharmProjects\\project#3\\reduced_datasets\\3dim\\'

    ### zipped folder option:

    #zip_folder_2dim = 'C:\\Users\\z003zewu\\PycharmProjects\\project#3\\20211007_2dim_rohdaten.zip'
    zip_folder_3dim = 'C:\\Users\\z003zewu\\PycharmProjects\\project#3\\20211007_3dim_rohdaten.zip'
    print("Files originate in folder: ", zip_folder_3dim)

    #test 1
    counter = 0
    # access archive:
    with zipfile.ZipFile(zip_folder_3dim) as z:
        for filename in z.namelist():
            if not os.path.isdir(filename):
                # read the file
                with z.open(filename) as f:
                    temp = pd.read_csv(f, encoding="utf-8", delimiter=";")
                    temp_cols = temp[selected_cols]
                    temp_cols_dd = temp_cols.drop_duplicates()
                    removed_rows = temp.shape[0] - temp_cols_dd.shape[0]
                    print("For file {} {} rows have been removed}!".format(filename, removed_rows))
                    print()
                    file_name = f.split('.')
                    file_name = file_name[0] + '_reduced.' + file_name[2]
                    temp_cols_dd.to_csv(destination_folder_3dim+file_name, encoding='utf-8')
                    counter+=1

    #test 2
    """
    zf = zipfile.ZipFile(zip_folder_3dim)

    for filename in zf.namelist():
        temp = pd.read_csv(zf.open(filename))
        temp_cols = temp[selected_cols]
        temp_cols_dd = temp_cols.drop_duplicates()
        removed_rows = temp.shape[0] - temp_cols_dd.shape[0]
        print("For file {} {} rows have been removed}!".format(filename, removed_rows))
        print()
        file_name = f.split('.')
        file_name = file_name[0] + '_reduced.' + file_name[2]
        temp_cols_dd.to_csv(destination_folder_3dim + file_name, encoding='utf-8')
        counter += 1
        
    """

    """
    ###unzipped folder version:
    folder_2dim = 'C:\\Users\\z003zewu\\PycharmProjects\\project#3\\20211007_2dim_rohdaten'

    counter = 0

    for filename in os.listdir(folder_2dim):
        temp = os.path.join(folder_2dim, filename)
        temp = pd.read_csv(temp, encoding='utf-8', delimiter=";")
        temp_cols = temp[selected_cols]
        temp_cols_dd = temp_cols.drop_duplicates()
        removed_rows = temp.shape[0] - temp_cols_dd.shape[0]
        print("For file {} {} rows have been removed.".format(filename, removed_rows))
        print()
        file_name = filename.split('.')
        file_name = file_name[0] + '_trimmed.' + file_name[2]
        temp_cols_dd.to_csv(destination_folder_2dim + file_name, encoding='utf-8')
        counter += 1

    print("Processed files saved in folder: ", destination_folder_2dim)
    #####

    time_needed = timer() - start
    print("Time needed for data processing:", time_needed)
    print("Number of processed files:", counter)
    print("---" * 50)
    sys.stdout.close()
    """


if __name__ == "__main__":
    main()