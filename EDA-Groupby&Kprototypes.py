#!/usr/bin/env python
# coding: utf-8

# In[5]:



#to include graphs next to the code
#useful libraries
import numpy as np #linear algebra
import math
import pandas as pd #data processing
from matplotlib import pyplot as plt  #plotting
import seaborn as sns #visualization


# In[6]:


import pandas as pd 
import os

working_directory = os.getcwd()
print (working_directory)


# In[7]:


path = working_directory + '/Desktop/combined_csv_2dim.csv'
df_bonus = pd.read_csv(path)
df_bonus.head()


# In[8]:


print(df_bonus.describe()) #statistics 


# In[12]:


df_bonus.columns


# In[13]:


#11 columns and 63+thousands of rows
df_bonus.shape


# In[14]:


data1 = df_bonus


# In[15]:


#no missing values
data1.isna().sum()


# In[16]:


#the longest walking distance from the full set of observations?
data1['totalWalkingDistance'].max()


# In[17]:


#we do not need more than 3 decimal places for our distance precision as well as not more than 2 decimal places for our price indicator
data2=data1.round({'totalWalkingDistance': 3, 'totalPrice': 2})


# In[18]:


data2.head()


# In[19]:


# how many entries are there per mode restrictions (Finite Automation)?
data1['finiteAutomaton'].value_counts()


# In[20]:


# number of unique price values-full dataset
data1['totalPrice'].nunique()


# In[21]:


# we have only 33 unique route combinations per data set
data1['finalSolutionUsedLabels'].nunique()


# In[22]:


#check all the SN available
data1.groupby(['sourceName']).groups.keys()


# In[23]:


# get the maximum for the applied price per starting position
#the most expensive offer is to go from Erfurt
data2.groupby('sourceName')['totalPrice'].max()


# In[24]:


#there are 5 records with the max price- always by railway- the lines are duplicating itself, data rows need to be cleaned
data2.loc[(data2['totalPrice'] == 362.74) & (data2['sourceName'].isin(['Erfurt']))]


# In[34]:


c = data2.groupby(['sourceName', 'targetName'])['totalPrice'].min()
# from Würzburg there are 22 cities that the traveler can visit with the unique itineraries, the cheapest one option is to Stuttgart
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(c)


# In[26]:


data2.loc[(data2['totalPrice'] == 7.00) & (data2['sourceName'].isin(['Würzburg']))]

#42 options are duplicationg each other-except totalWalkingDistance and finiteAutomation values, need to shrink the data set
#the proposed final mode is the same, FA won't be taken into consideration, only with respect to totalWalkingDistance


# In[27]:


# to go to Duisburg we have to pay 0,72 euros as minimum and this is the cheapest price
data2.groupby('targetName')['totalPrice'].min()


# In[28]:


data2.loc[(data2['totalPrice'] == 0.72 ) & (data2['targetName'].isin(['Duisburg']))]
#get rid of non-dominative solutions as the next step


# In[29]:


# Group the data frame pairwise Source&Target and extract the most friendly combination proposed by the algorithm with respect to price,time,tranfers
a = data2.groupby(
   ['sourceName', 'targetName']
).agg(
    {
         'totalTravelTimeInSec':'min',    # proposed the minimum time
         'totalPrice': "min",  # get the lowest price
         'totalNumberOfChanges': 'min'  # get a direct route
    }
)
a
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(a)


# In[30]:


data2.loc[(data2['totalPrice'] == 28.22 ) & (data2['targetName'].isin(['Bochum']))]


# In[31]:


#select ST towns from where it is possible to move directly simultanously with having 0 waiting time and 0 ditsance by foot
cr1 = data1.totalNumberOfChanges == 0
cr2 = data1.totalWaitingTime == 0
cr3 = data1.totalWalkingDistance == 0

data2[cr1 & cr2 & cr3]. loc [:, ['sourceName', 'targetName']]


# In[32]:


# Group the data frame by target&source to see all the ranges for the respective variables
data2.groupby(
    ['sourceName', 'targetName']
).agg(
    {
        # Find the min, max, and sum of the duration column
        'totalTravelTimeInSec': [min, max],
        # find the number of network type entries
        'totalPrice': [min, max],
        # minimum, first, and number of unique dates
        'totalWalkingDistance': [min, max],
        'totalWaitingTime': [min, max]
    }
)


# In[33]:


# get the number of unique proposed combinations in total per source-target
data2.groupby(['sourceName', 'targetName'])['finalSolutionUsedLabels'].nunique()


# In[35]:


#we do not need an objective column
data_new = data2.drop('objective', 1)


# In[36]:


data_new.head()


# In[37]:


data_new.drop_duplicates()
# we shortened our DF 3 times by getting rid of duplications


# In[46]:


from sklearn.cluster import KMeans 
from sklearn.preprocessing import StandardScaler


from sklearn.metrics import silhouette_samples, silhouette_score

get_ipython().run_line_magic('matplotlib', 'inline')


# In[63]:


#we do not need to specify source and target for clustering technique
data_new.head()


# In[64]:


#use kprototypes as a function of kmodes to handle both numerical and categorical variables
categorical_features_idx = [5, 6, 7] #specidy our categorical


# In[65]:


mark_array=data_new.values


# In[67]:


from kmodes.kprototypes import KPrototypes


# In[ ]:


#how many clusters? absed on a cost function
cost = []
for num_clusters in list(range(1,10)):
    kproto = KPrototypes(n_clusters=num_clusters, init='Cao')
    kproto.fit_predict(data_new, categorical=[5,6,7])
    cost.append(kproto.cost_)

plt.plot(cost)


# In[69]:


#try 8 clusters
kproto = KPrototypes(n_clusters=8, verbose=2, max_iter=20).fit(mark_array, categorical=categorical_features_idx)


# In[70]:


# get cluster centroids
print(kproto.cluster_centroids_)


# In[71]:


# prediction
clusters = kproto.predict(mark_array, categorical=categorical_features_idx)


# In[73]:


data_new['cluster'] = list(clusters) #obtain the clusters


# In[79]:


cluster_1= data_new[data_new['cluster']== 0]
cluster_1.head(50) #get the results


# In[80]:


#investigate the group
minvalue = cluster_1[['totalTravelTimeInSec', 'totalWaitingTime']].min()
print("minimum value in column 'totalTravelTimeInSec' & 'totalWaitingTime': ")
print(minvalue)

#Could describe a group as the slow trips with high waiting time


# In[ ]:


pip install plotly
from tqdm import tqdm
#an elbow plot with cost -takes super long to execute
costs = []
n_clusters = []
clusters_assigned = []

for i in tqdm(range(2, 25)):
    try:
        kproto = KPrototypes(n_clusters= i, init='Cao', verbose=2)
        clusters = kproto.fit_predict(data_new, categorical=[5,6,7])
        costs.append(kproto.cost_)
        n_clusters.append(i)
        clusters_assigned.append(clusters)
    except:
        print(f"Can't cluster with {i} clusters")
        
fig = go.Figure(data=go.Scatter(x=n_clusters, y=costs ))
fig.show()


# In[ ]:


#DBscan clustering

