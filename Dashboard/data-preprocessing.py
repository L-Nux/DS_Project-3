import pandas as pd

df = pd.read_csv("./Dashboard/withoutcolumns.csv")

def drop_column(df, column_name):
    for col in df.columns:
        if column_name in col:
            del df[col]


# dropping unnecessary columns
drop_column(df, "Unnamed: 0")
drop_column(df, "index")


# Transform minutes to hours, metres to kilometres, round the price value
def transform_values(d):
    d['totaltraveltimeinsec'] = d['totaltraveltimeinsec'].div(60).round(2)
    d['totalwaitingtime'] = d['totalwaitingtime'].div(60).round(2)
    d['totalwalkingdistance'] = (d['totalwalkingdistance'] * 1000).round(2).astype(int)
    d['totalprice'] = d['totalprice'].round(2)

    return d

df = transform_values(df)

df.drop_duplicates(inplace = True)
# dropping the instances with the same attributes for the different objectives
df = df.drop_duplicates(subset=['totaltraveltimeinsec', 'totalprice', 'totalnumberofchanges',
                                'totalwalkingdistance', 'totalwaitingtime', 'finiteautomaton',
                                'finalsolutionusedlabels', 'sourcename', 'targetname'])

df = df.rename(columns={'totaltraveltimeinsec': 'totaltraveltimeinhours', 'totalwaitingtime': 'totalwaitingtimeinhours',
                        'totalwalkingdistance': 'totalwalkingdistanceinm'})

describe = df.describe()

df.to_csv("data.csv", index=False)

