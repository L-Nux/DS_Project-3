import pandas as pd
import numpy as np
import os

#path to directory with reduced datasets
os.chdir("/home/lisnux/Desktop/UniWien/WS2122/DS_Project/data/reduced_datasets/2dim/")

#read merged 2dim dataset
df = pd.read_csv("combined_csvs/combined_csv_2dim.csv", encoding = 'utf-8')

print("Columns: ", df.columns)
print("Data type of columns: ", df.dtypes)

#numerical columns:
print("Statistical summary of columns with numerical values: ", df.describe())

#non-numerical columns:
non_num_columns = ['objective', 'consideredPreferences', 'finiteAutomaton', 'finalSolutionUsedLabels', 'sourceName', 'targetName']
print("Inspection of columns with non-numerical values: ")
for col in df[non_num_columns]:
    print("Column: ", col)
    print("{} unique values: {}".format(len(df[col].unique()), df[col].unique()))

print("Cities that are targets but not sources:")
for city in df.targetName.unique():
    if city not in df.sourceName.unique():
        print(city)