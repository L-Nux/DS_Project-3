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

#read merged 2dim dataset with od-pair column
df_id = pd.read_csv("combined_csvs/combined_csv_2dim_withIDs.csv", encoding = 'utf-8', index_col=0)
print(df_id.info())

### Inspection of data issues ###

#Issue 1: mismatch between totalNumberOfChanges and number of finalSolutionUsedLabels
# values in finalSolutionUsedLabels are strings and to differentiate between the different labels in a string the delimiter ", " is used.
# the delimiters between the labels are counted as changes.
def changes_labels_match(df):
    #for index, row in df.iterrows():
    #    count = row.finalSolutionUsedLabels.count(", ") +1
    df["changeLabelMatch"] = df.apply(lambda row: "match" if row.totalNumberOfChanges == (row.finalSolutionUsedLabels.count(", ")) else "noMatch", axis=1)

    return df

df_id = changes_labels_match(df_id)
print("Number of matches / no matches in totalNumberOfChanges finalSolutionUsedLabels: ", df_id.changeLabelMatch.value_counts(normalize=True))

#create dataframe with noMatches
df_id_noMatch = df_id.loc[df_id["changeLabelMatch"] == "noMatch"]
print("Source cities with no match in changes and used labels: ", df_id_noMatch["sourceName"].value_counts())
print("Target cities with no match in changes and used labels: ", df_id_noMatch["targetName"].value_counts())
print("OD-pairs with no match in changes and used labels: ", len(df_id_noMatch["odPair_id"].unique()))

count_morechanges = 0
diff_morechanges = []
count_morelabels = 0
diff_morelabels = []
for index, row in df_id_noMatch.iterrows():
    if row.totalNumberOfChanges > (row.finalSolutionUsedLabels.count(", ")):
        count_morechanges += 1
        diff_morechanges.append(row.totalNumberOfChanges - (row.finalSolutionUsedLabels.count(", ")))
    elif row.totalNumberOfChanges < (row.finalSolutionUsedLabels.count(", ")):
        count_morelabels += 1
        diff_morelabels.append((row.finalSolutionUsedLabels.count(", ")) - row.totalNumberOfChanges)

print("The number in totalNumberOfChanges is greater: ", count_morechanges)
print("The number in finalSolutionUsedLabels is greater: ", count_morelabels)

print("Range of differences between totalNumberOfChanges and finalSolutionUsedLabels, when former is larger: ", set(diff_morechanges))
print("Range of  differences between totalNumberOfChanges and finalSolutionUsedLabels, when latter is larger: ", set(diff_morelabels))






