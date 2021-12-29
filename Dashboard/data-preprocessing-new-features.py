import pandas as pd

df = pd.read_csv(r"I:\University of Vienna\3 term\Data Analysis Project\DS_Project-3\Dashboard\final.csv")

df.info()


def drop_column(df, column_name):
    for col in df.columns:
        if column_name in col:
            del df[col]


# dropping unnecessary columns

drop_column(df, "Unnamed: 0")
drop_column(df, "objective")
drop_column(df, "consideredpreferences")
drop_column(df, "travelfrom")
drop_column(df, "travelto")
drop_column(df, "numtravelfrom")
drop_column(df, "numtravelto")
drop_column(df, "totalnumberofchanges")
drop_column(df, "temperaturefrom")
drop_column(df, "temperatureto")
drop_column(df, "humidityfrom")
drop_column(df, "humidityto")
drop_column(df, "pressurefrom")
drop_column(df, "pressureto")
drop_column(df, "finiteautomaton")

df.drop_duplicates(inplace=True)
df.info()

df['totalwalkingdistance'] = (df['totalwalkingdistance'] * 1000).round(2).astype(int)


df.rename({'totalwalkingdistance': 'totalwalkingdistanceinm',
           'totalwaitingtime': 'totalwaitingtimeinhours'
              ,}, axis=1, inplace=True)


df.to_csv("data.csv", index=False)
