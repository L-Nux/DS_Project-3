# %%
import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import parallel_coordinates
import plotly.express as px

'''
Investigation of the "objective" column

How does it relate to other columns? 
Can we drop it? 
How does it influence the dataset? 
Should dominated rows be dropped?

'''
# %%
# importing the dataset
df = pd.read_csv(Path().joinpath('Data_exploration', 'withoutcolumns.csv'), encoding='utf-8')
df.head()


# %%
# dropping unnecessary columns

def drop_column(column_name):
    for col in df.columns:
        if column_name in col:
            del df[col]


# %%
df.info()
statistics = df.describe()
# %%
df['objective'].unique()
# %%
# grouping by OD and objective columns calculating the size of this grouping
group = df.groupby(['sourcename', 'targetname', 'objective'])
group_count = group.size()
# %%
# counting unique values per group of different objectives per specific pair of OD
group = group.agg({'totalprice': 'nunique', 'totaltraveltimeinsec': 'nunique', 'totalnumberofchanges': 'nunique',
                   'totalwalkingdistance': 'nunique', 'totalwaitingtime': 'nunique'})
group = group.reset_index()
# %%
group_price = group[group['objective'] == 'price']
# %%
# dropping unnecessary columns for plotting
refined_df = df.drop(df.loc[:, 'finiteautomaton':'targetname'].columns, axis=1)

# %%
# plotting the graph with the respect to objective for all ODs
parallel_coordinates(refined_df, 'objective', colormap=plt.get_cmap("Set1"))
plt.show()

# %%
# filtering dataset to have one OD
df_essen = df[(df['sourcename'] == 'Essen') & (df['targetname'] == 'Gelsenkirchen')]
# %%
# dropping unnecessary columns for plotting
refined_df_essen = df_essen.drop(df_essen.loc[:, 'finiteautomaton':'targetname'].columns, axis=1)

# %%
# mapping values for better representation to the [0,1] range
numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
for c in [c for c in refined_df_essen.columns if refined_df_essen[c].dtype in numerics]:
    refined_df_essen[c] = (refined_df_essen[c] - np.min(refined_df_essen[c])) / (
            np.max(refined_df_essen[c]) - np.min(refined_df_essen[c]) + 0.000000001)
# %%
# plotting the graph with the specific OD and normalized values
parallel_coordinates(refined_df_essen, 'objective', colormap=plt.get_cmap("Set2"), sort_labels=True)
plt.show()
# %%
# encode objectives for better representation
obj_nums = {"objective": {"price": 1, "travelTime": 2, "numberofChanges": 3, "walkingDistance": 4,
                          "waitingTime": 5}}
obj_df = refined_df_essen.replace(obj_nums)
obj_df.head()
# %%
# plotting the graph with the specific OD and normalized values
fig = px.parallel_coordinates(
    obj_df,
    color='objective',
    color_continuous_scale=px.colors.diverging.Tealrose,
    color_continuous_midpoint=3)
fig.show()
fig.write_html(Path().joinpath('Data_exploration', 'parallel-coordinate-plot-plotly.html'))
# %%
# filtering dataset to have only price objectives
refined_df_essen_price = refined_df_essen[refined_df_essen['objective'] == 'price']
refined_df_essen_price.drop_duplicates(inplace=True)
# %%
# plotting the graph with the specific OD and normalized values and only one objective
parallel_coordinates(refined_df_essen_price, 'objective', colormap=plt.get_cmap("Set3"))
plt.show()

# %%
# How dropping of the whole objective influence the dataset?
index = df.index
number_of_rows = len(index)
# %%
del df['objective']
# %%
df.drop_duplicates(inplace=True)
# %%
df.drop_duplicates(inplace=True)
index = df.index
number_of_rows = len(index)

# Number of rows drops from 85153 to 30486
# %%
# dropping the instances with the same attributes for the different objectives
dropped = df.drop_duplicates(subset=['totaltraveltimeinsec', 'totalprice', 'totalnumberofchanges',
                                     'totalwalkingdistance', 'totalwaitingtime', 'finiteautomaton',
                                     'finalsolutionusedlabels', 'sourcename', 'targetname'])

# Number of rows drops from 85153 to 24009
