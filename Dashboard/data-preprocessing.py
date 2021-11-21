import pandas as pd

df = pd.read_csv("withoutcolumns.csv")

def drop_column(df, column_name):
    for col in df.columns:
        if column_name in col:
            del df[col]


# dropping unnecessary columns
drop_column(df, "Unnamed: 0")
drop_column(df, "index")
# dropping the instances with the same attributes for the different objectives
df = df.drop_duplicates(subset=['totaltraveltimeinsec', 'totalprice', 'totalnumberofchanges',
                                'totalwalkingdistance', 'totalwaitingtime', 'finiteautomaton',
                                'finalsolutionusedlabels', 'sourcename', 'targetname'])


# Transform minutes to hours
def transform_values(d):
    d['totaltraveltimeinsec'] = d['totaltraveltimeinsec'].div(60).round(1)
    d['totalwaitingtime'] = d['totalwaitingtime'].div(60).round(1)
    d['totalwalkingdistance'] = (d['totalwalkingdistance'] * 1000).round(1).astype(int)
    d['totalprice'] = d['totalprice'].round(1)

    return d


df = transform_values(df)

describe = df.describe()

df.to_csv("data.csv", index=False)

data = pd.read_csv("data.csv")
print(data.head())
