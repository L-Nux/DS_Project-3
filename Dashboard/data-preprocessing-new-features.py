import pandas as pd

df = pd.read_csv("final.csv")

def drop_column(df, column_name):
    for col in df.columns:
        if column_name in col:
            del df[col]


# dropping unnecessary columns



# Transform minutes to hours, metres to kilometres, round the price value
def transform_values(d):
    d['totaltraveltimeinsec'] = d['totaltraveltimeinsec'].div(10).round(2)
    d['totalwaitingtime'] = d['totalwaitingtime'].div(10).round(2)
    d['totalwalkingdistance'] = (d['totalwalkingdistance'] * 1000).round(2).astype(int)
    d['totalprice'] = d['totalprice'].round(2)

    return d


df.to_csv("data.csv", index=False)

