import pandas as pd

routes = pd.read_csv('combined_csv_2dim.csv')

# Ordinal feature encoding
df = routes.copy()
target = 'finalsolutionusedlabels'
encode = ['objective', 'consideredPreferences', 'sourceName', 'targetName','finiteautomaton']

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