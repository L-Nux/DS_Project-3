import pandas as pd

routes = pd.read_csv('combined_csv_2dim.csv')

# Ordinal feature encoding
# https://www.kaggle.com/pratik1120/penguin-dataset-eda-classification-and-clustering
df = routes.copy()
target = 'finiteAutomaton'
encode = ['objective', 'consideredPreferences', 'sourceName', 'targetName','finalSolutionUsedLabels']

insight = df.describe()

for col in encode:
    dummy = pd.get_dummies(df[col], prefix=col)
    df = pd.concat([df,dummy], axis=1)
    del df[col]

target_mapper = {'all':0, 'ptOnly':1, 'noFlights':2}
def target_encode(val):
    return target_mapper[val]

df['finiteAutomaton'] = df['finiteAutomaton'].apply(target_encode)

# Separating X and y
X = df.drop('finiteAutomaton', axis=1)
Y = df['finiteAutomaton']

# Build random forest model
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier()
clf.fit(X, Y)

# Saving the model
import pickle
pickle.dump(clf, open('routes_clf.pkl', 'wb'))