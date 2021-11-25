import pandas as pd
import os

#data for city size downloaded from:
# https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/Administrativ/05-staedte.html
# status: 31.Dec.2020

path_source = "/home/lisnux/Desktop/UniWien/WS2122/DS_Project/data/"
city_size_orig = pd.read_excel(path_source+"city_size.xlsx")
print(city_size_orig.head(10))
print("Dimensions of original dataset: ", city_size_orig.shape)

#city_size = city_size_orig.drop(index=[0, 1, 4, 5])

#rename relevant columns
city_size = city_size_orig.rename(columns = {'Unnamed: 6':'city', 'Unnamed: 7': 'postcode', 'Unnamed: 8': 'area_km2',
                           'Unnamed: 9' : 'population_total', 'Unnamed: 10' : 'population_male',
                           'Unnamed: 11' : 'population_female', 'Unnamed: 12' : 'population_density_per_km2'})

#get rid of irrelevant attributes:
city_size = city_size.iloc[: , 6:]

#get rid of metadata rows
city_size = city_size.iloc[6: , :]

#drop null values
city_size = city_size.dropna()

#clean city names (get substring)
#e.g. Berlin, Stadt --> Berlin
city_size['city'] = city_size['city'].str.split(',', 1).str[0].str.strip()
print(city_size.city.unique())

#define list of cities considered in Thomas' algorithm
relevant_cities = ['Gelsenkirchen', 'Oberhausen', 'Bonn', 'Duisburg', 'München', 'Bochum',
 'Solingen', 'Nürnberg', 'Karlsruhe', 'Wuppertal', 'Hagen', 'Dortmund',
 'Düsseldorf' ,'Essen', 'Erlangen' ,'Osnabrück' ,'Leipzig' ,'Würzburg',
 'Mannheim' ,'Ulm' ,'Bamberg' ,'Darmstadt', 'Köln', 'Stuttgart' ,'Heidelberg',
 'Erfurt', 'Berlin' ,'Aachen' ,'Hamburg']

#get subset of dataset with relevant cities
city_size = city_size[city_size.city.isin(relevant_cities)]

if city_size.shape[0] == len(relevant_cities):
    print("Yay! Found all relevant cities!")
else:
    print("Attention, there is a mismatch in the number of cities!")

print("Dimensions of cleaned dataset with relevant info:", city_size.shape)

#assign category to city size (3 classes)
#reference: http://www.metropolenforschung.de/download/Mieg_Metropolen_2012.pdf
# small city < 100 000
# big city >= 100 000
# metropolis  >= 1mio

def size_category(row):
    if row['population_total'] < 100000:
        return 'small_city'
    if 100000 <= row['population_total'] < 1000000:
        return 'big_city'
    if row['population_total'] >= 1000000:
        return 'metropolis'

city_size['size_category'] = city_size.apply(lambda row: size_category(row), axis=1)
print(city_size.head())

#save file:
path_dest = "/home/lisnux/Desktop/UniWien/WS2122/DS_Project/data/additional_metadata/"
city_size.to_csv(path_dest+"meta_city_size.csv", encoding = 'utf-8')






