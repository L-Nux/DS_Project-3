import pandas as pd

df = pd.read_csv(r"I:\University of Vienna\3 term\Data Analysis Project\DS_Project-3\Dashboard\withoutcolumns.csv")

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


df.to_csv("data.csv", index=False)

data = pd.read_csv("data.csv")
print(data.head())
