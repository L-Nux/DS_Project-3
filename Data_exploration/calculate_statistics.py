import pandas as pd
import numpy as np
import os
import sys

def create_numberId_dict(city_list, n_cities):

    number_ids = [str(i) for i in range(1,n_cities+1)] #np.arange(1,n_cities+1)
    city_id_dict = dict(zip(city_list, number_ids))
    return city_id_dict

def add_numIDColumn(df, city_id_dict):

    print("Creating IDs for origin - destination pairs...")
    df["odPair_id"] = df["sourceName"].map(city_id_dict) + "-" + df["targetName"].map(city_id_dict)

    print("Number of different origin-destination pairs: ", len(df.odPair_id.unique()))

    return df

def statistics_perOD(df):

    df_stats_all = pd.DataFrame()
    unique_od_pairs = df.odPair_id.unique()

    print("Calculate statistics per origin-destination pair...")
    for val in unique_od_pairs:
        df_temp = df.loc[df['odPair_id'] == val]
        source_temp = df_temp.sourceName.values[0]
        target_temp = df_temp.targetName.values[0]
        print("Statistics calculated for id {} with source -{}- and target -{}-.".format(val, source_temp, target_temp))
        df_stats = df_temp.describe().loc[pd.Index(["min", "mean", "max"])]
        df_stats['odPair_id'] = val
        df_stats['sourceName'] = source_temp
        df_stats['targetName'] = target_temp

        df_stats_all = df_stats_all.append(df_stats)

    print("Calculating statistics finished ...")
    print()
    return df_stats_all

def main():

    sys.stdout = open("Statistics_2dimdata_project#3.txt", "a")
    #path to directory with reduced datasets
    os.chdir("/home/lisnux/Desktop/UniWien/WS2122/DS_Project/data/reduced_datasets/2dim/")

    #read merged 2dim dataset
    df = pd.read_csv("combined_csvs/combined_csv_2dim.csv", encoding = 'utf-8')

    #prepare list of all cities, alphabetically sorted:
    #from data inspection before we know that 29 different cities are in the dataset, all of them occur in the colum "targeName"
    cities_sorted = sorted(df.targetName.unique(), key=str.lower)
    n_cities = len(cities_sorted)
    print("Number of different cities: ", n_cities)

    #create a dictionary with city name as key and distinct integer as value
    city_id_dict = create_numberId_dict(cities_sorted, n_cities)
    print("Cities with corresponding IDs:", city_id_dict)

    #add column to dataset with ID of origin-destination pairs:
    df = add_numIDColumn(df, city_id_dict)
    print("Dataframe with new column: ", df.head())
    #save new df
    df.to_csv("combined_csvs/combined_csv_2dim_withIDs.csv", encoding = 'utf-8')

    #calculate statistics per od-pair (min, mean, max):

    df_stats = statistics_perOD(df)
    print("Sample of statistics dataframe: ", df_stats.head(10))

    #save new dataframe
    dest_path = "/home/lisnux/Desktop/UniWien/WS2122/DS_Project/data/reduced_datasets/2dim/combined_csvs/"
    df_stats.to_csv(dest_path+"statistics_2dim.csv", encoding='utf-8')

    print("---"*50)
    sys.stdout.close()

if __name__ == "__main__":
    main()