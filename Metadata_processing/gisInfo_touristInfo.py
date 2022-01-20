import pandas as pd
import os
from itertools import permutations

os.chdir("/home/lisnux/Desktop/UniWien/WS2122/DS_Project/data/additional_metadata/")

#load data
gis_data = pd.read_csv("gis_data.csv", encoding = 'utf-8', delimiter=";")
tourist_info = pd.read_csv("tourist_info.csv", encoding = 'utf-8', delimiter=";")

#prepare datasets

cities = gis_data.city.unique()
routes = list(permutations(cities, 2))

#create routes list

def route_list(ls):
    delimiter = '-'
    new_routes = []
    for value in ls:
        route = delimiter.join(value)
        new_routes.append(route)
    return new_routes

routes = route_list(routes)

#create new dataframe with route info
new_df = pd.DataFrame({'routes':routes})
new_df[['origin', 'destination']] = new_df["routes"].str.split("-", n = 1, expand = True)

#create city - gis dictionary
gis_data['city_gis'] = gis_data[['longitude', 'latitude']].values.tolist()

def city_gis_dict(df):
    city_ls = list(df.city.unique())
    gis_ls = list(df.city_gis)

    city_gis_dict = {}
    i=0
    if len(city_ls) == len(gis_ls):
        for i in range(len(city_ls)):
            city_gis_dict[city_ls[i]] = gis_ls[i]

    return city_gis_dict

city_gis_dict = city_gis_dict(gis_data)

#map city_gis dictionary data with routes
new_df['origin_gis'] = new_df['origin'].map(city_gis_dict)
new_df['destination_gis'] = new_df['destination'].map(city_gis_dict)
new_df['path'] = new_df[['origin_gis', 'destination_gis']].values.tolist()

print(new_df.head())

#create tourist info dictionary

def tourist_info_dict(df):
    tourist_city = list(df.city)
    tourist_page = list(df.city_info)

    tourist_dict = {}
    i = 0
    if len(tourist_city) == len(tourist_page):
        for i in range(len(tourist_city)):
            tourist_dict[tourist_city[i]] = tourist_page[i]

    return tourist_dict

tourist_info_dict = tourist_info_dict(tourist_info)

#map tourist info dict data with routes
new_df['origin_info'] = new_df['origin'].map(tourist_info_dict)
new_df['destination_info'] = new_df['destination'].map(tourist_info_dict)

#save new dataset
new_df.to_csv("gisInfo_touristInfo_final.csv", encoding = 'utf-8')





