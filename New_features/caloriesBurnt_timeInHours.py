import pandas as pd
pd.set_option('max_columns', None)

###NEW FEATURE: Calories burnt
#based on the estimated energy cost of activities (MET) provided by The Adult Compendium of Physical Activities

def convert_str_toList(string):
    #remove brackets from string
    li = string.str.strip("[|]")
    #split string into single preferences as list elements
    li = list(li.str.split(pat = ", "))
    return li

def get_calories(met_score, weight = 65):
    avg_male = round(met_score*70)
    avg_female = round(met_score*60)
    #weight is an predefined parameter
    individual = round(met_score * weight)

    return avg_male, avg_female, individual

def calculate_caloriesBurnt(df, weight = 65):
    time_inHours = df['totaltraveltimeinhours'].values[0] #.values[0] --> used to only get the value not the index information
    preferences = df['consideredpreferences']
    preferences_list = convert_str_toList(preferences)
    #check if walking is involved in the traveling activity
    if "walkingDistance" in preferences_list:
        walk_dist = df['totalwalkingdistance'].values[0]
        #convert walking distance to walking time (4.83km/h = avg. walking speed)
        walk_time = (walk_dist/4.83)
        #subtract the walking time from the passive sitting time
        travel_time_passive = time_inHours - walk_time
        #add scores of passive traveling and walking
        met_score = (travel_time_passive * 1.3) + (walk_time* 3.5)
    else:
        #only passive travelling (sitting activity)
        met_score = time_inHours * 1.3

    return get_calories(met_score, weight)

###only for testing purposes###
path_source = "/home/lisnux/Desktop/UniWien/WS2122/DS_Project/data/Marina_data/"
df_3dim = pd.read_csv(path_source+"2featuresout.csv", encoding = 'utf-8')

test1 = df_3dim.sample() #type: #class pandas.core.frame.DataFrame

print("test", test1)

#test with individual weight parameter
m, f, i = calculate_caloriesBurnt(test1, 100)
print("Calories burnt: ", m, f, i)
#test without individual weight parameter
m, f, i = calculate_caloriesBurnt(test1)
print("Calories burnt: ", m, f, i)