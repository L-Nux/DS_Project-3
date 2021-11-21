import numpy as np
import pandas as pd
# import tensorflow as tf

df = pd.read_csv("../data.csv")

dftest = pd.read_csv(r"I:\University of Vienna\3 term\Data Analysis Project\DS_Project-3\Dashboard\combined_csv_2dim.csv")

df.info()

def drop_column(column_name):
    for col in df.columns:
        if column_name in col:
            del df[col]

drop_column("Unnamed: 0")
drop_column("index")

print(df.tail())

X = df.iloc[:,3:-1].values
print(X)